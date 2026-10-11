# Base original

Baixe **Temperature Readings: IoT Devices**, de Atul Anand Jha:
https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices

Extraia `IOT-temp.csv` nesta pasta. O CSV original e o ZIP baixado nao sao publicados no repositorio. O link de origem e o hash da versao utilizada estao documentados em `docs/resultados/primeira_importacao.json`.

Colunas: `id`, `room_id/id`, `noted_date`, `temp`, `out/in`. Datas em dia-mes-ano hora:minuto. A origem nao identifica sensores individuais nem informa fuso horario. O campo `room_id/id` e preservado como `device_id` por compatibilidade com o exemplo da disciplina; representa um local.
