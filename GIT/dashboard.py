"""Dashboard Streamlit: todas as visualizacoes usam views do PostgreSQL."""
import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError
from src.analytics import load_views
from src.database import get_engine

st.set_page_config(page_title='Termo | Temperaturas IoT', layout='wide')
st.markdown('''<style>
.block-container {padding-top:4rem; padding-bottom:2.5rem; max-width:1460px;}
[data-testid="stHeader"] {background:rgba(246,247,251,.92);}
[data-testid="stSidebar"] {background:#fff; border-right:1px solid #E8EBF2;}
[data-testid="stSidebar"] > div:first-child {padding-top:2rem;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#768197; line-height:1.7;}
[data-testid="stMetric"] {background:#fff; border:1px solid #E8EBF2; border-radius:16px;
    padding:23px 22px; box-shadow:0 3px 12px rgba(28,39,60,.025);}
[data-testid="stMetricLabel"] {color:#6B768B; font-size:13px;}
[data-testid="stMetricValue"] {color:#202939; font-weight:600; letter-spacing:-1.2px;}
.st-key-chart-average, .st-key-chart-hour, .st-key-chart-daily {background:#fff; border:1px solid #E8EBF2;
    border-radius:16px; padding:22px; box-shadow:0 3px 12px rgba(28,39,60,.02);}
h1 {font-size:2.3rem !important; font-weight:650 !important; letter-spacing:-1.1px; padding-bottom:.4rem !important;}
h3 {font-size:1.12rem !important; font-weight:600 !important; letter-spacing:-.3px;}
[data-testid="stCaptionContainer"] {color:#7B8495;}
[data-testid="stCaptionContainer"] p {color:#6B768B !important;}
.eyebrow {color:#6554C0; font-size:11px; font-weight:700; letter-spacing:2px; margin:0 0 10px;}
.brand {display:flex; align-items:center; gap:12px; margin:10px 0 8px; font-size:27px; font-weight:700; letter-spacing:-1px;}
.brand-mark {background:#6554C0; color:white; width:34px; height:34px; border-radius:10px;
    display:inline-flex; align-items:center; justify-content:center; font-size:21px; font-weight:600;}
.context-row {display:flex; flex-wrap:wrap; gap:10px; margin:18px 0 24px;}
.context-pill {background:#fff; border:1px solid #E6E9F0; color:#647087; border-radius:7px; padding:7px 11px; font-size:12px;}
.context-pill.active {background:#EEEAF9; color:#6554C0; border-color:#E6DFF6;}
.section-label {color:#8A93A4; font-size:10px; letter-spacing:1.6px; font-weight:700; margin:4px 0 6px;}
[data-testid="stButton"] button, [data-testid="stLinkButton"] a {border-radius:9px; font-size:13px;}
[data-testid="stExpander"] {background:#fff; border-radius:12px;}
.method-note {color:#7B8495; font-size:12px; line-height:1.7; padding:18px 0; border-top:1px solid #E6E9F0; margin-top:24px;}
@media (max-width:768px) {.block-container {padding-left:1rem; padding-right:1rem;} h1 {font-size:1.8rem !important;}}
</style>''', unsafe_allow_html=True)

@st.cache_resource
def connection():
    return get_engine()

@st.cache_data(ttl=60)
def fetch():
    return load_views(connection())

st.markdown('<p class="eyebrow">MONITORAMENTO / DADOS IOT</p>', unsafe_allow_html=True)
st.title('Visão geral das temperaturas')
st.markdown('Uma leitura clara dos ambientes internos e externos, da coleta aos extremos diários.')
try:
    frames = fetch()
except (SQLAlchemyError, ValueError):
    st.error('Não foi possível carregar os dados. Inicie o PostgreSQL e execute a importação conforme o README.')
    st.stop()

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-mark">t</span>Termo</div>', unsafe_allow_html=True)
    st.caption('Inteligência sobre temperaturas')
    st.divider()
    environment = st.radio('Ambientes', ['Todos', 'Interno', 'Externo'])
    st.divider()
    st.markdown('<p class="section-label">SOBRE A BASE</p>', unsafe_allow_html=True)
    st.markdown('**Temperature Readings**\n\nKaggle · Atul Anand Jha')
    st.caption('Dados históricos · 2018')
    st.caption('In = interno · Out = externo. Datas sem fuso na fonte; preservadas como registradas.')
    if st.button('Atualizar dados', use_container_width=True):
        fetch.clear()
        st.rerun()
    st.link_button('Abrir fonte no Kaggle', 'https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices')

selected = {'Interno': 'In', 'Externo': 'Out'}.get(environment)
def subset(df):
    return df.loc[df.location.eq(selected)].copy() if selected else df.copy()

avg = subset(frames['avg_temp_por_dispositivo']).sort_values(['device_id', 'location'])
hour = subset(frames['leituras_por_hora']).sort_values(['hora', 'location'])
daily = subset(frames['temp_max_min_por_dia']).sort_values(['data', 'location'])
if avg.empty:
    st.info('Nenhuma leitura disponível para este ambiente.')
    st.stop()
labels = {'In': 'Interno', 'Out': 'Externo'}
colors = {'Interno': '#7965C8', 'Externo': '#D99250'}
for df in [avg, hour, daily]:
    df['Ambiente'] = df.location.map(labels)
avg['Local / ambiente'] = avg.device_id + ' · ' + avg['Ambiente']
count = int(avg.leituras.sum())
mean = float((avg.avg_temp * avg.leituras).sum() / count)
period = frames['periodo'].iloc[0]
st.markdown(f'''<div class="context-row">
<span class="context-pill">{pd.Timestamp(period.inicio):%d/%m/%Y} a {pd.Timestamp(period.fim):%d/%m/%Y}</span>
<span class="context-pill active">Ambiente: {environment}</span>
<span class="context-pill">Fonte: Kaggle</span></div>''', unsafe_allow_html=True)
a, b, c, d = st.columns(4, gap='medium')
a.metric('Leituras analisadas', f'{count:,}'.replace(',', '.'))
b.metric('Temperatura média', f'{mean:.1f} °C')
c.metric('Menor temperatura', f'{avg.temp_min.min():.0f} °C')
d.metric('Maior temperatura', f'{avg.temp_max.max():.0f} °C')
st.space('small')

def show(fig, key):
    fig.update_layout(template='plotly_white', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', font=dict(family='Arial', color='#738096', size=12),
        margin=dict(l=12, r=12, t=24, b=12), legend_title_text='', height=300,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        hoverlabel=dict(bgcolor='white', font_color='#202939', bordercolor='#E8EBF2'))
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor='#E8EBF2', ticks='', title_font_size=11)
    fig.update_yaxes(gridcolor='#EEF0F5', zeroline=False, title_font_size=11)
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, width='stretch', key=key, config={'displayModeBar':False})

left, right = st.columns(2)
with left, st.container(border=False, key='chart-average'):
    st.markdown('<p class="section-label">COMPARATIVO</p>', unsafe_allow_html=True)
    st.subheader('Média por local e ambiente')
    st.caption('Temperatura média dos registros de cada grupo.')
    show(px.bar(avg, x='device_id', y='avg_temp', color='Ambiente', barmode='group',
        color_discrete_map=colors, labels={'avg_temp': 'Temperatura média (°C)', 'device_id':'Local'},
        hover_data=['leituras', 'temp_min', 'temp_max']), 'media')
with right, st.container(border=False, key='chart-hour'):
    st.markdown('<p class="section-label">FREQUÊNCIA DE COLETA</p>', unsafe_allow_html=True)
    st.subheader('Leituras ao longo do dia')
    st.caption('Contagem por hora, considerando todas as datas.')
    show(px.line(hour, x='hora', y='contagem', color='Ambiente', markers=True,
        color_discrete_map=colors, labels={'hora': 'Hora do dia', 'contagem': 'Leituras'}), 'hora')

long = daily.melt(id_vars=['data', 'Ambiente'], value_vars=['temp_min', 'temp_max'],
                  var_name='Extremo', value_name='Temperatura (°C)')
long['Extremo'] = long.Extremo.map({'temp_min': 'Mínima', 'temp_max': 'Máxima'})
# Insere lacunas explicitas para que o grafico nao conecte dias sem medicao.
long['data'] = pd.to_datetime(long['data'])
calendar = pd.date_range(long.data.min(), long.data.max(), name='data')
segments = []
for (ambiente, extremo), group in long.groupby(['Ambiente', 'Extremo']):
    segment = group.set_index('data').reindex(calendar).reset_index()
    segment['Ambiente'], segment['Extremo'] = ambiente, extremo
    segments.append(segment)
long = pd.concat(segments, ignore_index=True)
with st.container(border=False, key='chart-daily'):
    st.markdown('<p class="section-label">EVOLUÇÃO HISTÓRICA</p>', unsafe_allow_html=True)
    st.subheader('Extremos de temperatura por dia')
    st.caption('Mínimas e máximas registradas. As lacunas indicam dias sem medições.')
    show(px.line(long, x='data', y='Temperatura (°C)', color='Ambiente', line_dash='Extremo',
        markers=True, color_discrete_map=colors, labels={'data': 'Data'}), 'dia')

with st.expander('Consultar tabela e exportar os dados agregados'):
    st.dataframe(daily.drop(columns='location'), hide_index=True, width='stretch')
    st.download_button('Baixar resumo diário (CSV)', daily.drop(columns='location').to_csv(index=False).encode('utf-8-sig'),
        file_name='temperaturas_diarias.csv', mime='text/csv')
st.markdown('<div class="method-note"><b>Sobre esta análise</b> &nbsp;·&nbsp; '
    'A base identifica o local Room Admin, sem ID individual de sensor. A coleta é irregular; '
    'as médias representam os registros disponíveis e não são ponderadas pelo tempo. '
    'Dados históricos de temperatura. Atualização das consultas a cada 60 segundos.</div>', unsafe_allow_html=True)
