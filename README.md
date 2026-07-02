# Password Strength & Breach Checker

A beginner cybersecurity project that scores password strength offline and
checks for real-world breach exposure online — without ever sending your
actual password over the network.

## What it does

1. **Strength analysis** — scores a password 0-100 based on:
   - Length
   - Character variety (upper/lower/digits/symbols)
   - Entropy (bits of randomness — a rough measure of brute-force resistance)
   - Whether it appears in a list of 10,000 known common/leaked passwords
   - Predictable patterns: sequential runs (`abcd`, `4321`), repeated characters (`aaaa`),
     and keyboard walks (`qwerty`, `1qaz2wsx`)

2. **Breach check** — checks the password against the
   [Have I Been Pwned](https://haveibeenpwned.com/Passwords) database of
   billions of breached credentials, using the **k-anonymity model**:
   - The password is SHA-1 hashed *locally*
   - Only the first **5 characters** of that hash are sent to the API
   - The API returns every hash suffix sharing that prefix (hundreds of them)
   - The match is found *locally* by comparing the full hash
   - Result: the API never learns the actual password or its full hash

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Prompts for a password with hidden input (recommended)
python main.py

# Pass a password directly (visible in shell history — fine for testing, not real passwords)
python main.py -p "mypassword123"

# Skip the online breach check (fully offline)
python main.py --no-breach-check

# Use a different wordlist
python main.py --wordlist custom_list.txt
```

## Web app (Flask)

There's also a browser version with a live strength meter, built on top of
the exact same `strength.py` and `breach_check.py` modules the CLI uses —
no security logic is duplicated between the two interfaces.

```bash
python app.py
```

Then open **http://127.0.0.1:5000** in a browser. Type a password to see the
strength readout update live (debounced, checked locally on your machine as
you type). Click "Run Field Inspection" to run the breach check — this is a
separate explicit action rather than firing on every keystroke, both to
respect the HIBP API's rate limits and to make clear when a network request
is actually being made.

`app.py` runs in Flask's debug dev server, which is fine for local use but
should never be exposed beyond `127.0.0.1` or run in production as-is.

## Project structure

```
password_checker/
├── main.py               # CLI entry point
├── app.py                # Flask web app entry point
├── strength.py           # Offline scoring: length, entropy, patterns, common list
├── breach_check.py       # HIBP k-anonymity breach lookup
├── templates/
│   └── index.html        # Web UI markup
├── static/
│   ├── style.css         # Web UI styling
│   └── script.js         # Live strength check + breach check logic
├── common_passwords.txt  # 10,000 common/leaked passwords (from SecLists)
├── requirements.txt
└── README.md
```

## Concepts this project demonstrates

Useful talking points for a resume line or interview:

- **Entropy & keyspace estimation** — understanding why length and character
  variety matter mathematically, not just intuitively.
- **Password cracking patterns** — dictionary attacks, keyboard walks,
  and why "P@ssw0rd!" is weaker than it looks (attackers check leetspeak
  substitutions first).
- **Cryptographic hashing (SHA-1)** and why hashing ≠ encryption.
- **k-anonymity** — a real privacy-preserving technique used in production
  security tooling (this is the actual method HIBP, Chrome, and 1Password
  use for breach checks).
- **API integration** and handling network failures gracefully.

## Ideas to extend this project

Good next steps if you want to keep building on it:

- **Batch mode**: read a list of passwords from a file and output a CSV report —
  useful for auditing a team's password habits (with consent).
- **zxcvbn-style scoring**: research Dropbox's `zxcvbn` algorithm and compare
  its approach to the simple scoring used here.
- **Salting demo**: add a companion script that shows how salting defeats
  precomputed rainbow tables, using `bcrypt` or `hashlib.pbkdf2_hmac`.
- **Email breach check**: add the HIBP breach-by-account-email endpoint (requires
  a free API key) to check if an email address itself has been in a breach.
- **Tests**: write `pytest` unit tests for `strength.py` — this is an easy way
  to show testing skills alongside security skills.
- **Containerize it**: add a `Dockerfile` so it's portable — a nice small
  DevOps/security crossover skill to show off.

## Notes

- Never test this against your real, currently-in-use passwords over an
  untrusted network. For learning, use throwaway example passwords.
- The bundled `common_passwords.txt` is the public SecLists "10k most common
  passwords" list, used widely in security tooling and CTFs.
