# Current local deployment

The verified release runs locally: Next.js on loopback port 3000, FastAPI on loopback port 8000, and SQLite at `data/agrishift.db`. No Compose services, cloud resources, or remote deployment target are required by the MVP.

Do not deploy this checkout to a public host until TLS, a private expert `.env`, database backup/retention, restricted origins, and an approved hosting target are configured. No deployment credentials or target configuration are present in the current environment.

Start the verified local stack from the repository root with `python scripts/start_demo.py`. The launcher runs Next.js on loopback port 3000 and FastAPI on loopback port 8000, validates runtime data/model files, and initializes SQLite at `data/agrishift.db` without deleting existing analyses.

No cloud deployment is configured in this workspace. A real deployment needs a selected host, HTTPS, restricted `CORS_ORIGINS`, persistent SQLite storage, `APP_ENV=production`, and private expert session/password-hash environment settings. The API and frontend commands and variables are listed in `README_FINAL.md`.
