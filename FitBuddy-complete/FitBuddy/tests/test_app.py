def sample_payload():
    return {
        "username": "Alex",
        "user_id": "alex01",
        "age": 28,
        "weight": 72,
        "goal": "muscle gain",
        "intensity": "medium",
    }


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_create_plan(client):
    response = client.post("/api/plans", json=sample_payload())
    assert response.status_code == 201

    data = response.json()
    assert data["plan"]["user_id"] == "alex01"
    assert len(__import__("json").loads(data["plan"]["original_plan"])["days"]) == 7


def test_duplicate_user_rejected(client):
    assert client.post("/api/plans", json=sample_payload()).status_code == 201
    response = client.post("/api/plans", json=sample_payload())
    assert response.status_code == 409


def test_feedback_update(client):
    assert client.post("/api/plans", json=sample_payload()).status_code == 201

    response = client.post(
        "/api/plans/alex01/feedback",
        json={"feedback": "Add more cardio and include an extra recovery day."},
    )
    assert response.status_code == 200
    assert response.json()["plan"]["updated_plan"] is not None
    assert response.json()["plan"]["feedback"].startswith("Add more cardio")


def test_list_and_delete(client):
    assert client.post("/api/plans", json=sample_payload()).status_code == 201

    response = client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.delete("/api/users/alex01")
    assert response.status_code == 200

    response = client.get("/api/users/alex01")
    assert response.status_code == 404


def test_validation(client):
    bad = sample_payload()
    bad["age"] = 5

    response = client.post("/api/plans", json=bad)
    assert response.status_code == 422
