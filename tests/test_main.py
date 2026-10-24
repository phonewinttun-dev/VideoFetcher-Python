from fastapi.testclient import TestClient


def test_root_html_template(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "VideoFetcher" in resp.text
    assert "Universal Media Downloader" in resp.text
    assert "style.css" in resp.text
    assert "Easily download Instagram Reels, YouTube Shorts, TikTok and Audio with single-click." in resp.text
    assert "300 MB" in resp.text
    # Verify supported platform brands
    assert "YouTube" in resp.text
    assert "Facebook" in resp.text
    assert "Instagram" in resp.text
    assert "TikTok" in resp.text
    assert "X" in resp.text


def test_static_assets_serving(client: TestClient) -> None:
    # Test CSS serving
    css_resp = client.get("/static/css/style.css")
    assert css_resp.status_code == 200
    assert len(css_resp.text) > 0

    # Test JS serving
    js_resp = client.get("/static/js/app.js")
    assert js_resp.status_code == 200
    assert "VideoFetcher Client Application" in js_resp.text
    assert "PLATFORMS" in js_resp.text
    assert "getPlatformInfo" in js_resp.text

    # Test Manifest serving
    manifest_resp = client.get("/static/manifest.json")
    assert manifest_resp.status_code == 200
    assert manifest_resp.json()["name"] == "VideoFetcher"


def test_health_check(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
