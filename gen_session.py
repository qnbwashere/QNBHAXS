"""
Run this ONCE on Replit (or any trusted device) to generate your Instagram session.
Paste the output JSON as the IG_SESSION secret in GitHub.

Usage:
    pip install instagrapi
    python gen_session.py
"""

import json
import os
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired, ChallengeRequired

username = os.environ.get("IG_USERNAME") or input("Instagram username: ").strip()
password = os.environ.get("IG_PASSWORD") or input("Instagram password: ").strip()

cl = Client()

try:
    cl.login(username, password)
except TwoFactorRequired:
    code = input("Enter your 2FA code: ").strip()
    cl.login(username, password, verification_code=code)
except ChallengeRequired:
    print("Instagram sent a verification challenge.")
    print("Check your email or phone for a code from Instagram.")
    code = input("Enter the verification code: ").strip()
    cl.challenge_resolve(cl.last_json)

print("\n✅ Login successful!")
print("\n=== COPY EVERYTHING BETWEEN THE LINES ===")
print("-" * 60)
print(json.dumps(cl.get_settings()))
print("-" * 60)
print("\nPaste that as the value for a new GitHub secret named: IG_SESSION")
