# Security notes

- Farmer analysis is public and does not create an account.
- The Expert Portal has one `EXPERT` role. Its account is seeded from `EXPERT_EMAIL` and a PBKDF2-SHA256 `EXPERT_PASSWORD_HASH`; never put a plaintext password in source control.
- `EXPERT_SESSION_SECRET` must be randomly generated and at least 32 characters. The signed cookie is Secure, HttpOnly, SameSite=Strict, expires after eight hours, and can be revoked at logout.
- Login failures are limited to ten attempts per client address in a ten-minute window. The in-memory limiter resets when the API restarts, so a public host must also rate-limit at its edge.
- Request bodies with a declared size over 1 MiB are rejected. Expert API responses use `Cache-Control: no-store` and `Vary: Cookie`.
- SQLite foreign-key enforcement is enabled. Database initialization adds missing schema pieces without dropping farmer rows.
- Keep provider credentials and local `.env` files out of ZIPs and source control. Only blank `.env.example` templates are distributable.
- Notes, decisions, and audit timestamps are stored in SQLite and linked to the analysis and expert user.
- Analysis coordinates are personal data. Do not publish the SQLite database or share real farmer requests outside the project team.
- Local demo traffic uses HTTP loopback; a public deployment must terminate TLS and keep the Secure cookie flag enabled.

To configure the account, copy `.env.example` to `.env`, generate a hash with `python scripts/hash_expert_password.py`, add the email and a random session secret, then restart the API.
