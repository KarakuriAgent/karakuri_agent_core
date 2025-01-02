from datetime import datetime
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch

from app.main import app
from app.schemas.status import AgentStatus, AgentStatusConfig
from app.schemas.schedule import AgentScheduleConfig

client = TestClient(app)

# Mock data
MOCK_API_KEY = "test-api-key"
MOCK_AGENT_ID = "1"
MOCK_STATUS = AgentStatusConfig(
    current_status=AgentStatus.AVAILABLE,
    last_status_change=datetime.now().isoformat(),
)
MOCK_SCHEDULE_CONFIG = AgentScheduleConfig()


@pytest.fixture
def mock_agent():
    with patch("app.core.agent_manager.AgentManager.get_agent") as mock:
        mock.return_value.status = MOCK_STATUS
        mock.return_value.schedule = MOCK_SCHEDULE_CONFIG
        yield mock


def test_get_agent_status(mock_agent):
    """Test getting agent status"""
    response = client.get(
        f"/v1/agents/{MOCK_AGENT_ID}/status",
        headers={"api-key": MOCK_API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == AgentStatus.AVAILABLE


def test_update_agent_status(mock_agent):
    """Test updating agent status"""
    new_status = AgentStatus.WORKING
    response = client.put(
        f"/v1/agents/{MOCK_AGENT_ID}/status",
        headers={"api-key": MOCK_API_KEY},
        json=new_status,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == new_status


def test_get_agent_schedule(mock_agent):
    """Test getting agent schedule"""
    with patch(
        "app.core.schedule_service.ScheduleService._schedule_cache"
    ) as mock_cache:
        mock_schedule = {
            "date": datetime.now().date().isoformat(),
            "items": [],
            "generated_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
        }
        mock_cache.get.return_value = mock_schedule
        response = client.get(
            f"/v1/agents/{MOCK_AGENT_ID}/schedule",
            headers={"api-key": MOCK_API_KEY},
        )
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "items" in data


def test_get_agent_availability(mock_agent):
    """Test getting agent availability"""
    response = client.get(
        f"/v1/agents/{MOCK_AGENT_ID}/availability",
        headers={"api-key": MOCK_API_KEY},
    )
    assert response.status_code == 200
    data = response.json()
    assert "chat" in data
    assert "voice" in data
    assert "video" in data
    assert isinstance(data["chat"], bool)
    assert isinstance(data["voice"], bool)
    assert isinstance(data["video"], bool)


def test_agent_not_found():
    """Test error handling when agent is not found"""
    with patch("app.core.agent_manager.AgentManager.get_agent") as mock:
        mock.side_effect = KeyError("Agent not found")
        endpoints = [
            "/v1/agents/999/status",
            "/v1/agents/999/schedule",
            "/v1/agents/999/availability",
        ]
        for endpoint in endpoints:
            response = client.get(
                endpoint,
                headers={"api-key": MOCK_API_KEY},
            )
            assert response.status_code == 404
            assert response.json()["detail"] == "Agent not found"


def test_schedule_not_found(mock_agent):
    """Test error handling when schedule is not found"""
    with patch(
        "app.core.schedule_service.ScheduleService._schedule_cache"
    ) as mock_cache:
        mock_cache.get.return_value = None
        response = client.get(
            f"/v1/agents/{MOCK_AGENT_ID}/schedule",
            headers={"api-key": MOCK_API_KEY},
        )
        assert response.status_code == 404
        assert "Schedule not found" in response.json()["detail"]
