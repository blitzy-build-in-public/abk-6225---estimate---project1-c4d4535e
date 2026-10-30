# Hello World Web App

A small Flask app that greets you on a web page and returns the same greeting as JSON.

## Requirements

- Python 3.11 or later.
- Runs on Linux, macOS and Windows with no platform-specific steps.
- No build step and no front-end tooling.

## Install

```bash
pip install -r requirements.txt
```

`requirements.txt` declares two pinned dependencies — Flask 3.1.3 and pytest 9.1.1 — and nothing else.

## Run

```bash
python -m flask --app app run
```

Run it from the repository root, the same directory the install and test commands assume: `--app app` imports the `app` module from the working directory, so the command fails with `Could not import 'app'` from anywhere else.

The app is then served at http://127.0.0.1:5000. No environment variable, configuration file or second command is needed. Open that address in a browser: the page carries a form — a field labelled `Your name` and a `Greet me` submit button — that sends the typed name back to `/` as the `name` query parameter, so the heading reads `Hello, <name>!`.

The development server binds the loopback interface only, so the app is not reachable from the network. Debug mode is deliberately absent from that command: the Werkzeug debugger it would enable lets code be executed through the browser.

## Port override

The port defaults to 5000. To serve on another one, run the module entry point and set `PORT`:

```bash
PORT=5057 python app.py
```

That serves http://127.0.0.1:5057. `PORT` is the only environment variable the application's own code reads, and it applies to this entry point.

The `VAR=value command` prefix above is POSIX shell syntax, which cmd.exe and PowerShell do not implement; each shell sets the same variable with its own syntax. In cmd.exe:

```bat
set PORT=5057
python app.py
```

In PowerShell:

```powershell
$env:PORT="5057"
python app.py
```

Only the way the variable is set differs — the application itself still needs no platform-specific step, so it is the same override on every platform.

The Flask CLI path is different: the CLI resolves its port before it imports the application module, so it never sees `PORT`. Use Flask's own variable there instead:

```bash
FLASK_RUN_PORT=5057 python -m flask --app app run
```

`FLASK_RUN_PORT` is read by the Flask CLI, not by `app.py`. Set it with each shell's own syntax too — in cmd.exe:

```bat
set FLASK_RUN_PORT=5057
python -m flask --app app run
```

and in PowerShell:

```powershell
$env:FLASK_RUN_PORT="5057"
python -m flask --app app run
```

## Test

```bash
pytest
```

Run it from the repository root. The suite passes with no failures, needs no server running and binds no port, because it drives the app through Flask's test client.

## Routes

| Route | Result |
|-------|--------|
| `GET /` | 200, the page showing `Hello, World!` |
| `GET /?name=Ada` | 200, the page showing `Hello, Ada!` |
| `GET /api/hello` | 200, `{"message": "Hello, World!"}` |
| `GET /api/hello?name=Ada` | 200, `{"message": "Hello, Ada!"}` |

```bash
curl -s http://127.0.0.1:5000/
curl -s "http://127.0.0.1:5000/api/hello?name=Ada"
```

Surrounding whitespace is trimmed first, so a name that is empty or all spaces means no name and gets the world greeting. A name longer than 50 characters is rejected: the page shows the message below and keeps its `Hello, World!` heading, and the API answers HTTP 400.

```text
Name must be 50 characters or fewer.
```

```json
{"error": "Name must be 50 characters or fewer."}
```

HTML and script characters in a name are escaped on the page, so they appear as visible text rather than as markup. Submitting

```text
<script>alert(1)</script>
```

renders `&lt;script&gt;alert(1)&lt;/script&gt;` in the heading, with no script element anywhere in the response. On the JSON route those same characters travel as data inside the JSON string.

An unknown route answers 404 with a short plain-text message, and an unsupported method on a known route answers 405.

## Project layout

- `app.py` — the Flask application, its routes and the `PORT` override.
- `templates/index.html` — the greeting page.
- `tests/` — the test suite, run with `pytest`.
- `requirements.txt` — the pinned dependencies.
