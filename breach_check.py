"""
breach_check.py
Checks whether a password has appeared in known data breaches, using the
Have I Been Pwned (HIBP) Pwned Passwords API.

This uses the k-ANONYMITY MODEL, which is the interesting security concept
in this file:

  1. We SHA-1 hash the password locally. The plaintext password never
     leaves this machine.
  2. We send only the FIRST 5 CHARACTERS of that hash to the API.
  3. The API returns every hash suffix in its database that shares that
     5-character prefix — usually several hundred of them — each with a
     breach count.
  4. We compare our full hash against that returned list LOCALLY.

Because the API only ever sees a 5-character prefix shared by hundreds of
possible passwords, it cannot determine which password we were actually
checking. This is the same technique browsers and password managers use
for their built-in breach-check features.
"""

import hashlib
import requests

HIBP_API_URL = "https://api.pwnedpasswords.com/range/{}"


def check_password_breach(password, timeout=5):
    """
    Returns:
        {"breached": bool, "count": int}  on success
        {"error": str}                     if the request failed
    """
    sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]

    try:
        response = requests.get(HIBP_API_URL.format(prefix), timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Could not reach breach database: {e}"}

    for line in response.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return {"breached": True, "count": int(count)}

    return {"breached": False, "count": 0}
