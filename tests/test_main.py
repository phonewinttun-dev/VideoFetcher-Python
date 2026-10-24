from fastapi.testclient import TestClient


def test_root_html_template(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "VideoFetcher" in resp.text
    assert "Universal Media Downloader" in resp.text
    assert "style.css" in resp.text


def test_static_assets_serving(client: TestClient) -> None:
    # Test CSS serving
    css_resp = client.get("/static/css/style.css")
    assert css_resp.status_code == 200
    assert len(css_resp.text) > 0

    # Test JS serving
    js_resp = client.get("/static/js/app.js")
    assert js_resp.status_code == 200
    assert "VideoFetcher Client Application" in js_resp.text

    # Test Manifest serving
    manifest_resp = client.get("/static/manifest.json")
    assert manifest_resp.status_code == 200
    assert manifest_resp.json()["name"] == "VideoFetcher"


def test_health_check(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
