CREATE TABLE IF NOT EXISTS temperature_readings (
    reading_id TEXT PRIMARY KEY,
    device_id TEXT NOT NULL CHECK (length(trim(device_id)) > 0),
    noted_at TIMESTAMP NOT NULL,
    temperature DOUBLE PRECISION NOT NULL
        CHECK (temperature > '-Infinity'::float8 AND temperature < 'Infinity'::float8),
    location TEXT NOT NULL CHECK (location IN ('In', 'Out'))
);
CREATE INDEX IF NOT EXISTS idx_readings_date ON temperature_readings (noted_at);
CREATE TABLE IF NOT EXISTS import_runs (
    id BIGSERIAL PRIMARY KEY,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_sha256 TEXT NOT NULL,
    source_name TEXT NOT NULL,
    input_rows INTEGER NOT NULL,
    rejected_rows INTEGER NOT NULL,
    duplicate_ids INTEGER NOT NULL,
    inserted_rows INTEGER NOT NULL,
    existing_rows INTEGER NOT NULL
);
