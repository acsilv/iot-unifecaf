"""Validacao e integracao em schema temporario (sem tocar nas leituras reais)."""
import os
import uuid
import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from src.database import get_engine
from src.pipeline import normalize, import_csv
from src.analytics import load_views

def sample():
    return pd.DataFrame([
        ['a', 'Sala 1', '28-07-2018 07:06', '20', 'In'],
        ['b', 'Sala 1', '28-07-2018 08:00', '30', 'Out'],
        ['c', 'Sala 1', '29-07-2018 07:06', '24', 'In'],
    ], columns=['id', 'room_id/id', 'noted_date', 'temp', 'out/in'])

def test_rejects_invalid_values_and_parses_day_first():
    raw = sample()
    raw.loc[1, 'temp'] = 'texto'
    raw.loc[2, 'noted_date'] = '31-02-2018 07:00'
    valid, rejected, duplicates = normalize(raw)
    assert len(valid) == 1 and len(rejected) == 2 and duplicates == 0
    assert valid.iloc[0].noted_at == pd.Timestamp('2018-07-28 07:06')
    assert rejected.linha_csv.tolist() == [3, 4]

@pytest.mark.parametrize('value', ['inf', '-inf', '', None, 'NaN'])
def test_nonfinite_temperature_rejected(value):
    raw = sample()
    raw.loc[0, 'temp'] = value
    valid, rejected, _ = normalize(raw)
    assert len(valid) == 2 and len(rejected) == 1

def test_duplicate_id_removed_but_distinct_ids_preserved():
    raw = pd.concat([sample(), sample().iloc[:1]], ignore_index=True)
    valid, _, duplicates = normalize(raw)
    assert len(valid) == 3 and duplicates == 1
    raw.loc[3, 'id'] = 'd'
    assert len(normalize(raw)[0]) == 4

def test_conflicting_id_fails():
    raw = pd.concat([sample(), sample().iloc[:1]], ignore_index=True)
    raw.loc[3, 'temp'] = '99'
    with pytest.raises(ValueError, match='Mesmo ID'):
        normalize(raw)

def test_missing_column_fails():
    with pytest.raises(ValueError, match='Colunas ausentes'):
        normalize(sample().drop(columns='id'))

@pytest.fixture
def isolated_db():
    if os.getenv('RUN_POSTGRES_TESTS') != '1':
        pytest.skip('Defina RUN_POSTGRES_TESTS=1 com PostgreSQL iniciado.')
    admin = get_engine()
    schema = 'test_' + uuid.uuid4().hex
    with admin.begin() as conn:
        conn.execute(text('CREATE SCHEMA ' + schema))
    engine = create_engine(admin.url, connect_args={'options': '-csearch_path=' + schema})
    try:
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as conn:
            conn.execute(text('DROP SCHEMA ' + schema + ' CASCADE'))
        admin.dispose()

def test_postgres_import_views_idempotency_and_rollback(isolated_db, tmp_path):
    csv = tmp_path / 'test.csv'
    sample().to_csv(csv, index=False)
    first = import_csv(csv, isolated_db, tmp_path / 'report')
    second = import_csv(csv, isolated_db, tmp_path / 'report')
    assert first['inserted_rows'] == 3
    assert second['inserted_rows'] == 0 and second['existing_rows'] == 3
    views = load_views(isolated_db)
    inside = views['avg_temp_por_dispositivo'].query("location == 'In'").iloc[0]
    assert inside.avg_temp == 22 and inside.leituras == 2
    assert views['leituras_por_hora'].contagem.sum() == 3
    assert views['temp_max_min_por_dia'].leituras.sum() == 3
    changed = sample()
    changed.loc[0, 'temp'] = '99'
    changed.loc[2, 'id'] = 'new'
    changed.to_csv(csv, index=False)
    with pytest.raises(ValueError, match='conflitam'):
        import_csv(csv, isolated_db, tmp_path / 'report')
    with isolated_db.connect() as conn:
        assert conn.scalar(text('SELECT count(*) FROM temperature_readings')) == 3
        assert conn.scalar(text('SELECT count(*) FROM import_runs')) == 2

def test_empty_valid_data_does_not_change_database(isolated_db, tmp_path):
    raw = sample()
    raw['temp'] = 'invalido'
    csv = tmp_path / 'invalid.csv'
    raw.to_csv(csv, index=False)
    with pytest.raises(ValueError, match='Nenhuma leitura'):
        import_csv(csv, isolated_db, tmp_path / 'report')
