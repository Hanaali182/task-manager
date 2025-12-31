import os
import time
import requests
import pytest


@pytest.mark.integration
def test_live_homepage():
    """
    Integration test: call the running service over HTTP.
    We assert HTTP 200 and HTML content-type, which verifies the
    containerized app is reachable and serving web content.
    """
    url = os.getenv("LIVE_URL", "http://localhost:5000")
    time.sleep(2)  # small wait to ensure container is accepting connections
    r = requests.get(url, timeout=5)

    # Service must be up
    assert r.status_code == 200, f"Unexpected status: {r.status_code}"

    # It must serve web/html responses (content-type header or body looks like HTML)
    ct = (r.headers.get("Content-Type") or "").lower()
    assert "text/html" in ct or "<!doctype html>" in r.text.lower() or "<html" in r.text.lower(), (
        f"Unexpected content-type/body. Content-Type: {ct!r}, sample body: {r.text[:200]!r}"
    )
