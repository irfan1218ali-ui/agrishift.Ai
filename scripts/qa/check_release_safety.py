"""Scan files that could be committed and report only redacted findings."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLOCKED_DIRS = {
    ".git", ".venv", "venv", "node_modules", ".next", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".playwright-mcp", "backups",
}
BLOCKED_SUFFIXES = {
    ".env.local", ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".db",
    ".sqlite", ".sqlite3", ".log", ".pem", ".key", ".p12", ".pfx", ".tif",
    ".tiff", ".nc", ".nc4", ".h5", ".hdf", ".hdf5", ".grib", ".jp2",
    ".gpkg", ".shp", ".shx", ".dbf",
}
SECRET_NAME = re.compile(
    r"(?i)^\.(?:env|env\..+)$|(?:credentials?|secrets?|private[_-]?key|service[_-]?account)",
)
SECRET_ASSIGNMENT = re.compile(
    r"(?m)^\s*(?:export\s+)?(EXPERT_EMAIL|EXPERT_PASSWORD_HASH|EXPERT_SESSION_SECRET|"
    r"METEOMATICS_USERNAME|METEOMATICS_PASSWORD|NASA_API_KEY|OPENAI_API_KEY|"
    r"GITHUB_TOKEN|ACCESS_TOKEN|CLIENT_SECRET)\s*=\s*([^#\r\n]*)"
)
GENERIC_TOKEN = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|"
    r"sk-[A-Za-z0-9_-]{24,})\b"
)
BEARER_TOKEN = re.compile(r"(?i)\bauthorization\s*[:=]\s*bearer\s+([^\s\"']+)")
LOCAL_USER_PATH = re.compile(r"(?i)\b[A-Z]:[\\/]Users[\\/][^\\/\s\"']+")
PLACEHOLDERS = {"", "example", "placeholder", "changeme", "change_me", "your_value", "<redacted>"}
RAW_METADATA_NAMES = {"README.md", "manifest.csv", ".gitignore"}


def git_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, capture_output=True,
    )
    return [ROOT / Path(name.decode("utf-8", errors="surrogateescape"))
            for name in result.stdout.split(b"\0") if name]


def blocked_path(path: Path) -> str | None:
    relative = path.relative_to(ROOT)
    parts = set(relative.parts)
    filename = relative.name.lower()
    suffixes = {suffix.lower() for suffix in path.suffixes}
    is_env_example = filename == ".env.example"
    if not is_env_example and (filename == ".env" or filename.startswith(".env.")):
        return "environment file"
    if not is_env_example and SECRET_NAME.search(filename):
        return "credential-named file"
    if parts & BLOCKED_DIRS:
        return "local cache or backup directory"
    if suffixes & BLOCKED_SUFFIXES:
        return "private, temporary, archive, or raw-data file"
    if relative.parts and relative.parts[0] in {"data", "data\\"}:
        allowed_metadata = {name.lower() for name in RAW_METADATA_NAMES}
        if relative.as_posix().startswith(("data/raw/", "data/interim/")) and filename not in allowed_metadata:
            return "raw/interim data payload"
    return None


def inspect_content(path: Path) -> list[tuple[str, int]]:
    try:
        if path.stat().st_size > 20 * 1024 * 1024:
            return [("oversized file", 0)]
        raw = path.read_bytes()
    except OSError:
        return [("unreadable file", 0)]
    if b"\0" in raw:
        return []
    text = raw.decode("utf-8", errors="replace")
    findings: list[tuple[str, int]] = []
    relative = path.relative_to(ROOT).as_posix().lower()
    for number, line in enumerate(text.splitlines(), start=1):
        if LOCAL_USER_PATH.search(line):
            findings.append(("absolute local user path", number))
        if GENERIC_TOKEN.search(line):
            findings.append(("high-confidence API/token pattern", number))
        bearer = BEARER_TOKEN.search(line)
        if bearer and bearer.group(1).strip("{}$").lower() not in PLACEHOLDERS:
            findings.append(("authorization bearer value", number))
        assignment = SECRET_ASSIGNMENT.search(line)
        if assignment:
            value = assignment.group(2).strip().strip("\"'").strip()
            if value.lower() not in PLACEHOLDERS and not value.startswith("${"):
                is_test_fixture = ("test" in relative or "fixture" in relative) and "test" in value.lower()
                is_example_email = assignment.group(1) == "EXPERT_EMAIL" and value.lower().endswith(".example")
                if not is_test_fixture and not is_example_email:
                    findings.append(("credential assignment", number))
    return findings


def main() -> int:
    try:
        files = git_files()
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: could not enumerate Git candidate files ({type(exc).__name__}).")
        return 2

    findings: list[tuple[str, str, int]] = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        category = blocked_path(path)
        if category:
            findings.append((relative, category, 0))
        findings.extend((relative, category, line) for category, line in inspect_content(path))

    if findings:
        print(f"FAIL: {len(findings)} release-safety finding(s); values are redacted.")
        for relative, category, line in findings:
            location = f":{line}" if line else ""
            print(f"{relative}{location}: {category}")
        return 1

    print(f"PASS: scanned {len(files)} tracked and non-ignored candidate files; no sensitive or excluded content found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
