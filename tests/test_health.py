def test_health_endpoint(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body


def test_ready_endpoint_reports_checks(client) -> None:
    response = client.get("/ready")
    assert response.status_code in (200, 503)
    body = response.json()
    assert "checks" in body
    assert "database" in body["checks"]
    assert "ml_model" in body["checks"]
