-- Project Icarus Database Schema
-- AI Red Team vs Blue Team Cyber Range

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Games table: tracks overall game sessions
CREATE TABLE IF NOT EXISTS games (
    game_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    start_time TIMESTAMP NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP,
    red_team_model VARCHAR(100) NOT NULL,
    blue_team_model VARCHAR(100) NOT NULL,
    scenario VARCHAR(100) NOT NULL,
    red_score INT DEFAULT 0,
    blue_score INT DEFAULT 0,
    winner VARCHAR(10),
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Rounds table: individual turn-by-turn actions
CREATE TABLE IF NOT EXISTS rounds (
    round_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    round_number INT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    phase VARCHAR(50) NOT NULL,

    -- Red team data
    red_observation TEXT,
    red_reasoning TEXT,
    red_action TEXT,
    red_result TEXT,
    red_success BOOLEAN,
    red_points_earned INT DEFAULT 0,
    red_execution_time_ms INT,

    -- Blue team data
    blue_observation TEXT,
    blue_reasoning TEXT,
    blue_action TEXT,
    blue_result TEXT,
    blue_success BOOLEAN,
    blue_points_earned INT DEFAULT 0,
    blue_execution_time_ms INT,

    -- State tracking
    red_access_level VARCHAR(50),
    blue_services_up TEXT[],
    blue_ips_blocked TEXT[],
    state_snapshot JSONB
);

-- Command log: detailed execution history
CREATE TABLE IF NOT EXISTS command_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID REFERENCES rounds(round_id) ON DELETE CASCADE,
    game_id UUID REFERENCES games(game_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    team VARCHAR(10) NOT NULL,
    container VARCHAR(50) NOT NULL,
    command TEXT NOT NULL,
    exit_code INT,
    stdout TEXT,
    stderr TEXT,
    execution_time_ms INT,
    working_directory VARCHAR(255)
);

-- Telemetry: system monitoring data
CREATE TABLE IF NOT EXISTS telemetry (
    telemetry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID REFERENCES rounds(round_id) ON DELETE CASCADE,
    game_id UUID REFERENCES games(game_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    metric_type VARCHAR(50) NOT NULL,
    metric_data JSONB NOT NULL,
    anomaly_detected BOOLEAN DEFAULT FALSE,
    severity VARCHAR(20),
    source_container VARCHAR(50)
);

-- Events: significant milestones and achievements
CREATE TABLE IF NOT EXISTS events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID NOT NULL REFERENCES games(game_id) ON DELETE CASCADE,
    round_id UUID REFERENCES rounds(round_id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,
    team VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    points_awarded INT DEFAULT 0,
    metadata JSONB
);

-- AI memory: learned patterns and strategies
CREATE TABLE IF NOT EXISTS ai_memory (
    memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    game_id UUID REFERENCES games(game_id) ON DELETE CASCADE,
    team VARCHAR(10) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    memory_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    relevance_score FLOAT DEFAULT 0.5,
    successful BOOLEAN,
    context JSONB
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_rounds_game_id ON rounds(game_id);
CREATE INDEX IF NOT EXISTS idx_rounds_round_number ON rounds(game_id, round_number);
CREATE INDEX IF NOT EXISTS idx_command_log_round ON command_log(round_id);
CREATE INDEX IF NOT EXISTS idx_command_log_game ON command_log(game_id);
CREATE INDEX IF NOT EXISTS idx_events_game ON events(game_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_round ON telemetry(round_id);
CREATE INDEX IF NOT EXISTS idx_telemetry_game ON telemetry(game_id);
CREATE INDEX IF NOT EXISTS idx_ai_memory_game_team ON ai_memory(game_id, team);

-- Create view for game statistics
CREATE OR REPLACE VIEW game_statistics AS
SELECT
    g.game_id,
    g.scenario,
    g.red_team_model,
    g.blue_team_model,
    g.red_score,
    g.blue_score,
    g.winner,
    g.status,
    COUNT(DISTINCT r.round_id) as total_rounds,
    g.start_time,
    g.end_time,
    EXTRACT(EPOCH FROM (COALESCE(g.end_time, NOW()) - g.start_time)) as duration_seconds
FROM games g
LEFT JOIN rounds r ON g.game_id = r.game_id
GROUP BY g.game_id;

-- Grant permissions to gamemaster user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gamemaster;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gamemaster;
