import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Force SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///./test_homebox.db"

import pytest
from fastapi.testclient import TestClient

from database import Base, engine
from main import app


@pytest.fixture(autouse=True)
def reset_db():
    """Recreate all tables before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


class TestHealth:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestHouseholds:
    def test_create_household(self):
        r = client.post("/households", json={
            "household_name": "Test Home",
            "your_name": "Alice",
        })
        data = r.json()
        assert r.status_code == 200
        assert data["household_name"] == "Test Home"
        assert data["your_name"] == "Alice"
        assert len(data["join_code"]) == 6
        assert len(data["token"]) == 32

    def test_create_household_empty_name(self):
        r = client.post("/households", json={
            "household_name": "",
            "your_name": "Alice",
        })
        assert "error" in r.json()

    def test_join_household(self):
        # Create first
        r1 = client.post("/households", json={
            "household_name": "Test Home",
            "your_name": "Alice",
        })
        code = r1.json()["join_code"]

        # Join
        r2 = client.post("/households/join", json={
            "join_code": code,
            "your_name": "Bob",
        })
        data = r2.json()
        assert data["your_name"] == "Bob"
        assert data["join_code"] == code
        assert data["token"] != r1.json()["token"]

    def test_join_bad_code(self):
        r = client.post("/households/join", json={
            "join_code": "XXXXXX",
            "your_name": "Bob",
        })
        assert "error" in r.json()


def _create_and_get_token() -> str:
    r = client.post("/households", json={
        "household_name": "Test Home",
        "your_name": "Alice",
    })
    return r.json()["token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestItems:
    def test_add_item(self):
        token = _create_and_get_token()
        r = client.post("/items", json={"raw_input": "the drill is in the garage"}, headers=_auth(token))
        data = r.json()
        assert data["message"] == "Got it. drill is in garage."
        assert data["item"]["name"] == "drill"
        assert data["item"]["location"] == "garage"
        assert data["item"]["category"] == "Tools"

    def test_add_item_no_auth(self):
        r = client.post("/items", json={"raw_input": "drill in garage"})
        assert "error" in r.json()

    def test_add_item_bad_input(self):
        token = _create_and_get_token()
        r = client.post("/items", json={"raw_input": "hello"}, headers=_auth(token))
        assert "error" in r.json()

    def test_search_items(self):
        token = _create_and_get_token()
        client.post("/items", json={"raw_input": "drill in garage"}, headers=_auth(token))
        client.post("/items", json={"raw_input": "hammer in garage"}, headers=_auth(token))
        client.post("/items", json={"raw_input": "plates in kitchen"}, headers=_auth(token))

        r = client.get("/items/search", params={"q": "drill"}, headers=_auth(token))
        data = r.json()
        assert data["query"] == "drill"
        assert len(data["results"]) >= 1
        assert data["results"][0]["name"] == "drill"

    def test_search_by_location(self):
        token = _create_and_get_token()
        client.post("/items", json={"raw_input": "drill in garage"}, headers=_auth(token))
        client.post("/items", json={"raw_input": "hammer in garage"}, headers=_auth(token))

        r = client.get("/items/search", params={"q": "garage"}, headers=_auth(token))
        assert len(r.json()["results"]) == 2

    def test_list_items(self):
        token = _create_and_get_token()
        client.post("/items", json={"raw_input": "drill in garage"}, headers=_auth(token))
        client.post("/items", json={"raw_input": "plates in kitchen"}, headers=_auth(token))

        r = client.get("/items", headers=_auth(token))
        data = r.json()
        assert data["count"] == 2

    def test_list_items_filter_category(self):
        token = _create_and_get_token()
        client.post("/items", json={"raw_input": "drill in garage"}, headers=_auth(token))
        client.post("/items", json={"raw_input": "plates in kitchen"}, headers=_auth(token))

        r = client.get("/items", params={"category": "Tools"}, headers=_auth(token))
        assert r.json()["count"] == 1
        assert r.json()["items"][0]["name"] == "drill"

    def test_list_items_filter_location(self):
        token = _create_and_get_token()
        client.post("/items", json={"raw_input": "drill in garage"}, headers=_auth(token))
        client.post("/items", json={"raw_input": "hammer in garage"}, headers=_auth(token))
        client.post("/items", json={"raw_input": "plates in kitchen"}, headers=_auth(token))

        r = client.get("/items", params={"location": "garage"}, headers=_auth(token))
        assert r.json()["count"] == 2

    def test_delete_item(self):
        token = _create_and_get_token()
        r1 = client.post("/items", json={"raw_input": "drill in garage"}, headers=_auth(token))
        item_id = r1.json()["item"]["id"]

        r2 = client.delete(f"/items/{item_id}", headers=_auth(token))
        assert "Deleted" in r2.json()["message"]

        # Verify it's gone
        r3 = client.get("/items", headers=_auth(token))
        assert r3.json()["count"] == 0

    def test_delete_item_not_found(self):
        token = _create_and_get_token()
        r = client.delete("/items/9999", headers=_auth(token))
        assert "error" in r.json()


class TestMultiUser:
    def test_shared_household(self):
        # Alice creates household
        r1 = client.post("/households", json={
            "household_name": "Test Home",
            "your_name": "Alice",
        })
        alice_token = r1.json()["token"]
        code = r1.json()["join_code"]

        # Bob joins
        r2 = client.post("/households/join", json={
            "join_code": code,
            "your_name": "Bob",
        })
        bob_token = r2.json()["token"]

        # Alice adds an item
        client.post("/items", json={"raw_input": "drill in garage"}, headers=_auth(alice_token))

        # Bob adds an item
        client.post("/items", json={"raw_input": "hammer in shed"}, headers=_auth(bob_token))

        # Both can see both items
        r_alice = client.get("/items", headers=_auth(alice_token))
        r_bob = client.get("/items", headers=_auth(bob_token))
        assert r_alice.json()["count"] == 2
        assert r_bob.json()["count"] == 2

    def test_separate_households(self):
        # Alice's household
        r1 = client.post("/households", json={
            "household_name": "Alice Home",
            "your_name": "Alice",
        })
        alice_token = r1.json()["token"]

        # Carol's household
        r2 = client.post("/households", json={
            "household_name": "Carol Home",
            "your_name": "Carol",
        })
        carol_token = r2.json()["token"]

        # Each adds an item
        client.post("/items", json={"raw_input": "drill in garage"}, headers=_auth(alice_token))
        client.post("/items", json={"raw_input": "hammer in shed"}, headers=_auth(carol_token))

        # Each only sees their own
        assert client.get("/items", headers=_auth(alice_token)).json()["count"] == 1
        assert client.get("/items", headers=_auth(carol_token)).json()["count"] == 1
