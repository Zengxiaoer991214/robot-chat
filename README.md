# AI Group Chat System

A web-based AI group chat system that allows users to create chat rooms, set topics, and invite AI agents powered by different LLMs (OpenAI, DeepSeek, Ollama) to have autonomous conversations.

## Features

- **Multi-Model Integration**: Support for OpenAI (GPT), DeepSeek, and local models (Ollama)
- **Group Chat Management**: Create rooms with customizable topics and maximum round limits
- **Autonomous Conversations**: AI agents automatically engage in multi-turn conversations
- **Real-Time Updates**: WebSocket support for live message streaming
- **RESTful API**: Comprehensive API for managing agents, rooms, and messages

## Architecture

### Backend (Python/FastAPI)
- **FastAPI Framework**: High-performance async API server
- **SQLAlchemy ORM**: Database abstraction with PostgreSQL
- **LLM Adapter Pattern**: Unified interface for different AI providers
- **Chat Orchestrator**: Manages autonomous conversations with round-robin turn-taking
- **WebSocket Support**: Real-time message broadcasting

### Database (PostgreSQL)
- Users, Agents, Rooms, Messages tables
- Many-to-many relationships for room-agent associations
- Optimized indexes for query performance

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- (Optional) Ollama for local models

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd robot-chat/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL database**
   ```bash
   # Create database
   createdb ai_chat_db
   
   # Initialize schema
   psql -d ai_chat_db -f schema.sql
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run the server**
   ```bash
   # Development mode
   python -m app.main
   
   # Or with uvicorn
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Agents
- `POST /api/agents` - Create a new AI agent
- `GET /api/agents` - List all agents
- `GET /api/agents/{id}` - Get specific agent
- `PATCH /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

#### Rooms
- `POST /api/rooms` - Create a new room
- `GET /api/rooms` - List all rooms
- `GET /api/rooms/{id}` - Get specific room
- `POST /api/rooms/{id}/join` - Add agent to room
- `POST /api/rooms/{id}/start` - Start autonomous conversation
- `POST /api/rooms/{id}/stop` - Stop conversation
- `GET /api/rooms/{id}/messages` - Get room messages

#### WebSocket
- `WS /ws/rooms/{id}` - Real-time message updates

## Usage Example

### 1. Create AI Agents

```bash
# Create a philosopher agent
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Socrates",
    "provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "system_prompt": "You are Socrates, the ancient Greek philosopher. Engage in thoughtful dialogue using the Socratic method.",
    "temperature": 0.7
  }'

# Create a scientist agent
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Einstein",
    "provider": "openai",
    "model_name": "gpt-3.5-turbo",
    "system_prompt": "You are Albert Einstein. Discuss topics with scientific rigor and curiosity.",
    "temperature": 0.7
  }'
```

### 2. Create a Room with Agents

```bash
curl -X POST http://localhost:8000/api/rooms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Philosophy Debate",
    "topic": "What is the nature of reality?",
    "max_rounds": 10,
    "agent_ids": [1, 2]
  }'
```

### 3. Start the Conversation

```bash
curl -X POST http://localhost:8000/api/rooms/1/start
```

### 4. Watch Messages in Real-Time

Connect to WebSocket: `ws://localhost:8000/ws/rooms/1`

Or retrieve messages via API:
```bash
curl http://localhost:8000/api/rooms/1/messages
```

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_llm_adapter.py

# Run with verbose output
pytest -v
```

### Test Coverage

The test suite includes:
- **LLM Adapter Tests**: Testing all providers (OpenAI, DeepSeek, Ollama)
- **Orchestrator Tests**: Conversation flow, agent selection, edge cases
- **API Tests**: All endpoints with success and failure scenarios
- **Edge Case Testing**: Empty lists, invalid inputs, error handling

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_chat_db

# API Keys
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=sk-...

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Application Settings
MAX_CONTEXT_MESSAGES=20
DEFAULT_SLEEP_BETWEEN_MESSAGES=2.0
```

### Supported LLM Providers

#### OpenAI
- Models: gpt-3.5-turbo, gpt-4, gpt-4-turbo, etc.
- Requires: `OPENAI_API_KEY`

#### DeepSeek
- Models: deepseek-chat, deepseek-coder
- Requires: `DEEPSEEK_API_KEY`
- Uses OpenAI-compatible API

#### Ollama (Local)
- Models: llama3, mistral, codellama, etc.
- Requires: Ollama running locally
- Default URL: http://localhost:11434

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── agents.py     # Agent CRUD endpoints
│   │   ├── rooms.py      # Room management endpoints
│   │   └── websocket.py  # WebSocket handler
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings management
│   │   └── database.py   # Database connection
│   ├── models/           # SQLAlchemy models
│   │   └── __init__.py   # User, Agent, Room, Message models
│   ├── schemas/          # Pydantic schemas
│   │   └── __init__.py   # Request/response models
│   ├── services/         # Business logic
│   │   ├── llm_adapter.py    # LLM provider adapters
│   │   └── orchestrator.py   # Chat orchestration
│   └── main.py           # FastAPI application
├── tests/                # Unit tests
│   ├── test_api.py
│   ├── test_llm_adapter.py
│   └── test_orchestrator.py
├── requirements.txt      # Python dependencies
├── schema.sql           # Database schema
└── setup.cfg            # Pytest configuration
```

## Error Handling

The system includes comprehensive error handling:

- **Validation Errors**: Pydantic validates all input data
- **Database Errors**: Transactions with rollback on failure
- **API Errors**: Proper HTTP status codes and error messages
- **LLM Errors**: Graceful handling of API failures
- **Logging**: Structured logging for debugging

## Security Considerations

- API keys can be configured per agent or system-wide
- Database credentials via environment variables
- CORS configuration for frontend integration
- Input validation on all endpoints

## Future Enhancements

- [ ] Human interruption during AI conversations
- [ ] Memory compression for long conversations
- [ ] Text-to-speech integration
- [ ] Advanced agent selection strategies
- [ ] Conversation export functionality
- [ ] Rate limiting and quota management
- [ ] Multi-language support

## License

[Specify your license here]

## Contributing

[Contribution guidelines]
