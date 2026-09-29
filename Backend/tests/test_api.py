import base64
from datetime import date

import bcrypt
import pytest
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.main import create_app
from app.service.game_service import calculate_result
from tests.fake_mongo import FakeDatabase

SECRET = base64.b64encode(b"x" * 32).decode()
ORIGIN = "http://localhost:5500"
PASSWORD = "Passw0rd$"


@pytest.fixture
def db():
    return FakeDatabase()


@pytest.fixture
def client(db):
    settings = Settings(mongodb_uri="mongodb://unused", jwt_secret=SECRET)
    with TestClient(create_app(settings, db=db), base_url="http://localhost:8080") as c:
        yield c


def register(client, username="Alice", password=PASSWORD):
    return client.post(
        "/auth/register",
        json={"username": username, "password": password, "confirmPassword": password},
    )


def set_target(db, word):
    db.raw["games"].update_many({"status": "IN_PROGRESS"}, {"$set": {"targetWord": word}})


def test_words_are_seeded_once(db, client):
    assert db.raw["words"].count_documents({}) == 20
    doc = db.raw["words"].find_one({"word": "APPLE"})
    assert doc["_class"] == "com.example.guessgame.model.Word"


def test_register_sets_cookie_and_stores_spring_shaped_user(db, client):
    r = register(client)
    assert r.status_code == 200
    assert r.json() == {"token": None, "username": "Alice", "role": "PLAYER"}
    cookie = r.headers["set-cookie"]
    assert cookie.startswith("token=")
    for part in ("HttpOnly", "Max-Age=3600", "Path=/", "SameSite=lax"):
        assert part in cookie
    doc = db.raw["users"].find_one({"username": "Alice"})
    assert set(doc) == {"_id", "username", "passwordHash", "role", "_class"}
    assert doc["passwordHash"].startswith("$2a$10$")


@pytest.mark.parametrize(
    "username,password,confirm,message",
    [
        ("abc", PASSWORD, PASSWORD, "username should have a minimum of 5 characters"),
        ("alice", PASSWORD, PASSWORD, "Username must contain atleast one upper and lower letters"),
        ("Alice", "Ab1$", "Ab1$", "Password should have a minimum length of 5"),
        ("Alice", "Password1", "Password1", "Password should have atleast one lower case letter"),
        ("Alice", PASSWORD, "other", "Passwords dont match"),
    ],
)
def test_register_validation_returns_plain_text_400(client, username, password, confirm, message):
    r = client.post(
        "/auth/register",
        json={"username": username, "password": password, "confirmPassword": confirm},
    )
    assert r.status_code == 400
    assert r.headers["content-type"].startswith("text/plain")
    assert r.text.startswith(message)


def test_duplicate_user(client):
    register(client)
    r = register(client)
    assert (r.status_code, r.text) == (400, "Username already exists try logging in")


def test_login_logout_me(client):
    register(client)
    client.cookies.clear()
    assert client.get("/auth/me").status_code == 403

    r = client.post("/auth/login", json={"username": "Alice", "password": "wrong"})
    assert (r.status_code, r.text) == (400, "Username or password is incorrect")
    r = client.post("/auth/login", json={"username": "Nobody", "password": "x"})
    assert (r.status_code, r.text) == (400, "User not found please register")

    r = client.post("/auth/login", json={"username": "Alice", "password": PASSWORD})
    assert r.status_code == 200
    assert client.get("/auth/me").json() == {"token": None, "username": "Alice", "role": "PLAYER"}

    r = client.post("/auth/logout")
    assert r.status_code == 204
    assert "Max-Age=0" in r.headers["set-cookie"]
    assert client.get("/auth/me").status_code == 403


def test_login_accepts_spring_bcrypt_hash(db, client):
    # Hash with the $2a$ prefix Spring's BCryptPasswordEncoder writes.
    h = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(10, prefix=b"2a")).decode()
    db.raw["users"].insert_one({"username": "OldUser", "passwordHash": h, "role": "PLAYER"})
    r = client.post("/auth/login", json={"username": "OldUser", "password": PASSWORD})
    assert r.status_code == 200


def test_tampered_cookie_is_forbidden(client):
    client.cookies.set("token", "not-a-jwt")
    assert client.get("/auth/me").status_code == 403
    assert client.post("/games/start").status_code == 403


def test_full_game_win(db, client):
    register(client)
    r = client.post("/games/guess", json={"guess": "APPLE"})
    assert (r.status_code, r.text) == (400, "Please start a game")

    r = client.post("/games/start")
    assert r.status_code == 200
    assert r.json() == {"guesses": [], "results": [], "status": "IN_PROGRESS"}
    game = db.raw["games"].find_one({})
    assert set(game) == {"_id", "playerId", "targetWord", "guesses", "status", "createdAt", "_class"}
    set_target(db, "APPLE")

    assert client.post("/games/guess", json={"guess": "abc"}).text == "Word length should be equal to 5"
    assert client.post("/games/guess", json={"guess": "ZZZZZ"}).text == "Word is not in the word list"

    r = client.post("/games/guess", json={"guess": " grape "})
    assert r.json() == {"results": ["GREY", "GREY", "ORANGE", "ORANGE", "GREEN"], "status": "IN_PROGRESS"}

    r = client.get("/games/current")
    assert r.json() == {
        "guesses": ["GRAPE"],
        "results": [["GREY", "GREY", "ORANGE", "ORANGE", "GREEN"]],
        "status": "IN_PROGRESS",
    }
    # Starting again resumes the same game.
    assert client.post("/games/start").json()["guesses"] == ["GRAPE"]

    r = client.post("/games/guess", json={"guess": "apple"})
    assert r.json() == {"results": ["GREEN"] * 5, "status": "WON"}
    assert client.get("/games/current").json() == {"guesses": [], "results": [], "status": "IN_PROGRESS"}


def test_game_lost_after_five_and_daily_limit(db, client):
    register(client)
    for _ in range(3):
        client.post("/games/start")
        set_target(db, "APPLE")
        statuses = [client.post("/games/guess", json={"guess": "STONE"}).json()["status"] for _ in range(5)]
        assert statuses == ["IN_PROGRESS"] * 4 + ["LOST"]
    r = client.post("/games/start")
    assert (r.status_code, r.text) == (400, "Limits exceeded ! try again tomorrow!")


def test_admin_routes(db, client):
    register(client)
    client.post("/games/start")
    set_target(db, "APPLE")
    client.post("/games/guess", json={"guess": "APPLE"})
    player_id = db.raw["users"].find_one({"username": "Alice"})["_id"]
    today = date.today().isoformat()

    assert client.get(f"/admin/daily-report?date={today}").status_code == 403

    db.raw["users"].update_one({"username": "Alice"}, {"$set": {"role": "ADMIN"}})
    r = client.get(f"/admin/daily-report?date={today}")
    assert r.json() == {"noOfUsers": 1, "noOfCorrectGuesses": 1}
    r = client.get(f"/admin/user-report/{player_id}?date={today}")
    assert r.json() == {"date": today, "noOfWordsTried": 1, "noOfCorrectGuesses": 1}
    r = client.get("/admin/daily-report?date=2000-01-01")
    assert r.json() == {"noOfUsers": 0, "noOfCorrectGuesses": 0}
    assert client.get("/admin/daily-report").status_code == 400
    # Admins may play too, like hasAnyRole("PLAYER", "ADMIN").
    assert client.get("/games/current").status_code == 200


def test_cors_preflight_and_credentials(client):
    r = client.options(
        "/auth/login",
        headers={"Origin": ORIGIN, "Access-Control-Request-Method": "POST",
                 "Access-Control-Request-Headers": "content-type"},
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == ORIGIN
    assert r.headers["access-control-allow-credentials"] == "true"
    r = client.get("/auth/me", headers={"Origin": ORIGIN})
    assert r.status_code == 403
    assert r.headers["access-control-allow-origin"] == ORIGIN
    r = client.options(
        "/auth/login",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert r.status_code == 400


@pytest.mark.parametrize(
    "target,guess,expected",
    [
        ("APPLE", "PAPER", ["ORANGE", "ORANGE", "GREEN", "ORANGE", "GREY"]),
        ("ABBEY", "BABES", ["ORANGE", "ORANGE", "GREEN", "GREEN", "GREY"]),
        ("CLOUD", "LLAMA", ["GREY", "GREEN", "GREY", "GREY", "GREY"]),
    ],
)
def test_calculate_result_matches_java(target, guess, expected):
    assert [r.value for r in calculate_result(target, guess)] == expected
