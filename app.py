"""The Hello World web app: one greeting page and one JSON greeting route."""

import os

from flask import Flask, jsonify, render_template, request

MAX_NAME_LENGTH = 50
DEFAULT_NAME = "World"
# Fixed text, never built from the submitted value, so a rejection cannot
# echo the name it rejects.
NAME_TOO_LONG_MESSAGE = "Name must be 50 characters or fewer."
NOT_FOUND_MESSAGE = "404 Not Found: the requested page does not exist."
METHOD_NOT_ALLOWED_MESSAGE = (
    "405 Method Not Allowed: that method is not supported for this route."
)
PLAIN_TEXT = {"Content-Type": "text/plain; charset=utf-8"}

# Read once at import; this port applies when this module is run directly, as
# `python app.py`. The Flask CLI resolves its own port before importing the
# module, so it cannot see this value and uses FLASK_RUN_PORT instead.
PORT = int(os.environ.get("PORT", "5000"))

app = Flask(__name__)


def normalise_name(raw: str | None) -> str | None:
    """Return the submitted name trimmed, or None when no name was given."""
    if raw is None:
        return None
    name = raw.strip()
    return name or None


def is_too_long(name: str | None) -> bool:
    """Return True when the normalised name exceeds the length limit."""
    return name is not None and len(name) > MAX_NAME_LENGTH


def greeting_for(name: str | None) -> str:
    """Return the greeting text for the normalised name, or the default one."""
    return f"Hello, {name or DEFAULT_NAME}!"


@app.get("/")
def index():
    """Render the greeting page from the optional name query parameter."""
    name = normalise_name(request.args.get("name"))
    if is_too_long(name):
        return render_template(
            "index.html",
            greeting=greeting_for(None),
            name="",
            error=NAME_TOO_LONG_MESSAGE,
        )
    return render_template(
        "index.html",
        greeting=greeting_for(name),
        name=name or "",
        error=None,
    )


@app.get("/api/hello")
def api_hello():
    """Return the greeting as JSON from the optional name parameter."""
    name = normalise_name(request.args.get("name"))
    if is_too_long(name):
        return jsonify({"error": NAME_TOO_LONG_MESSAGE}), 400
    return jsonify({"message": greeting_for(name)}), 200


@app.errorhandler(404)
def not_found(error):
    """Return the fixed plain-text body and status for an unmatched path."""
    # The three-part form is required: Flask does not adopt a handler's own
    # status code, and a bare string body would be served as text/html.
    return NOT_FOUND_MESSAGE, 404, PLAIN_TEXT


@app.errorhandler(405)
def method_not_allowed(error):
    """Return the fixed plain-text body for an unsupported method."""
    return METHOD_NOT_ALLOWED_MESSAGE, 405, PLAIN_TEXT


if __name__ == "__main__":
    app.run(port=PORT)
