
# tests/test_unit_routes.py
from app import app, demo_function_for_lint


def test_home_message_constant():
    msg = app.config.get("HOMEPAGE_MESSAGE", "")
    assert "DevOps CI/CD" in msg


def test_demo_function_for_lint():
    assert demo_function_for_lint() == "lint demo"
