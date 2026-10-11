"""Gera a documentacao resumida do projeto em PDF."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image

DOCS = Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold')
BLACK = colors.black
WIDTH = A4[0] - 108
styles = {
    'body': ParagraphStyle('body', fontName='Arial', fontSize=11, leading=15,
                           textColor=BLACK, spaceAfter=9),
    'title': ParagraphStyle('title', fontName='Arial-Bold', fontSize=17, leading=22,
                            textColor=BLACK, spaceAfter=12),
    'heading': ParagraphStyle('heading', fontName='Arial-Bold', fontSize=12, leading=16,
                              textColor=BLACK, spaceBefore=10, spaceAfter=6),
    'small': ParagraphStyle('small', fontName='Arial', fontSize=9, leading=12,
                            textColor=BLACK, spaceAfter=7),
}
story = []

def p(text, style='body'):
    return Paragraph(text, styles[style])

def add(text, style='body'):
    story.append(p(text, style))

def table(rows, widths):
    data = [[p(str(cell), 'small') for cell in row] for row in rows]
    item = Table(data, colWidths=widths, repeatRows=1)
    item.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOX', (0, 0), (-1, -1), 0.5, BLACK),
        ('INNERGRID', (0, 0), (-1, -1), 0.3, BLACK),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(item)
    story.append(Spacer(1, 8))

add('Termo - Pipeline de dados com IoT e Docker', 'title')
add('Disruptive Architectures | Documentação do projeto', 'small')

add('1. Objetivo', 'heading')
add('O projeto organiza leituras de temperatura para comparar ambientes internos e externos. '
    'A proposta é ler um arquivo CSV, tratar os dados em Python, armazená-los no PostgreSQL '
    'e consultar os resultados em um dashboard Streamlit. Esse tipo de análise pode ajudar '
    'no acompanhamento de ambientes e na identificação de temperaturas fora do esperado.')

add('2. Desenvolvimento', 'heading')
add('Foi utilizada a base Temperature Readings: IoT Devices, de Atul Anand Jha, disponível no '
    'Kaggle. O arquivo IOT-temp.csv possui identificador, local, data, temperatura e ambiente '
    '(In para interno e Out para externo).')
add('As bibliotecas pandas, SQLAlchemy, psycopg2-binary, Streamlit e Plotly foram instaladas '
    'em um ambiente Python. O Docker Compose configura três serviços: db, com PostgreSQL 17; '
    'ingest, que executa a importação; e dashboard, que apresenta os gráficos. O banco usa '
    'um volume para manter os dados entre execuções.')
add('O script src/pipeline.py lê o CSV e verifica campos obrigatórios, datas, temperaturas '
    'numéricas e o ambiente. Das 97.606 linhas originais, uma repetia um ID com o mesmo conteúdo. '
    'Após retirar essa duplicata, foram armazenadas 97.605 leituras, sem rejeições por formato. '
    'A carga usa uma transação: se houver conflito, as alterações são canceladas. Reimportar '
    'o arquivo não duplica os registros já existentes.')
add('Depois da carga, são criadas as views SQL. O dashboard consulta essas views e monta os '
    'gráficos com Plotly. Para executar, é necessário colocar o CSV em data/, configurar '
    'o arquivo .env e rodar <b>docker compose up -d --build</b>. O painel fica disponível '
    'em <b>http://localhost:8501</b>. As instruções completas estão no README.')

add('3. Views SQL', 'heading')
add('<b>avg_temp_por_dispositivo:</b> agrupa por local e ambiente e calcula quantidade de '
    'leituras, média, mínima e máxima. Alimenta o gráfico de barras para comparar os grupos. '
    'O campo device_id representa o local informado na base, não um sensor individual.')
add('<b>leituras_por_hora:</b> conta os registros por hora do dia e ambiente, reunindo todas '
    'as datas. Mostra em quais horários houve mais coleta, sem indicar a temperatura desses horários.')
add('<b>temp_max_min_por_dia:</b> agrupa por data e ambiente e calcula quantidade, média, '
    'mínima e máxima. Alimenta o gráfico de extremos diários e o resumo exportado em CSV. '
    'O código das três views está em sql/02_views.sql.')

story.append(PageBreak())
add('4. Dashboard', 'title')
add('O painel apresenta os indicadores gerais e os três gráficos. O filtro permite selecionar '
    'todos os registros ou apenas um ambiente. Também é possível consultar a tabela e baixar '
    'o resumo diário em CSV.')
img = Image(str(DOCS / 'imagens/dashboard-visao-geral.png'))
original_width, original_height = img.imageWidth, img.imageHeight
img.drawWidth = WIDTH
img.drawHeight = WIDTH * original_height / original_width
story.append(img)
story.append(Spacer(1, 7))
add('Figura 1. Dashboard executado com os dados importados no PostgreSQL.', 'small')
add('No filtro Interno, o painel mostra 20.345 leituras e média arredondada de 30,5 °C. '
    'No filtro Externo, são 77.260 leituras e média de 36,3 °C. As lacunas no gráfico '
    'diário correspondem aos dias sem medições.')

story.append(PageBreak())
add('5. Resultados e conclusão', 'title')
table([
    ['<b>Ambiente</b>', '<b>Leituras</b>', '<b>Média</b>', '<b>Mínima</b>', '<b>Máxima</b>'],
    ['Interno', '20.345', '30,45 °C', '21 °C', '41 °C'],
    ['Externo', '77.260', '36,27 °C', '24 °C', '51 °C'],
    ['Total', '97.605', '35,05 °C', '21 °C', '51 °C'],
], [100, 100, 100, 85, WIDTH - 385])
add('A média externa foi 5,81 °C maior que a interna. Essa diferença pode orientar uma '
    'investigação sobre as condições dos ambientes, mas os dados não comprovam suas causas. '
    'A máxima externa de 51 °C também merece atenção: antes de uma decisão, seria necessário '
    'verificar a instalação e a calibração do sensor.')
add('O horário com mais registros foi 14h. Isso representa a frequência de coleta e não '
    'significa que seja o horário mais quente. Como cerca de 79,2% das leituras são externas, '
    'esse grupo tem maior influência na média geral.')
add('A base vai de 28/07/2018 a 08/12/2018, com registros em 86 dias. A coleta é irregular, '
    'portanto as médias descrevem as leituras disponíveis, sem ponderação pelo tempo. Há '
    'apenas o local Room Admin, sem identificação individual de sensor. As datas foram '
    'preservadas sem fuso, e a apresentação adota graus Celsius, embora o CSV não traga '
    'uma coluna de unidade.')
add('Foram aprovados 11 testes, incluindo validação, reimportação e cancelamento de cargas '
    'com conflito. As três views foram conferidas com cálculos em pandas sobre o CSV '
    'original. Os filtros e a exportação também foram verificados no navegador.')
add('O projeto cumpriu o fluxo de processamento, armazenamento e visualização. Em uso '
    'prático, pode apoiar o acompanhamento térmico e o planejamento de climatização. '
    'Uma continuação seria receber leituras de forma contínua e criar alertas com limites '
    'definidos para cada ambiente.')

add('6. Referências', 'heading')
refs = [
    ('Atul Anand Jha. Temperature Readings: IoT Devices. Kaggle.',
     'https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices'),
    ('Docker. Ordem de inicialização no Compose.',
     'https://docs.docker.com/compose/how-tos/startup-order/'),
    ('PostgreSQL 17. CREATE VIEW.', 'https://www.postgresql.org/docs/17/sql-createview.html'),
    ('SQLAlchemy. Transações e conexões.',
     'https://docs.sqlalchemy.org/en/21/tutorial/dbapi_transactions.html'),
    ('Streamlit. Gráficos Plotly.',
     'https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart'),
]
for title, url in refs:
    add(f'{title}<br/><link href="{url}" color="black">{url}</link>', 'small')
add('Consulta às fontes: 10/10/2026.', 'small')
add('Vídeo de apresentação: <link href="https://youtu.be/ordWjpNnjTs" color="black">'
    'https://youtu.be/ordWjpNnjTs</link>', 'small')

def footer(canvas, doc):
    canvas.setFillColor(BLACK)
    canvas.setFont('Arial', 9)
    canvas.drawRightString(A4[0] - 54, 30, str(doc.page))

output = DOCS / 'documentacao_termo.pdf'
document = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=54, rightMargin=54,
    topMargin=45, bottomMargin=45, title='Termo - Pipeline de dados com IoT e Docker',
    author='', subject='Documentação do projeto')
document.build(story, onFirstPage=footer, onLaterPages=footer)
print(output)
