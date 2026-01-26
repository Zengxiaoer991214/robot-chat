"""
Unit tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models import Agent, Room, User

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestAgentAPI:
    """Tests for Agent API endpoints."""
    
    def test_create_agent_success(self, client):
        """Test successful agent creation."""
        agent_data = {
            "name": "Test Agent",
            "avatar_url": "https://example.com/avatar.png",
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "system_prompt": "You are a helpful assistant.",
            "temperature": 0.7
        }
        
        response = client.post("/api/agents", json=agent_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == agent_data["name"]
        assert data["provider"] == agent_data["provider"]
        assert "id" in data
    
    def test_create_agent_invalid_provider(self, client):
        """Test agent creation with invalid provider."""
        agent_data = {
            "name": "Test Agent",
            "provider": "invalid_provider",
            "model_name": "test-model",
            "system_prompt": "Test prompt"
        }
        
        response = client.post("/api/agents", json=agent_data)
        
        assert response.status_code == 400
        assert "Invalid provider" in response.json()["detail"]
    
    def test_create_agent_missing_fields(self, client):
        """Test agent creation with missing required fields."""
        agent_data = {
            "name": "Test Agent"
            # Missing required fields
        }
        
        response = client.post("/api/agents", json=agent_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_agents_empty(self, client):
        """Test getting agents when none exist."""
        response = client.get("/api/agents")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_agents_list(self, client):
        """Test getting list of agents."""
        # Create test agents
        for i in range(3):
            client.post("/api/agents", json={
                "name": f"Agent {i}",
                "provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "system_prompt": f"You are agent {i}"
            })
        
        response = client.get("/api/agents")
        
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) == 3
    
    def test_get_agent_by_id_success(self, client):
        """Test getting specific agent by ID."""
        # Create agent
        create_response = client.post("/api/agents", json={
            "name": "Test Agent",
            "provider": "openai",
            "model_name": "gpt-4",
            "system_prompt": "Test"
        })
        agent_id = create_response.json()["id"]
        
        # Get agent
        response = client.get(f"/api/agents/{agent_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent_id
        assert data["name"] == "Test Agent"
    
    def test_get_agent_not_found(self, client):
        """Test getting non-existent agent."""
        response = client.get("/api/agents/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_agent_success(self, client):
        """Test updating an agent."""
        # Create agent
        create_response = client.post("/api/agents", json={
            "name": "Original Name",
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "system_prompt": "Original prompt"
        })
        agent_id = create_response.json()["id"]
        
        # Update agent
        update_data = {"name": "Updated Name", "temperature": 0.9}
        response = client.patch(f"/api/agents/{agent_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["temperature"] == 0.9
        assert data["provider"] == "openai"  # Unchanged
    
    def test_update_agent_not_found(self, client):
        """Test updating non-existent agent."""
        response = client.patch("/api/agents/999", json={"name": "New Name"})
        
        assert response.status_code == 404
    
    def test_delete_agent_success(self, client):
        """Test deleting an agent."""
        # Create agent
        create_response = client.post("/api/agents", json={
            "name": "To Delete",
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "system_prompt": "Test"
        })
        agent_id = create_response.json()["id"]
        
        # Delete agent
        response = client.delete(f"/api/agents/{agent_id}")
        
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/agents/{agent_id}")
        assert get_response.status_code == 404
    
    def test_delete_agent_not_found(self, client):
        """Test deleting non-existent agent."""
        response = client.delete("/api/agents/999")
        
        assert response.status_code == 404


class TestRoomAPI:
    """Tests for Room API endpoints."""
    
    def test_create_room_success(self, client):
        """Test successful room creation."""
        room_data = {
            "name": "Test Room",
            "topic": "Testing AI conversations",
            "max_rounds": 10
        }
        
        response = client.post("/api/rooms", json=room_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == room_data["name"]
        assert data["topic"] == room_data["topic"]
        assert data["status"] == "idle"
        assert data["current_rounds"] == 0
    
    def test_create_room_with_agents(self, client):
        """Test room creation with agents."""
        # Create agents first
        agent1 = client.post("/api/agents", json={
            "name": "Agent 1",
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "system_prompt": "Test"
        }).json()
        
        agent2 = client.post("/api/agents", json={
            "name": "Agent 2",
            "provider": "openai",
            "model_name": "gpt-4",
            "system_prompt": "Test"
        }).json()
        
        # Create room with agents
        room_data = {
            "name": "Test Room",
            "topic": "Test Topic",
            "agent_ids": [agent1["id"], agent2["id"]]
        }
        
        response = client.post("/api/rooms", json=room_data)
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["agents"]) == 2
    
    def test_create_room_invalid_agent_id(self, client):
        """Test room creation with invalid agent ID."""
        room_data = {
            "name": "Test Room",
            "topic": "Test Topic",
            "agent_ids": [999]  # Non-existent agent
        }
        
        response = client.post("/api/rooms", json=room_data)
        
        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()
    
    def test_get_rooms_list(self, client):
        """Test getting list of rooms."""
        # Create test rooms
        for i in range(3):
            client.post("/api/rooms", json={
                "name": f"Room {i}",
                "topic": f"Topic {i}"
            })
        
        response = client.get("/api/rooms")
        
        assert response.status_code == 200
        rooms = response.json()
        assert len(rooms) == 3
    
    def test_get_room_by_id(self, client):
        """Test getting specific room by ID."""
        create_response = client.post("/api/rooms", json={
            "name": "Test Room",
            "topic": "Test Topic"
        })
        room_id = create_response.json()["id"]
        
        response = client.get(f"/api/rooms/{room_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == room_id
    
    def test_join_room_success(self, client):
        """Test joining agent to room."""
        # Create agent and room
        agent = client.post("/api/agents", json={
            "name": "Test Agent",
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "system_prompt": "Test"
        }).json()
        
        room = client.post("/api/rooms", json={
            "name": "Test Room",
            "topic": "Test Topic"
        }).json()
        
        # Join room
        response = client.post(f"/api/rooms/{room['id']}/join", json={
            "agent_id": agent["id"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["agents"]) == 1
        assert data["agents"][0]["id"] == agent["id"]
    
    def test_join_room_duplicate_agent(self, client):
        """Test joining same agent twice."""
        # Create agent and room with agent
        agent = client.post("/api/agents", json={
            "name": "Test Agent",
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "system_prompt": "Test"
        }).json()
        
        room = client.post("/api/rooms", json={
            "name": "Test Room",
            "topic": "Test Topic",
            "agent_ids": [agent["id"]]
        }).json()
        
        # Try to join again
        response = client.post(f"/api/rooms/{room['id']}/join", json={
            "agent_id": agent["id"]
        })
        
        assert response.status_code == 400
        assert "already in room" in response.json()["detail"]
    
    def test_get_room_messages_empty(self, client):
        """Test getting messages from empty room."""
        room = client.post("/api/rooms", json={
            "name": "Test Room",
            "topic": "Test Topic"
        }).json()
        
        response = client.get(f"/api/rooms/{room['id']}/messages")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_stop_room_success(self, client):
        """Test stopping a room."""
        room = client.post("/api/rooms", json={
            "name": "Test Room",
            "topic": "Test Topic"
        }).json()
        
        response = client.post(f"/api/rooms/{room['id']}/stop")
        
        assert response.status_code == 200
        
        # Verify room status changed
        get_response = client.get(f"/api/rooms/{room['id']}")
        assert get_response.json()["status"] == "idle"


class TestHealthEndpoints:
    """Tests for health and root endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
