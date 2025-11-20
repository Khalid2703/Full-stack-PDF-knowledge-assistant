"""
Simple test helper to login and call /api/auth/me

Usage:
  Set environment variables AUTH_EMAIL and AUTH_PASSWORD, or the script will prompt.
  python scripts/test_auth.py

This script requires the `requests` package (already in requirements.txt).
"""
import os
import sys
import getpass
import requests

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000/api")


def get_credentials():
    email = os.environ.get("AUTH_EMAIL")
    password = os.environ.get("AUTH_PASSWORD")
    if not email:
        email = input("Email: ")
    if not password:
        password = getpass.getpass("Password: ")
    return email, password


def login(email, password):
    url = f"{API_BASE}/auth/login"
    resp = requests.post(url, json={"email": email, "password": password})
    if resp.status_code != 200:
        print(f"Login failed ({resp.status_code}): {resp.text}")
        return None
    data = resp.json()
    return data.get("access_token")


def me(token):
    url = f"{API_BASE}/auth/me"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    print(f"GET /auth/me -> {resp.status_code}")
    try:
        print(resp.json())
    except Exception:
        print(resp.text)


if __name__ == "__main__":
    email, password = get_credentials()
    token = login(email, password)
    if not token:
        sys.exit(1)
    print("Access token:", token)
    me(token)
