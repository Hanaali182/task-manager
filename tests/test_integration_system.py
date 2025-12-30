
import os
import requests


def test_live_homepage():
    # Use LIVE_URL from environment or default to localhost
    url = os.getenv("LIVE_URL", "http://localhost:5000")
    response = requests.get(url, timeout=5)

    # Check homepage loads successfully
    assert response.status_code == 200

    # Check that HOMEPAGE_MESSAGE or Flask text is present
    assert "DevOps CI/CD" in response.text or "Flask" in response.text
