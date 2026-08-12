# Codex Project Memory

## Project

- Project: 留学考霸 - CSCA & HKS exam-prep WeChat mini-program.
- Workspace: `E:\Deng\csca-hks-exam-app`
- Current date: 2026-08-12.
- Paper: none provided. All decisions are engineering decisions, not paper claims.

## Product Goal

Build a complete learning loop:

`刷题 -> 组卷 -> 答题 -> 成绩反馈 -> 错题本 -> 复习`

## Stack Order

1. `uni-app + Vue 3`
2. `Pinia`
3. `TypeScript`
4. `FastAPI`
5. `SQLAlchemy`
6. `MySQL`
7. `Redis` reserved for sessions and cache
8. `JWT`
9. `OSS / 微信云存储` reserved for media and PDF assets

## Completed

- Removed the old `CLAUDE.md` file and Claude-specific references.
- Refactored frontend shared types, constants, mocks, API contracts, and exam store.
- Added FastAPI application factory and versioned API router.
- Added backend service layers for users, questions, exams, and wrongbook.
- Added exam and wrongbook API routes.
- Fixed a circular import in `server/src/common/deps.py`.
- Added frontend API integration for:
  - paper generation
  - answer submission
  - result reports
  - knowledge-point statistics
  - wrongbook list/detail/mastered state
  - related-question navigation
- Added `client/src` uni-app entry files and corrected page/component resolution.
- Corrected the uni-app dependency versions in `client/package.json`.
- MySQL80 is running.
- Database `csca_hks_exam` was created successfully.
- Database schema and 5 sample questions were imported successfully.
- Backend dependencies are installed in `server/.venv`.
- Frontend dependencies are installed in `client/node_modules`.
- Backend starts on `http://127.0.0.1:8000`.
- Frontend MP-Weixin compilation succeeds and outputs to:
  `client/dist/dev/mp-weixin`.
- Exam-mode paper generation no longer returns `answer` or `analysis`.
- Exam-mode answer submission no longer returns `is_correct` or `correct_answer`.
- Practice mode still returns immediate correctness and solution fields.
- Frontend API base URL now comes from `VITE_API_BASE_URL`.
- Frontend request layer no longer sends an empty `Authorization` header.

## Known Risks

- Frontend API base URL is configured through `client/.env.development`.
- WeChat login is still development-mode login using `dev-openid`.
- Dashboard, profile, history, and wrongbook redo still contain mock-driven areas.
- Wrongbook PDF export returns HTTP 501.
- Sass emits legacy API deprecation warnings; this is non-blocking.
- PowerShell may display UTF-8 API text as mojibake even when the data is valid.

## Current Development Plan

### Phase 1: Correctness and Security

1. Hide answer and analysis fields in exam-mode paper responses. Done.
2. Make exam result the authoritative source for correctness. Done for exam-mode submit responses.
3. Move frontend API base URL to environment configuration. Done.
4. Normalize API error and loading behavior. Partially done in the request layer.
5. Add focused backend tests for paper generation and answer submission. Pending.

### Phase 2: Real Business Data

1. Replace dashboard mock data.
2. Replace profile mock data.
3. Connect history paper list.
4. Implement real wrongbook redo paper generation.
5. Implement real WeChat `code2session` login.

### Phase 3: UX and Release

1. Polish mobile layouts and empty/loading/error states.
2. Run full WeChat DevTools regression.
3. Add migrations, idempotent seeds, deployment notes, and release checks.

## Environment Rules

- User handles network, proxy, or package-download issues.
- Stop and ask the user when a network operation fails.
- Do not expose or request MySQL passwords in chat.
- Keep backend and frontend dev servers running in separate terminals.
- Backend command:
  `server/.venv/Scripts/python.exe -m uvicorn main:app --reload`
- Frontend command:
  `npm.cmd run dev:mp-weixin`

## Working Style

- Prefer small, reviewable changes.
- Preserve existing user changes.
- Use `apply_patch` for manual edits.
- Run static checks after each implementation stage.
- Report completed work, remaining risks, and the next concrete action.

## Review Snapshot (2026-08-11)

### Verified State

- Backend health check passes: `GET /api/v1/health` returns HTTP 200.
- Frontend `npm.cmd run build:mp-weixin` succeeds; remaining output is Sass legacy JS API warnings plus an `os` alias warning.
- `pytest -q` finds no runnable tests (exit status 5); `server/tests/conftest.py` only provides a `TestClient` fixture.
- `original_question_bank` contains 60 UTF-8 JSON files; all parse successfully with approximately 3,708 question records.
- The checked-in SQL seed contains only 5 sample question rows, so the production-shaped question bank is not yet imported into MySQL.

### Current Product Boundary

- The core path is implemented end to end at API level: generate paper -> submit answer -> result report -> wrongbook list/detail/mastered state -> related questions.
- Exam mode hides solutions during paper generation and does not return correctness from answer submission; practice mode returns immediate correctness and solution fields.
- The client still uses mock data for dashboard, profile, history, and wrongbook redo. The user store also writes `mock-token` instead of calling `/user/wx-login`.
- `/user/wx-login` currently treats the submitted code as the openid (or falls back to `dev-openid`); this is development-only and is not a real WeChat `code2session` flow.
- Wrongbook PDF export is an explicit HTTP 501 placeholder. The result page's `reviewAll` action is also a no-op.

### Risks Found During Review

- Authentication is permissive by default: requests without a bearer token resolve to `dev-openid`. Production configuration must fail closed and require a verified token.
- `POST /exam/submit` verifies paper ownership but does not verify that `question_id` belongs to the paper's `question_ids`; add this integrity check before release.
- The API has no pagination/summary endpoint for dashboard and history, so replacing mocks will otherwise couple pages to ad-hoc queries.
- `func.rand()` is acceptable for the sample database but will become expensive as the full question bank is imported; define a scalable sampling strategy before data volume grows.
- Database schema and ORM models rely on application checks and do not declare foreign keys; migration/seed idempotency and referential integrity remain release work.

### Next Optimization Plan

1. **Data foundation:** define the import contract for the 60 JSON files, map CSCA/HKS subjects and question types, validate required answer/options fields, deduplicate records, and make the import idempotent. Verify counts by exam/subject/difficulty after import.
2. **Backend correctness/security:** add focused tests for paper generation, exam/practice response redaction, answer idempotency, paper-question membership, result aggregation, wrongbook transitions, and auth failure behavior. Replace permissive development auth with an explicit development flag and real WeChat exchange in production.
3. **Real client data:** add dashboard summary, user profile, history, and wrongbook-redo APIs; replace page-level mock imports with loading/error/empty states and API-backed stores. Make the result review action navigate to persisted answer details.
4. **Learning loop completion:** implement wrongbook redo paper generation from server-selected unmastered items, persist redo submissions through the same exam service, and expose PDF export only after a real export implementation exists.
5. **Release hardening:** add Alembic revisions and idempotent seeds, declare ownership/foreign-key constraints or document the deliberate alternative, restrict CORS, move secrets to deployment config, and run a WeChat DevTools regression against a clean database.

### Immediate Next Action

Start with the question-bank import contract and backend test scaffolding. Do not begin UI polish or social features until the full data set can be imported repeatably and the exam submission integrity tests pass.

## Progress Update (2026-08-11)

- Added `scripts/import_questions.py` as the repeatable question-bank importer. It supports dry-run by default and requires `--apply` before writing to MySQL.
- Added `docs/question-bank-import-contract.md` to document supported source shapes, HSK->HKS mapping, raw HSK4 mapping, skipped learning resources, and idempotent upsert key.
- Dry-run validation passes with 2562 importable questions, 128 source duplicates skipped, and no invalid records. The importer intentionally skips 1018 non-question learning-resource records from HSK4 vocabulary, sentences, and grammar-pattern files.
- Added explicit auth development switch: `AUTH_ALLOW_DEV_OPENID` and `DEV_OPENID`. Missing bearer auth now fails with HTTP 401 when the dev switch is disabled.
- Fixed `submit_answer` integrity: a submitted `question_id` must belong to the paper's `question_ids`, otherwise the service raises `AppException` code `40013`.
- Added SQLite-backed pytest scaffolding plus focused tests for auth behavior and `exam.submit` paper-question membership.
- Added importer unit tests and paper-generation redaction tests for exam/practice modes.
- Verification: `server/.venv/Scripts/python.exe -m pytest -q` passes with 8 tests. Remaining warnings are existing Pydantic/pytest-asyncio deprecations.
- Attempted `scripts/import_questions.py --apply`, but MySQL refused connection because local `MySQL80` is stopped. `sc.exe qc MySQL80` shows it points to `E:\MySQL\MySQL Server 8.0\bin\mysqld.exe` with `my.ini`; both `Start-Service` and `sc.exe start MySQL80` fail with access denied even after elevated execution, and the MySQL `Data` directory is not readable from this session. Database write has not been completed yet.

### Next Immediate Action

Restore/start the local MySQL service, then run `server/.venv/Scripts/python.exe scripts/import_questions.py --apply`. After import, verify database counts by exam, subject, difficulty, and question type.

## Progress Update (2026-08-12)

- Expanded backend correctness tests to cover answer idempotency, answer correction counter adjustments, result aggregation with unanswered questions, wrongbook auto-mastering after three later correct answers, manual mastered toggle, wrongbook filtering, and related-question redaction.
- Added `generate_redo_paper` backend service and `POST /wrongbook/redo-paper?examType=CSCA|HKS&limit=20`. It creates a practice paper from the current user's unmastered wrong questions for one exam type and returns questions with solutions for redo practice.
- Added frontend API entry `wrongBookApi.generateRedoPaper(...)` and rewired `client/src/pages/wrongbook/redo.vue` away from mock data. The page now loads a real redo paper, submits each selected answer through `examApi.submitAnswer`, and redirects to the persisted result page on completion.
- Verification: backend `pytest -q` passes with 16 tests. Frontend `npm.cmd run build:mp-weixin` succeeds with the existing Sass legacy API and `os - Alias not found` warnings.

### Next Immediate Action

After MySQL service is restored, apply and verify the full question-bank import. Then continue replacing remaining dashboard, profile, and history mocks with API-backed data.

## Data Import Completed (2026-08-12)

- User restored `MySQL80` to running state.
- Running `scripts/import_questions.py --apply` from the project root failed because `settings.Config.env_file = ".env"` did not load `server/.env` from that working directory and therefore attempted `root` with no password.
- Running from `server` succeeded with `server/.env`: `server/.venv/Scripts/python.exe ../scripts/import_questions.py --apply`.
- Import result: inserted 2562, updated 0.
- Database verification: 2567 total questions. The extra 5 are the pre-existing sample seed rows.
- Verified database distribution:
  - Exam counts: CSCA 270, HKS 2297.
  - Difficulty counts: easy 245, medium 2241, hard 81.
  - Question type counts: single 2095, multi 1, judge 177, fill 294.
  - HKS subjects: 听力 951, 阅读 916, 书写 375, 口语 34, 翻译 21.
  - CSCA imported subjects each have 53 rows for 化学, 数学, 文科中文, 物理, 理科中文; 5 older sample rows remain under 地理常识/文化常识/语言知识.
- Real database smoke test generated an HKS exam paper with 5 questions and confirmed answer redaction (`has_answer: False`).
- Backend verification after import: `pytest -q` passes with 16 tests.

### Next Immediate Action

Fix `.env` loading so scripts can be run safely from the project root, or document that DB-backed scripts must be run from `server`. Then continue replacing dashboard, profile, and history mocks with API-backed data.

## Progress Update (2026-08-12, Import Script Fix)

- Fixed `scripts/import_questions.py` so database-backed commands temporarily use `server` as the working directory before importing project database settings. This makes `server/.env` load correctly even when the script is launched from the project root.
- Verified from project root:
  - `server/.venv/Scripts/python.exe scripts/import_questions.py --verify-db` succeeds and reports 2567 database questions.
  - `server/.venv/Scripts/python.exe scripts/import_questions.py --apply` succeeds idempotently with inserted 0, updated 2562.
  - `server/.venv/Scripts/python.exe scripts/import_questions.py` dry-run still succeeds.
  - Backend `pytest -q` still passes with 16 tests.

### Next Immediate Action

Continue replacing dashboard, profile, and history mocks with API-backed data.
