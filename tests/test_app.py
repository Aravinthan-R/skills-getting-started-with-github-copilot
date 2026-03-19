def test_get_activities_returns_initial_activities(client):
    res = client.get("/activities")
    assert res.status_code == 200
    json_data = res.json()
    assert "Chess Club" in json_data
    assert "Programming Class" in json_data
    assert "Gym Class" in json_data


def test_signup_for_activity_adds_participant(client):
    res = client.post("/activities/Chess Club/signup", params={"email": "alice@mergington.edu"})
    assert res.status_code == 200
    assert "Signed up alice@mergington.edu" in res.json()["message"]

    activities = client.get("/activities").json()
    assert "alice@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_fails_400(client):
    client.post("/activities/Chess Club/signup", params={"email": "alice@mergington.edu"})
    res = client.post("/activities/Chess Club/signup", params={"email": "alice@mergington.edu"})
    assert res.status_code == 400
    assert res.json()["detail"] == "Student already signed up"


def test_signup_beyond_capacity_fails_409(client):
    # Use an activity with small capacity for deterministic test.
    # Temporarily create a fresh activity.
    from src.app import activities

    activities["Test Capacity"] = {
        "description": "Temp capacity test",
        "schedule": "Now",
        "max_participants": 2,
        "participants": [],
    }

    client.post("/activities/Test Capacity/signup", params={"email": "a@x.com"})
    client.post("/activities/Test Capacity/signup", params={"email": "b@x.com"})
    res = client.post("/activities/Test Capacity/signup", params={"email": "c@x.com"})

    assert res.status_code == 409
    assert res.json()["detail"] == "Activity is full"


def test_remove_participant_removes_email(client):
    client.post("/activities/Chess Club/signup", params={"email": "bob@mergington.edu"})
    res = client.delete("/activities/Chess Club/participants/bob@mergington.edu")
    assert res.status_code == 200
    assert "Removed bob@mergington.edu" in res.json()["message"]

    activities = client.get("/activities").json()
    assert "bob@mergington.edu" not in activities["Chess Club"]["participants"]


def test_remove_nonexistent_participant_404(client):
    res = client.delete("/activities/Chess Club/participants/not-in-list@mergington.edu")
    assert res.status_code == 404
    assert res.json()["detail"] == "Participant not found"
