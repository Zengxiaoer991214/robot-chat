# Robot Chat - AI Group Chat System

![Vue.js](https://img.shields.io/badge/vue-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

A modern, web-based AI group chat system that orchestrates autonomous conversations between multiple AI agents. Create chat rooms, assign roles (personas), and watch as agents powered by different LLMs (OpenAI, DeepSeek, Ollama) debate, discuss, and collaborate on topics.

## ✨ Features

- **🎭 Role-Based Agents**: Create distinct personas with specific professions, ages, genders, and aggressiveness levels.
- **🤖 Multi-Model Support**: Seamlessly mix agents powered by OpenAI (GPT), DeepSeek, and local Ollama models.
- **💬 Real-Time Interaction**: Watch conversations unfold live via WebSocket streaming.
- **🏟️ Versatile Modes**:
  - **Debate Mode**: Structured arguments between opposing viewpoints.
  - **Group Chat**: Casual, multi-party conversations.
- **📱 Responsive Design**: Apple-style aesthetic UI optimized for both desktop and mobile devices.
- **🔌 Robust API**: Full RESTful API support for external integrations.

## 🏗️ Architecture

The project follows a modern full-stack architecture:

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Styling**: Tailwind CSS with custom glassmorphism design
- **State Management**: Reactive refs and centralized stores
- **Routing**: Vue Router

### Backend
- **Framework**: FastAPI (High-performance async Python framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Orchestration**: Custom `Orchestrator` service for turn-taking and context management
- **LLM Abstraction**: Adapter pattern to unify different AI providers

## 🚀 Getting Started

### Prerequisites
- Node.js 16+
- Python 3.10+
- PostgreSQL 12+
- (Optional) Ollama for running local models

### 1. Database Setup

```bash
# Create the database
createdb ai_chat_db

# The schema will be automatically initialized by Alembic or on first run
# Alternatively, use the provided SQL file:
psql -d ai_chat_db -f backend/schema.sql
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DB credentials and API keys:
# DATABASE_URL=postgresql://postgres:password@localhost/ai_chat_db
# OPENAI_API_KEY=sk-...

# Run the server
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit `http://localhost:5173` to open the application.

## 📦 Deployment & CI/CD

This project uses **GitHub Actions** for automated deployment. The workflow builds a Docker image, pushes it to the GitHub Container Registry (GHCR), and deploys it to your remote server.

### Configuring GitHub Secrets

To enable the deployment pipeline, you must configure the following **Secrets** in your GitHub repository settings (`Settings` -> `Secrets and variables` -> `Actions`):

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `DATABASE_URL` | **Required**. The full connection string to your production PostgreSQL database. | `postgresql://user:pass@1.2.3.4:5432/dbname` |
| `SERVER_HOST` | The IP address or domain of your deployment server. | `203.0.113.1` |
| `SERVER_USER` | The SSH username for logging into the server. | `ubuntu` or `root` |
| `SSH_PRIVATE_KEY` | The SSH private key content for passwordless authentication. | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `APP_PASSWORD` | (Optional) Admin password for the application if enabled. | `CorrectHorseBatteryStaple` |

### Configuring Variables

You can also set non-sensitive configuration in the **Variables** tab:

| Variable Name | Description | Example Value |
|---------------|-------------|---------------|
| `APP_URL` | The public URL where the app will be accessible. | `https://chat.example.com` |

### Deployment Workflow

1. **Push to `main` branch**: Triggers the build and deploy pipeline.
2. **Build**: Docker image is built and pushed to `ghcr.io/your-username/robot-chat`.
3. **Deploy**: The script logs into your server via SSH, pulls the new image, and restarts the container with the updated environment variables (including the `DATABASE_URL` injected from Secrets).

## 📚 API Documentation

When the backend is running, interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
