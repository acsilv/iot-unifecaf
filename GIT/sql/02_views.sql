-- device_id corresponde ao local room_id/id, nao a um sensor individual.
CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
SELECT device_id, location, COUNT(*) AS leituras,
       AVG(temperature) AS avg_temp,
       MIN(temperature) AS temp_min, MAX(temperature) AS temp_max
FROM temperature_readings GROUP BY device_id, location;

-- Distribuicao por HORA DO DIA, somando todas as datas da base.
CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT EXTRACT(HOUR FROM noted_at)::INTEGER AS hora, location,
       COUNT(*) AS contagem
FROM temperature_readings
GROUP BY EXTRACT(HOUR FROM noted_at), location;

CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT noted_at::DATE AS data, location, COUNT(*) AS leituras,
       MIN(temperature) AS temp_min, MAX(temperature) AS temp_max,
       AVG(temperature) AS temp_media
FROM temperature_readings GROUP BY noted_at::DATE, location;
