"""
Unit tests for the Chat Orchestrator.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from app.services.orchestrator import ChatOrchestrator
from app.models import Room, Agent, Message


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def sample_room():
    """Create a sample room for testing."""
    room = MagicMock(spec=Room)
    room.id = 1
    room.name = "Test Room"
    room.topic = "Test Topic"
    room.max_rounds = 5
    room.current_rounds = 0
    room.status = "idle"
    return room


@pytest.fixture
def sample_agents():
    """Create sample agents for testing."""
    agent1 = MagicMock(spec=Agent)
    agent1.id = 1
    agent1.name = "Agent 1"
    agent1.provider = "openai"
    agent1.model_name = "gpt-3.5-turbo"
    agent1.system_prompt = "You are agent 1"
    agent1.temperature = 0.7
    agent1.api_key_config = None
    
    agent2 = MagicMock(spec=Agent)
    agent2.id = 2
    agent2.name = "Agent 2"
    agent2.provider = "openai"
    agent2.model_name = "gpt-3.5-turbo"
    agent2.system_prompt = "You are agent 2"
    agent2.temperature = 0.7
    agent2.api_key_config = None
    
    return [agent1, agent2]


class TestChatOrchestrator:
    """Tests for ChatOrchestrator."""
    
    def test_initialization(self, mock_db):
        """Test orchestrator initialization."""
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        assert orchestrator.room_id == 1
        assert orchestrator.db == mock_db
        assert orchestrator.current_agent_index == 0
        assert orchestrator._stop_requested is False
    
    def test_stop(self, mock_db):
        """Test stop functionality."""
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        orchestrator.stop()
        assert orchestrator._stop_requested is True
    
    def test_select_next_agent_round_robin(self, mock_db, sample_agents):
        """Test round-robin agent selection."""
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        
        # First selection
        agent1 = orchestrator._select_next_agent(sample_agents)
        assert agent1 == sample_agents[0]
        
        # Second selection
        agent2 = orchestrator._select_next_agent(sample_agents)
        assert agent2 == sample_agents[1]
        
        # Third selection (wraps around)
        agent3 = orchestrator._select_next_agent(sample_agents)
        assert agent3 == sample_agents[0]
    
    def test_select_next_agent_empty_list(self, mock_db):
        """Test agent selection with empty list."""
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        agent = orchestrator._select_next_agent([])
        assert agent is None
    
    def test_get_recent_messages(self, mock_db):
        """Test getting recent messages."""
        # Create mock messages
        messages = []
        for i in range(5):
            msg = MagicMock(spec=Message)
            msg.id = i + 1
            msg.content = f"Message {i + 1}"
            msg.role = "assistant"
            msg.created_at = datetime.utcnow()
            messages.append(msg)
        
        # Setup mock query
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = messages
        
        mock_db.query.return_value = mock_query
        
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        result = orchestrator._get_recent_messages(room_id=1)
        
        # Messages should be reversed to chronological order
        assert len(result) == 5
        assert result[0].id == 1
        assert result[-1].id == 5
    
    @pytest.mark.asyncio
    async def test_save_message(self, mock_db):
        """Test saving a message."""
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        
        message = await orchestrator._save_message(
            room_id=1,
            agent_id=1,
            content="Test message",
            role="assistant"
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_agent_response_success(self, mock_db, sample_agents):
        """Test successful agent response generation."""
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        
        # Mock get_recent_messages
        orchestrator._get_recent_messages = MagicMock(return_value=[])
        
        # Mock room
        room = MagicMock()
        room.id = 1
        
        # Mock LLM adapter
        with patch('app.services.orchestrator.get_llm_adapter') as mock_get_adapter:
            mock_adapter = AsyncMock()
            mock_adapter.generate = AsyncMock(return_value="Generated response")
            mock_get_adapter.return_value = mock_adapter
            
            result = await orchestrator._generate_agent_response(sample_agents[0], room)
            
            assert result == "Generated response"
            mock_adapter.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_conversation_room_not_found(self, mock_db):
        """Test starting conversation with non-existent room."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        orchestrator = ChatOrchestrator(room_id=999, db=mock_db)
        
        with pytest.raises(ValueError, match="Room 999 not found"):
            await orchestrator.start_conversation()
    
    @pytest.mark.asyncio
    async def test_start_conversation_no_agents(self, mock_db, sample_room):
        """Test starting conversation with no agents."""
        sample_room.agents = []
        mock_db.query.return_value.filter.return_value.first.return_value = sample_room
        
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        
        with pytest.raises(ValueError, match="Room has no agents"):
            await orchestrator.start_conversation()
    
    @pytest.mark.asyncio
    async def test_start_conversation_already_finished(self, mock_db, sample_room):
        """Test starting conversation that is already finished."""
        sample_room.status = "finished"
        mock_db.query.return_value.filter.return_value.first.return_value = sample_room
        
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        
        with pytest.raises(ValueError, match="already finished"):
            await orchestrator.start_conversation()
    
    @pytest.mark.asyncio
    async def test_start_conversation_max_rounds_reached(self, mock_db, sample_room, sample_agents):
        """Test conversation stopping when max rounds reached."""
        sample_room.agents = sample_agents
        sample_room.max_rounds = 2
        sample_room.current_rounds = 0
        
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = sample_room
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        # Mock save_message
        mock_msg = MagicMock()
        mock_msg.id = 1
        mock_msg.created_at = datetime.utcnow()
        
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        
        # Mock methods
        orchestrator._save_message = AsyncMock(return_value=mock_msg)
        orchestrator._send_system_message = AsyncMock()
        
        # Mock LLM adapter
        with patch('app.services.orchestrator.get_llm_adapter') as mock_get_adapter:
            mock_adapter = AsyncMock()
            mock_adapter.generate = AsyncMock(return_value="Response")
            mock_get_adapter.return_value = mock_adapter
            
            # Mock sleep to speed up test
            with patch('asyncio.sleep', new_callable=AsyncMock):
                await orchestrator.start_conversation()
        
        # Verify room was set to finished
        assert sample_room.status == "finished"
        assert sample_room.current_rounds == 2
    
    @pytest.mark.asyncio
    async def test_start_conversation_stop_requested(self, mock_db, sample_room, sample_agents):
        """Test conversation stopping when stop is requested."""
        sample_room.agents = sample_agents
        
        mock_db.query.return_value.filter.return_value.first.return_value = sample_room
        
        orchestrator = ChatOrchestrator(room_id=1, db=mock_db)
        orchestrator._stop_requested = True
        orchestrator._send_system_message = AsyncMock()
        
        await orchestrator.start_conversation()
        
        # Room should be marked as finished
        assert sample_room.status == "finished"
