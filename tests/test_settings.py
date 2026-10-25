from fastapi.testclient import TestClient


def test_get_version(client: TestClient) -> None:
    resp = client.get("/api/settings/version")
    assert resp.status_code == 200
    data = resp.json()
    assert data["app_name"] == "VideoFetcher"
    assert isinstance(data["ytdlp_version"], str) and len(data["ytdlp_version"]) > 0
    assert isinstance(data["python_version"], str) and len(data["python_version"]) > 0
    assert isinstance(data["ffmpeg_available"], bool)


def test_validate_cookies_valid(client: TestClient, valid_netscape_cookie: str) -> None:
    resp = client.post(
        "/api/settings/cookies/validate",
        json={"cookies": valid_netscape_cookie},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["entries_count"] == 2
    assert "youtube.com" in data["domains"]
    assert "tiktok.com" in data["domains"]


def test_validate_cookies_empty(client: TestClient) -> None:
    resp = client.post(
        "/api/settings/cookies/validate",
        json={"cookies": "   "},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert data["entries_count"] == 0


def test_validate_cookies_invalid_format(client: TestClient) -> None:
    resp = client.post(
        "/api/settings/cookies/validate",
        json={"cookies": "just some random text without tabs"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is False
    assert data["entries_count"] == 0
