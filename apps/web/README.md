# AgriShift AI frontend

The public farmer flow and single EXPERT portal use Next.js App Router, React, TypeScript, Tailwind CSS, shadcn-style UI primitives, and MapLibre GL. The farmer flow requires no account. Expert authentication, analysis search, reviews, notes, and review status are served by FastAPI and SQLite.

## Run locally

From the repository root, install frontend dependencies once with `cd apps/web && npm ci`, then return to the root and run `python scripts/start_demo.py`. Open `http://127.0.0.1:3000`. Next.js serves the UI and proxies `/api/expert/*` to the API on port 8000; public farmer requests continue to use `/api/v1`.

## Configure the EXPERT account

The API seeds exactly one EXPERT from the root `.env` values `EXPERT_EMAIL` and `EXPERT_PASSWORD_HASH`. Generate the hash with `python scripts/hash_expert_password.py`; it prompts without echoing the password and prints only the encoded hash. Set a random `EXPERT_SESSION_SECRET` with at least 32 characters. Keep `.env` private and restart the API after changing it. The expert session is an eight-hour signed, Secure, HttpOnly, SameSite=Strict cookie.

The expert API is unavailable until the email, password hash, and session secret are configured. Farmer analysis remains public and works without expert credentials.

## Checks

```powershell
npm run typecheck
npm run build
```

The landing-page field photograph is credited to Rabia Saleem via Wikimedia Commons under CC BY-SA 4.0 and is labelled illustrative, not as an analyzed field.
