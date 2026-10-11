"""Exporta as views e confere os agregados SQL com o CSV de origem."""
import json
from pathlib import Path
import pandas as pd
from sqlalchemy import text
from src.database import get_engine, ROOT
from src.analytics import load_views
from src.pipeline import normalize

engine = get_engine()
frames = load_views(engine)
clean, rejected, duplicates = normalize(pd.read_csv(ROOT / 'data/IOT-temp.csv', dtype='string'))
out = ROOT / 'docs/resultados'
out.mkdir(parents=True, exist_ok=True)
for name, frame in frames.items():
    frame.to_csv(out / (name + '.csv'), index=False)

avg = frames['avg_temp_por_dispositivo'].set_index(['device_id', 'location']).sort_index()
expected = clean.groupby(['device_id', 'location']).temperature.agg(['count', 'mean', 'min', 'max'])
assert avg.leituras.tolist() == expected['count'].tolist()
assert all(abs(a-b) < 1e-9 for a, b in zip(avg.avg_temp, expected['mean']))
assert avg.temp_min.tolist() == expected['min'].tolist()
assert avg.temp_max.tolist() == expected['max'].tolist()
actual_hour = frames['leituras_por_hora'].set_index(['hora', 'location']).contagem.sort_index()
expected_hour = clean.groupby([clean.noted_at.dt.hour.rename('hora'), 'location']).size().sort_index()
assert actual_hour.to_dict() == expected_hour.to_dict()
actual_day = frames['temp_max_min_por_dia'].copy()
actual_day['data'] = pd.to_datetime(actual_day['data'])
actual_day = actual_day.set_index(['data', 'location']).sort_index()
expected_day = clean.groupby([clean.noted_at.dt.normalize().rename('data'), 'location']).temperature.agg(['count','mean','min','max'])
assert actual_day.leituras.to_dict() == expected_day['count'].to_dict()
assert actual_day.temp_min.to_dict() == expected_day['min'].to_dict()
assert actual_day.temp_max.to_dict() == expected_day['max'].to_dict()
assert all(abs(a-b)<1e-9 for a,b in zip(actual_day.temp_media,expected_day['mean']))
with engine.connect() as conn:
    total = conn.scalar(text('SELECT count(*) FROM temperature_readings'))
    version = conn.scalar(text('SHOW server_version'))
summary = {
    'rows': total, 'input_rows': len(clean) + len(rejected) + duplicates,
    'duplicates': duplicates, 'rejected': len(rejected),
    'start': str(clean.noted_at.min()), 'end': str(clean.noted_at.max()),
    'mean': float(clean.temperature.mean()), 'min': float(clean.temperature.min()),
    'max': float(clean.temperature.max()), 'days': int(clean.noted_at.dt.date.nunique()),
    'postgres_version': version,
    'groups': avg.reset_index().to_dict(orient='records'),
    'hour_peak': frames['leituras_por_hora'].groupby('hora').contagem.sum().idxmax().item(),
    'sql_csv_reconciliation': 'APROVADA: contagens, medias, minimas e maximas das tres views conferidas com pandas',
}
(out / 'resumo.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(summary, indent=2, ensure_ascii=True))
