#!/usr/bin/env python3
"""
app.py
Flask web front-end for the password checker. This is a thin layer over
the same strength.py and breach_check.py modules the CLI (main.py) uses —
no security logic is duplicated between the two interfaces.

Run with:
    python app.py
Then open http://127.0.0.1:5000 in a browser.
"""

from flask import Flask, render_template, request, jsonify

from strength import analyze_password, load_common_passwords
from breach_check import check_password_breach

app = Flask(__name__)

# Loaded once at startup rather than per-request — the wordlist is static.
COMMON_PASSWORDS = load_common_passwords("common_passwords.txt")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/strength", methods=["POST"])
def api_strength():
    """Offline check — runs on every keystroke, no network call involved."""
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    if not password:
        return jsonify({"error": "No password provided"}), 400
    return jsonify(analyze_password(password, COMMON_PASSWORDS))


@app.route("/api/breach", methods=["POST"])
def api_breach():
    """
    Online check — only runs when the user explicitly clicks the button,
    not on every keystroke. This is deliberate: it respects the HIBP API's
    rate limits and avoids sending network requests for every character
    typed. See breach_check.py for the k-anonymity model this uses.
    """
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")
    if not password:
        return jsonify({"error": "No password provided"}), 400
    return jsonify(check_password_breach(password))


if __name__ == "__main__":
    # debug=True is for local development only — never run this in production
    # or expose it beyond localhost with debug mode on.
    app.run(debug=True, port=5000)
