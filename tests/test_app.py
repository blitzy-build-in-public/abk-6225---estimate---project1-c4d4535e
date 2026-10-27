"""Tests for the app module: the greeting page and the JSON route."""

import pytest

from app import app


@pytest.fixture
def client():
    """Return a test client for the application."""
    # A view that raises then surfaces as a test failure, not a generic 500.
    app.config["TESTING"] = True
    return app.test_client()


def test_page_without_name_shows_world(client):
    """A request for the page with no name renders the default greeting."""
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<h1>Hello, World!</h1>" in body
    assert 'role="alert"' not in body


def test_page_with_name_shows_personalised_greeting(client):
    """A name in the query string is greeted on the page."""
    response = client.get("/?name=Ada")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<h1>Hello, Ada!</h1>" in body


@pytest.mark.parametrize("name", ["", "   ", " " * 51])
def test_page_shows_world_for_blank_or_whitespace_name(client, name):
    """A blank or whitespace-only name means no name, at any length."""
    response = client.get("/", query_string={"name": name})
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "<h1>Hello, World!</h1>" in body
    assert 'role="alert"' not in body


def test_page_accepts_name_of_fifty_characters(client):
    """A name of exactly the length limit is greeted in full."""
    name = "a" * 50
    response = client.get("/", query_string={"name": name})
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert f"<h1>Hello, {name}!</h1>" in body
    assert 'role="alert"' not in body


def test_page_rejects_over_long_name(client):
    """An over-long name shows the error, keeps the default greeting and is
    not echoed back into the page."""
    name = "a" * 51
    response = client.get("/", query_string={"name": name})
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Name must be 50 characters or fewer." in body
    assert "<h1>Hello, World!</h1>" in body
    assert name not in body


def test_page_escapes_html_and_script_characters(client):
    """HTML and script characters in the name render as escaped text."""
    script = "<script>alert(1)</script>"
    response = client.get("/", query_string={"name": script})
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
    assert "<script>" not in body


def test_api_without_name_returns_world_json(client):
    """A request for the greeting API with no name returns the default."""
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json == {"message": "Hello, World!"}


def test_api_with_name_returns_personalised_json(client):
    """A name in the query string is greeted by the API."""
    response = client.get("/api/hello?name=Ada")
    assert response.status_code == 200
    assert response.json == {"message": "Hello, Ada!"}


@pytest.mark.parametrize("name", ["", "   ", " " * 51])
def test_api_shows_world_for_blank_or_whitespace_name(client, name):
    """A blank or whitespace-only name means no name, at any length."""
    response = client.get("/api/hello", query_string={"name": name})
    assert response.status_code == 200
    assert response.json == {"message": "Hello, World!"}


def test_api_accepts_name_of_fifty_characters(client):
    """A name of exactly the length limit is greeted in full."""
    name = "a" * 50
    response = client.get("/api/hello", query_string={"name": name})
    assert response.status_code == 200
    assert response.json == {"message": f"Hello, {name}!"}


def test_api_rejects_over_long_name(client):
    """An over-long name is rejected with the error and no greeting."""
    name = "a" * 51
    response = client.get("/api/hello", query_string={"name": name})
    assert response.status_code == 400
    assert response.json == {"error": "Name must be 50 characters or fewer."}
    assert "message" not in response.json


def test_api_returns_html_characters_as_data(client):
    """HTML and script characters travel as JSON data, not as markup."""
    script = "<script>alert(1)</script>"
    response = client.get("/api/hello", query_string={"name": script})
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.json == {"message": f"Hello, {script}!"}


def test_unknown_route_returns_404(client):
    """An unmatched path returns the fixed plain-text not-found message."""
    response = client.get("/does-not-exist")
    body = response.get_data(as_text=True)
    assert response.status_code == 404
    assert response.mimetype == "text/plain"
    assert "404 Not Found: the requested page does not exist." in body


def test_unsupported_method_returns_405(client):
    """An unsupported method returns the fixed plain-text 405 message."""
    response = client.post("/")
    body = response.get_data(as_text=True)
    assert response.status_code == 405
    assert response.mimetype == "text/plain"
    assert (
        "405 Method Not Allowed: that method is not supported for this route."
        in body
    )
