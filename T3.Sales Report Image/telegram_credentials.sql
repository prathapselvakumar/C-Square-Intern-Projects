-- Table read by send_report_from_db.py to find the Telegram chat and bot token.
-- The column types below are a suggested schema; only the column names are required.
CREATE DATABASE IF NOT EXISTS chat_id;

CREATE TABLE IF NOT EXISTS chat_id.telegram_table (
    chat_id   VARCHAR(32)  NOT NULL,
    api_token VARCHAR(128) NOT NULL
);

-- Check the stored credentials.
SELECT * FROM chat_id.telegram_table;
