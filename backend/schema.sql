-- Database initialization script for AI Group Chat System
-- PostgreSQL 12+

-- Create database (run as superuser)
-- CREATE DATABASE ai_chat_db;

-- Connect to the database
-- \c ai_chat_db

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Agent configuration table
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    provider VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    system_prompt TEXT NOT NULL,
    api_key_config TEXT,
    temperature FLOAT DEFAULT 0.7
);

-- Chat rooms table
CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    topic TEXT NOT NULL,
    max_rounds INT DEFAULT 20,
    current_rounds INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'idle',
    creator_id INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Room-Agent association table (many-to-many)
CREATE TABLE IF NOT EXISTS room_agents (
    room_id INT REFERENCES rooms(id) ON DELETE CASCADE,
    agent_id INT REFERENCES agents(id) ON DELETE CASCADE,
    PRIMARY KEY (room_id, agent_id)
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    room_id INT REFERENCES rooms(id) ON DELETE CASCADE,
    agent_id INT REFERENCES agents(id),
    content TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status);
CREATE INDEX IF NOT EXISTS idx_messages_room_id ON messages(room_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Sample data (optional)
-- INSERT INTO users (username) VALUES ('admin');
