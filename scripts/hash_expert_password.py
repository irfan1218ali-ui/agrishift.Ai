"""Prompt for an expert password and print its PBKDF2 hash for .env."""
from __future__ import annotations

import base64
import getpass
import hashlib
import secrets


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def main() -> None:
    password = getpass.getpass("Expert password (input hidden): ")
    confirmation = getpass.getpass("Confirm password: ")
    if not password or password != confirmation:
        raise SystemExit("Passwords are empty or do not match.")
    salt = secrets.token_bytes(16)
    iterations = 600_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    print("EXPERT_PASSWORD_HASH=" + f"pbkdf2_sha256${iterations}${_encode(salt)}${_encode(digest)}")


if __name__ == "__main__":
    main()
