"""Build a backend release from an explicit allowlist, without local settings."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile


PROJECT = Path(__file__).resolve().parent.parent
WORKSPACE = PROJECT.parent
OUTPUT = WORKSPACE / "deployment-artifacts"
RELEASE = "laowai-backend-" + datetime.now().strftime("%Y%m%d-%H%M%S")
ARCHIVE = OUTPUT / f"{RELEASE}.tar.gz"

sys.path.insert(0, str(PROJECT / "scripts"))
from import_questions import load_questions  # noqa: E402


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    payload: dict[str, bytes] = {}

    def include(path: Path) -> None:
        if path.is_symlink():
            raise ValueError(f"Symlink refused: {path.name}")
        relative = path.resolve().relative_to(WORKSPACE).as_posix()
        payload[relative] = path.read_bytes()

    for name in ("main.py", "requirements.txt", "alembic.ini", "pytest.ini", ".env.example"):
        include(PROJECT / "server" / name)
    for directory in ("src", "alembic", "tests"):
        for path in sorted((PROJECT / "server" / directory).rglob("*")):
            if path.is_file() and path.suffix in {".py", ".mako"}:
                if "__pycache__" not in path.parts:
                    include(path)
    for name in ("import_questions.py", "check_database_integrity.py", "reset_database.py", "export_schema.py"):
        include(PROJECT / "scripts" / name)
    include(PROJECT / "database" / "schema.sql")
    include(PROJECT / "database" / "README.md")
    include(PROJECT / "docs" / "question-bank-import-contract.md")
    sources = sorted((WORKSPACE / "original_question_bank").rglob("questions.json"))
    for path in sources:
        include(path)
    questions, report = load_questions(WORKSPACE / "original_question_bank")
    if report.invalid:
        raise RuntimeError("Invalid question bank; bundle was not produced")
    assets = {value for question in questions for value in [question.stem_audio, question.stem_image,
              *(option.get("image") for option in question.options)] if value and not value.startswith(("https://", "http://"))}
    for relative in sorted(assets):
        include(WORKSPACE / "original_question_bank" / relative)

    production_template = """# Copy to .env.local on the server and fill every required secret locally.
APP_ENV=production
CORS_ORIGINS=https://laowaiyidiantong.icu,https://www.laowaiyidiantong.icu

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=laowai_app
MYSQL_PASSWORD=REPLACE_WITH_DATABASE_PASSWORD
MYSQL_DATABASE=csca_hks_exam

AUTH_ALLOW_DEV_OPENID=false
JWT_SECRET_KEY=REPLACE_WITH_GENERATED_RANDOM_JWT_SECRET
JWT_EXPIRE_HOURS=72
WX_APPID=REPLACE_WITH_WECHAT_APPID
WX_SECRET=REPLACE_WITH_WECHAT_APPSECRET
CONTENT_ADMIN_OPENIDS=

# Leave the AI key empty until the real AI integration is configured.
QWEN_API_KEY=
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.8-27b
QWEN_TEMPERATURE=0.3
QWEN_MAX_TOKENS=1024
QWEN_TIMEOUT_SECONDS=45
"""
    payload["csca-hks-exam-app/server/.env.production.example"] = production_template.encode("utf-8")

    questions, report = load_questions(WORKSPACE / "original_question_bank")
    manifest = {
        "release": RELEASE,
        "intended_server": "Debian 13, x86_64, MySQL 8.4",
        "question_count": len(questions),
        "question_counts_by_exam": dict(Counter(q.exam_type for q in questions)),
        "question_source_json_files": len(sources),
        "alembic_head": "0007_question_bank_v2",
        "media_files": len(assets),
        "contents": "Backend, migrations, tests, bank tools, source questions, referenced media and sanitized settings templates",
        "excluded": ["real environment files", "credentials", "local user/answer records", "database dumps", "frontend", "dependencies", "unused media binaries", "Git metadata", "caches"],
        "files": {name: {"bytes": len(data), "sha256": sha256(data)} for name, data in sorted(payload.items())},
    }
    manifest_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    payload["DEPLOYMENT-MANIFEST.json"] = manifest_data

    allowed_env_files = {".env.example", ".env.production.example"}
    for name in payload:
        parts = PurePosixPath(name).parts
        assert not PurePosixPath(name).is_absolute() and ".." not in parts
        assert not {".git", "node_modules", "__pycache__", ".venv", "dist"}.intersection(parts)
        assert all(not part.startswith(".env") or part in allowed_env_files for part in parts)

    with ARCHIVE.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as tar:
                for name, data in sorted(payload.items()):
                    info = tarfile.TarInfo(name)
                    info.size = len(data)
                    info.mode = 0o644
                    info.uid = info.gid = info.mtime = 0
                    info.uname = info.gname = ""
                    tar.addfile(info, io.BytesIO(data))

    with tarfile.open(ARCHIVE, "r:gz") as tar:
        members = tar.getmembers()
        assert len(members) == len(payload)
        for member in members:
            assert member.isfile()
            assert tar.extractfile(member).read() == payload[member.name]
        with tempfile.TemporaryDirectory(prefix="verify-backend-", dir=OUTPUT) as verification_root:
            tar.extractall(verification_root, filter="data")

    archive_sha = sha256(ARCHIVE.read_bytes())
    OUTPUT.joinpath(f"{RELEASE}.sha256").write_text(f"{archive_sha}  {ARCHIVE.name}\n", encoding="ascii")
    OUTPUT.joinpath(f"{RELEASE}.manifest.json").write_bytes(manifest_data)
    print(json.dumps({
        "archive": str(ARCHIVE), "bytes": ARCHIVE.stat().st_size,
        "sha256": archive_sha, "files": len(payload),
        "question_count": len(questions), "json_files": len(sources),
        "archive_verified": True,
    }, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
