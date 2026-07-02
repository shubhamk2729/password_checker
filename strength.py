"""
strength.py
Analyzes password strength based on length, character variety,
entropy, common patterns, and known common passwords.
"""

import re
import math

# Common keyboard walk patterns — these get cracked instantly regardless
# of length, because attackers check them first.
KEYBOARD_PATTERNS = [
    "qwerty", "asdfgh", "zxcvbn", "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "1qaz2wsx", "qazwsx", "1q2w3e4r", "!qaz@wsx",
]


def has_sequential_chars(password, run_length=4):
    """Detect ascending or descending runs like 'abcd' or '4321'."""
    lower = password.lower()
    for i in range(len(lower) - run_length + 1):
        chunk = lower[i:i + run_length]
        ascending = all(ord(chunk[j + 1]) - ord(chunk[j]) == 1 for j in range(len(chunk) - 1))
        descending = all(ord(chunk[j]) - ord(chunk[j + 1]) == 1 for j in range(len(chunk) - 1))
        if ascending or descending:
            return True
    return False


def has_repeated_chars(password, run_length=4):
    """Detect the same character repeated run_length+ times in a row, e.g. 'aaaa'."""
    for i in range(len(password) - run_length + 1):
        if len(set(password[i:i + run_length])) == 1:
            return True
    return False


def has_keyboard_pattern(password):
    lower = password.lower()
    return any(pattern in lower for pattern in KEYBOARD_PATTERNS)


def calculate_entropy(password):
    """
    Rough Shannon-style entropy estimate: length * log2(character pool size).
    Higher bits = more attempts a brute-force attacker needs on average.
    ~28 bits is weak, ~60+ bits is considered strong for most contexts.
    """
    pool = 0
    if re.search(r'[a-z]', password):
        pool += 26
    if re.search(r'[A-Z]', password):
        pool += 26
    if re.search(r'[0-9]', password):
        pool += 10
    if re.search(r'[^a-zA-Z0-9]', password):
        pool += 32
    if pool == 0:
        return 0.0
    return len(password) * math.log2(pool)


def load_common_passwords(path="common_passwords.txt"):
    """Load a wordlist of known common/breached passwords into a set for fast lookup."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def analyze_password(password, common_passwords=None):
    """
    Score a password from 0-100 and return a rating plus human-readable feedback.
    """
    if common_passwords is None:
        common_passwords = set()

    feedback = []
    score = 0
    length = len(password)

    # --- Length ---
    if length < 8:
        feedback.append("Too short — use at least 12 characters.")
    elif length < 12:
        score += 15
        feedback.append("Decent length, but 12+ characters is safer.")
    elif length < 16:
        score += 25
    else:
        score += 30

    # --- Character variety ---
    variety = sum([
        bool(re.search(r'[a-z]', password)),
        bool(re.search(r'[A-Z]', password)),
        bool(re.search(r'[0-9]', password)),
        bool(re.search(r'[^a-zA-Z0-9]', password)),
    ])

    if variety <= 1:
        feedback.append("Uses only one character type — mix upper/lowercase, numbers, and symbols.")
    elif variety == 2:
        score += 10
        feedback.append("Add more variety: symbols and numbers strengthen a password a lot.")
    elif variety == 3:
        score += 20
    else:
        score += 30

    # --- Known common password ---
    if password.lower() in common_passwords:
        score = min(score, 5)
        feedback.append("This is one of the most commonly leaked passwords — change it immediately.")

    # --- Predictable patterns ---
    if has_sequential_chars(password):
        score -= 15
        feedback.append("Contains a sequential pattern (e.g. 'abcd', '1234') — avoid predictable runs.")
    if has_repeated_chars(password):
        score -= 15
        feedback.append("Contains repeated characters (e.g. 'aaaa') — avoid repetition.")
    if has_keyboard_pattern(password):
        score -= 15
        feedback.append("Contains a common keyboard pattern (e.g. 'qwerty') — these are cracked instantly.")

    # --- Entropy adjustment ---
    entropy = calculate_entropy(password)
    if entropy < 28:
        score -= 10
    elif entropy >= 60:
        score += 10

    score = max(0, min(100, score))

    if score >= 80:
        rating = "Very Strong"
    elif score >= 60:
        rating = "Strong"
    elif score >= 40:
        rating = "Moderate"
    elif score >= 20:
        rating = "Weak"
    else:
        rating = "Very Weak"

    if not feedback:
        feedback.append("Looks good! No obvious weaknesses detected.")

    return {
        "score": score,
        "rating": rating,
        "entropy_bits": round(entropy, 1),
        "length": length,
        "feedback": feedback,
        # Structured detail fields (used by the web UI's test-by-test readout;
        # additive fields, safe to ignore from the CLI).
        "variety_count": variety,
        "is_known_common": password.lower() in common_passwords,
        "has_sequential": has_sequential_chars(password),
        "has_repeated": has_repeated_chars(password),
        "has_keyboard_pattern": has_keyboard_pattern(password),
    }
