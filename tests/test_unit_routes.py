
from app import app

def test_home_message_constant():
    assert "DevOps CI/CD" in app.config.get("HOMEPAGE_MESSAGE", "")
