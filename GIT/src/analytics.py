"""Consultas fixas as views e metricas do banco PostgreSQL."""
import pandas as pd
from sqlalchemy import text

VIEWS = ['avg_temp_por_dispositivo', 'leituras_por_hora', 'temp_max_min_por_dia']

def load_views(engine):
    # Uma transacao consistente mesmo se outra ingestao terminar durante as consultas.
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn:
        frames = {name: pd.read_sql_query(text('SELECT * FROM ' + name), conn) for name in VIEWS}
        frames['periodo'] = pd.read_sql_query(text('SELECT min(noted_at) AS inicio, max(noted_at) AS fim FROM temperature_readings'), conn)
    return frames
