"""Configuracao de conexao sem senha fixa no codigo."""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

ROOT = Path(__file__).resolve().parents[1]

def get_engine():
    load_dotenv(ROOT / '.env')
    if os.getenv('POSTGRES_HOST'):
        url = URL.create('postgresql+psycopg2',
            username=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'],
            host=os.environ['POSTGRES_HOST'], port=int(os.getenv('POSTGRES_PORT', '5432')),
            database=os.getenv('POSTGRES_DB', 'iot'))
    else:
        url = os.getenv('DATABASE_URL')
        if not url:
            raise ValueError('Configure DATABASE_URL no arquivo .env. Consulte o README.')
    return create_engine(url, pool_pre_ping=True, connect_args={'connect_timeout': 10})

def initialize(conn):
    for name in ['01_schema.sql', '02_views.sql']:
        # Scripts locais, controlados pelo projeto; nunca entrada do usuario.
        conn.execute(text((ROOT / 'sql' / name).read_text(encoding='utf-8')))
