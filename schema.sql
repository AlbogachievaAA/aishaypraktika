CREATE TABLE IF NOT EXISTS daily_log (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    date DATE NOT NULL,
    mood INTEGER CHECK (mood BETWEEN 1 AND 5),
    study_hours REAL CHECK (study_hours >= 0),
    sleep_hours REAL CHECK (sleep_hours >= 0),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

CREATE INDEX IF NOT EXISTS idx_user_date ON daily_log(user_id, date);