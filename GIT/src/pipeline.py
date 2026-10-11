"""Ingestao transacional e idempotente do CSV original do Kaggle."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sqlalchemy import text
from src.database import ROOT, get_engine, initialize

REQUIRED = ['id', 'room_id/id', 'noted_date', 'temp', 'out/in']
COLUMNS = ['reading_id', 'device_id', 'noted_at', 'temperature', 'location']

def normalize(raw):
    missing = set(REQUIRED) - set(raw.columns)
    if missing:
        raise ValueError('Colunas ausentes: ' + ', '.join(sorted(missing)))
    data = pd.DataFrame({
        'reading_id': raw['id'].astype('string').str.strip(),
        'device_id': raw['room_id/id'].astype('string').str.strip(),
        'noted_at': pd.to_datetime(raw['noted_date'], format='%d-%m-%Y %H:%M', errors='coerce'),
        'temperature': pd.to_numeric(raw['temp'], errors='coerce'),
        'location': raw['out/in'].astype('string').str.strip(),
    })
    reasons = pd.Series('', index=raw.index, dtype='string')
    checks = [
        (data.reading_id.isna() | data.reading_id.eq(''), 'ID ausente'),
        (data.device_id.isna() | data.device_id.eq(''), 'local ausente'),
        (data.noted_at.isna(), 'data invalida'),
        (~np.isfinite(data.temperature.astype(float)), 'temperatura invalida'),
        (~data.location.isin(['In', 'Out']), 'ambiente invalido'),
    ]
    for invalid, reason in checks:
        reasons.loc[invalid.fillna(True)] += reason + '; '
    rejected = raw.loc[reasons.ne('')].copy()
    rejected['motivo'] = reasons.loc[reasons.ne('')]
    rejected.insert(0, 'linha_csv', rejected.index + 2)
    valid = data.loc[reasons.eq('')].copy()
    # Repetir valor/horario com IDs diferentes e permitido na base original.
    unique = valid.drop_duplicates(COLUMNS)
    if unique.reading_id.duplicated().any():
        raise ValueError('Mesmo ID associado a leituras diferentes no CSV. Importacao cancelada.')
    duplicates = len(valid) - len(unique)
    return unique, rejected, duplicates

def import_csv(path, engine=None, output=None):
    path = Path(path)
    raw = pd.read_csv(path, dtype='string')
    clean, rejected, duplicates = normalize(raw)
    if clean.empty:
        raise ValueError('Nenhuma leitura valida. O banco nao foi alterado.')
    engine = engine if engine is not None else get_engine()
    report = {'source_name': path.name,
              'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'input_rows': len(raw), 'rejected_rows': len(rejected),
              'duplicate_ids': duplicates}
    with engine.begin() as conn:
        initialize(conn)
        # Serializa importadores deste projeto; evita corrida entre checagem e insercao.
        conn.execute(text('SELECT pg_advisory_xact_lock(74201923)'))
        conn.execute(text('CREATE TEMP TABLE staging_readings (LIKE temperature_readings INCLUDING DEFAULTS) ON COMMIT DROP'))
        clean.to_sql('staging_readings', conn, if_exists='append', index=False,
                     method='multi', chunksize=1000)
        conflicts = conn.scalar(text('''SELECT count(*) FROM staging_readings s
            JOIN temperature_readings t USING (reading_id)
            WHERE (s.device_id,s.noted_at,s.temperature,s.location)
            IS DISTINCT FROM (t.device_id,t.noted_at,t.temperature,t.location)'''))
        if conflicts:
            raise ValueError(f'{conflicts} IDs conflitam com o banco. Transacao cancelada.')
        inserted = conn.execute(text('''INSERT INTO temperature_readings
            SELECT * FROM staging_readings ON CONFLICT (reading_id) DO NOTHING''')).rowcount
        report.update(inserted_rows=inserted, existing_rows=len(clean) - inserted)
        conn.execute(text('''INSERT INTO import_runs
            (source_name,source_sha256,input_rows,rejected_rows,duplicate_ids,inserted_rows,existing_rows)
            VALUES (:source_name,:source_sha256,:input_rows,:rejected_rows,:duplicate_ids,:inserted_rows,:existing_rows)'''), report)
        report['database_rows'] = conn.scalar(text('SELECT count(*) FROM temperature_readings'))
    output = Path(output) if output else ROOT / 'docs' / 'resultados'
    output.mkdir(parents=True, exist_ok=True)
    rejected.to_csv(output / 'linhas_rejeitadas.csv', index=False)
    (output / 'ultima_importacao.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=ROOT / 'data' / 'IOT-temp.csv')
    args = parser.parse_args()
    try:
        print(json.dumps(import_csv(args.csv), indent=2))
    except (ValueError, FileNotFoundError) as exc:
        parser.exit(1, f'Erro: {exc}\n')

if __name__ == '__main__':
    main()
