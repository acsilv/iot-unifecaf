# Roteiro do vídeo — Termo

Duração planejada: aproximadamente 3min45s. Limite: quatro minutos.
Grave a tela com sua narração e deixe os arquivos indicados abertos antes de começar.

## Preparação

- Abra http://localhost:8501 e selecione **Todos**.
- Abra o Docker Desktop na lista de containers do projeto **facul-iot**.
- Abra `compose.yaml`, `src/pipeline.py`, `sql/02_views.sql` e `docs/resultados/primeira_importacao.json` no editor.
- Deixe `docs/resultados/verificacao_testes.json` disponível para o encerramento.
- Aumente o zoom do editor para o código ficar legível.
- Não abra `.env` nem mostre senhas. Não precisa executar a importação durante a gravação.

## 0:00–0:25 — Apresentação

**Mostre:** o topo do dashboard e os quatro indicadores.

**Fale:**

> Este é o Termo, um projeto de análise de temperaturas de dispositivos IoT. O objetivo é transformar registros de temperatura em informações para comparar ambientes internos e externos. O pipeline utiliza uma base real do Kaggle, faz o processamento em Python, armazena os dados no PostgreSQL e apresenta os resultados em um dashboard interativo.

## 0:25–0:55 — Tecnologias e Docker

**Mostre:** `compose.yaml` e os containers no Docker Desktop.

**Fale:**

> A estrutura possui três serviços: o banco PostgreSQL, o importador e o dashboard. O Docker organiza a execução desses serviços. Primeiro, o banco precisa estar disponível; depois ocorre a importação; por último, o dashboard é iniciado. O pandas trata os dados, e o SQLAlchemy faz a conexão e controla as transações no banco.

O serviço `ingest` encerrado com código **0** significa que a importação terminou corretamente.

## 0:55–1:30 — Processamento dos dados

**Mostre:** `src/pipeline.py`, nas funções `normalize` e `import_csv`; depois, `primeira_importacao.json`, com as contagens.

**Fale:**

> O arquivo original contém 97.606 linhas. O processamento valida as datas, os valores de temperatura, os identificadores e o ambiente de cada leitura. Foi encontrado um ID repetido com conteúdo idêntico. Após remover essa duplicata, o banco ficou com 97.605 leituras únicas, sem rejeições por formato. A importação pode ser repetida sem duplicar os registros existentes.

## 1:30–2:00 — As três views SQL

**Mostre:** `sql/02_views.sql`, passando pelas três definições.

**Fale:**

> Foram criadas três views SQL. A primeira calcula a temperatura média por local e ambiente. A segunda conta as leituras por hora do dia, considerando todas as datas. A terceira calcula as temperaturas mínimas e máximas de cada dia. Essas consultas alimentam os três gráficos do dashboard e mantêm a separação entre as leituras internas e externas.

## 2:00–3:05 — Demonstração do dashboard

**Mostre, nesta ordem:**

1. Selecione **Todos** e apresente os quatro indicadores.
2. Aponte **Média por local e ambiente**.
3. Selecione **Interno**: **20.345 leituras**, média de **30,5 °C** no indicador.
4. Selecione **Externo**: **77.260 leituras**, média de **36,3 °C** no indicador.
5. Volte para **Todos** e aponte **Leituras ao longo do dia**.
6. Role até **Extremos de temperatura por dia** e passe o mouse sobre um ponto.
7. Expanda **Consultar tabela e exportar os dados agregados** e clique em **Baixar resumo diário (CSV)**.

**Fale enquanto demonstra:**

> O painel permite filtrar os ambientes e acompanhar os indicadores. A média interna é de aproximadamente 30,45 graus, e a externa é de 36,27 graus. O gráfico por hora mostra a distribuição da coleta, com mais registros às 14 horas. Isso não significa que seja a hora mais quente. O gráfico diário mostra os extremos ao longo do período, incluindo uma máxima externa de 51 graus. Também é possível consultar a tabela e exportar o resumo diário em CSV.

Os indicadores arredondam as médias para uma casa decimal; a fala usa duas casas.

## 3:05–3:45 — Validação, limites e conclusão

**Mostre:** `docs/resultados/verificacao_testes.json`, destacando **11 testes aprovados**; depois volte ao dashboard.

**Fale:**

> A validação incluiu 11 testes aprovados, cobrindo o tratamento dos dados, a reimportação e o cancelamento de transações com conflitos. Os resultados das três views foram conferidos com cálculos sobre o CSV original. Como a coleta é irregular, as médias representam os registros disponíveis, e valores extremos precisam ser investigados antes de decisões operacionais. O projeto pode apoiar o acompanhamento de ambientes e, futuramente, receber coleta contínua e alertas definidos para cada contexto.

## Depois da gravação

- Confira se o vídeo tem no máximo quatro minutos e se a narração está audível.
- Publique como **público** ou **não listado** no YouTube, ou em outra rede aceita.
- Abra o link em uma janela sem login para confirmar o acesso.
- Envie o link para reunir os arquivos finais da entrega.
