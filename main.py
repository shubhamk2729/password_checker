#!/usr/bin/env python3
"""
Password Strength & Breach Checker
------------------------------------
A beginner cybersecurity project covering:
  - Password entropy estimation
  - Common-pattern / common-password detection
  - SHA-1 hashing
  - The k-anonymity model (via the Have I Been Pwned API)

Usage:
    python main.py                        # prompts securely (hidden input)
    python main.py -p "mypassword123"      # pass password directly
    python main.py --no-breach-check       # skip the online check (offline mode)
    python main.py --wordlist custom.txt   # use a different common-password list
"""

import argparse
import getpass
import sys

from strength import analyze_password, load_common_passwords
from breach_check import check_password_breach


def render_bar(score, width=30):
    filled = int(width * score / 100)
    return "█" * filled + "░" * (width - filled)


def main():
    parser = argparse.ArgumentParser(description="Check password strength and breach history.")
    parser.add_argument("--password", "-p", help="Password to check (omit to be prompted securely)")
    parser.add_argument("--no-breach-check", action="store_true", help="Skip the online breach check")
    parser.add_argument("--wordlist", default="common_passwords.txt", help="Path to common passwords list")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Enter password to check (input hidden): ")
    if not password:
        print("No password entered.")
        sys.exit(1)

    common_passwords = load_common_passwords(args.wordlist)
    result = analyze_password(password, common_passwords)

    print("\n" + "=" * 50)
    print("PASSWORD STRENGTH REPORT")
    print("=" * 50)
    print(f"Length:   {result['length']} characters")
    print(f"Entropy:  {result['entropy_bits']} bits")
    print(f"Score:    {result['score']}/100  [{render_bar(result['score'])}]")
    print(f"Rating:   {result['rating']}")
    print("\nFeedback:")
    for f in result["feedback"]:
        print(f"  - {f}")

    if not args.no_breach_check:
        print("\nChecking Have I Been Pwned breach database...")
        breach_result = check_password_breach(password)
        if "error" in breach_result:
            print(f"  ! {breach_result['error']}")
        elif breach_result["breached"]:
            print(f"  ⚠ Found in {breach_result['count']:,} known data breaches — change it if you use it anywhere.")
        else:
            print("  ✓ Not found in known breaches (this alone doesn't mean it's strong — see rating above).")

    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
