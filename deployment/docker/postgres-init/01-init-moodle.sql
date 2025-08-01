-- MoodleClaude v3.0 PostgreSQL Initialization
-- Optimizes database for Moodle performance

-- Ensure UTF8 encoding
UPDATE pg_database SET datcollate='C', datctype='C' WHERE datname='moodle';

-- Create additional database for testing if needed
CREATE DATABASE moodle_test OWNER moodle;
GRANT ALL PRIVILEGES ON DATABASE moodle_test TO moodle;

-- Optimize PostgreSQL settings for Moodle
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();