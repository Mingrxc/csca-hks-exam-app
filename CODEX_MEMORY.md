# Codex Project Memory

## Project

- Project: 留学考霸 - CSCA & HKS exam-prep WeChat mini-program.
- Workspace: `E:\Deng\csca-hks-exam-app`
- Current date: 2026-08-17.
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

- Real WeChat login still needs WeChat DevTools and physical-device regression with valid `WX_APPID` and `WX_SECRET`.
- Database foreign keys are intentionally deferred; the read-only integrity audit is currently clean, but application-level ownership checks remain important.
- The database contains 5 legacy sample questions in addition to the 2562 imported questions.
- The real-API smoke test left one legitimate development paper/answer/wrongbook record under the configured development user.
- Sass emits legacy API deprecation warnings; this is non-blocking.
- `python-jose` emits one third-party `datetime.utcnow()` deprecation warning during tests; this is non-blocking.

## Current Development Plan

### Phase 1: Release Regression

1. Import `client/dist/build/mp-weixin` into WeChat DevTools and test the complete learning loop.
2. Test real `code2session` login with valid WeChat credentials and production auth settings.
3. Run physical-device checks for PDF download/preview, long question text, result review, and date editing.

### Phase 2: Deployment Hardening

1. Document production environment variables and startup/migration order.
2. Decide whether to add foreign keys after reviewing deletion and retention requirements.
3. Separate or remove the 5 legacy sample questions before production data preparation.

### Phase 3: Product Polish

1. Fix issues found in DevTools/device regression before adding new feature scope.
2. Review remaining loading, empty, and error states on all main pages.
3. Address Sass and dependency deprecations during a controlled dependency upgrade.

## Environment Rules

- User handles network, proxy, or package-download issues.
- Retry an environment or network operation at most three times, then give the user a concrete action to perform.
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

## Progress Update (2026-08-16, Remaining Product Features)

- Added `GET /user/dashboard` with real user identity, today's answered/correct/wrong counts, unmastered wrong-question count, target date, and three recent completed papers.
- Reworked `GET /question/papers` into completed-paper history with score, correct rate, elapsed time, pass state, and stable completion ordering. Reopening a result no longer changes `finished_at`.
- Added daily streak persistence for each newly answered question. Resubmitting the same paper/question does not double-count the daily record or streak.
- Removed dashboard, profile, and history mock imports. These pages now refresh from APIs on `onShow` and provide retry/empty states.
- Fixed history/result navigation to accept both `id` and `paperId` query parameters.
- Added full result review data and an expandable “全部解析” section with options, user answer, correct answer, correctness, and analysis for every question.
- Added editable target exam and target date in the profile page. Removed nonfunctional achievement, report, reminder, and feedback menu entries.
- Implemented real WeChat `code2session` exchange. Missing WeChat credentials only fall back to `DEV_OPENID` when `AUTH_ALLOW_DEV_OPENID=true`; production fails closed.
- JWT now reads `JWT_SECRET_KEY`, algorithm, and expiry from settings, includes `exp`, and rejects missing subjects or tokens signed with another key.
- Frontend no longer writes `mock-token`. API requests share one `uni.login` operation, persist the returned JWT, and retry once after a 401.
- Implemented wrongbook PDF generation and the mini-program download/open-document flow. Added `reportlab==4.4.9` to backend requirements.
- Verification: backend `pytest -q` reports 26 passed and 1 skipped. The skipped test is PDF generation because ReportLab could not be downloaded into `server/.venv` in the current network environment.
- Verification: `npm.cmd run build:mp-weixin` succeeds. Existing Sass legacy API and `os - Alias not found` warnings remain non-blocking.
- Real MySQL smoke testing was not rerun because `MySQL80` is stopped and cannot be opened even through the approved elevated `Start-Service` attempt.

### Current Remaining Work

1. Restore MySQL80 and install backend requirements, then run real API and PDF smoke tests.
2. Add an Alembic baseline plus answer-record uniqueness and referential-integrity migrations.
3. Replace `ORDER BY RAND()` for scalable question sampling.
4. Run WeChat DevTools and physical-device regression with real `WX_APPID`/`WX_SECRET` and production auth settings.

## Progress Update (2026-08-16, Release Hardening)

- ReportLab installation was attempted three times as requested: official PyPI timed out, the Tsinghua mirror returned HTTP 403, and the Aliyun mirror succeeded. `reportlab==4.4.9`, Pillow, and charset-normalizer are installed in `server/.venv`.
- The Chinese wrongbook PDF integration test now runs instead of skipping and validates a real `%PDF-` document.
- MySQL80 was tested through `Start-Service`, `sc.exe start`, and `net.exe start`. All three returned Windows service-control access denied (`System error 5`). The user must start it from an administrator PowerShell before real-DB work continues.
- Added Alembic `0001_initial_schema` and `0002_answer_record_uniqueness` revisions, a working metadata-aware `env.py`, and the missing revision template.
- `0002` deduplicates answer records by keeping the greatest ID for each `(user_id, paper_id, question_id)`, adds the unique constraint, and renames legacy indexes to globally descriptive names.
- Updated ORM metadata and `database/schema.sql` to match the migrated index and constraint layout.
- Documented fresh-database, existing-database stamp/upgrade, and schema.sql stamp workflows in `database/README.md`.
- Database foreign keys remain deliberately deferred until the real MySQL integrity audit can confirm there are no orphan rows.
- Added `scripts/check_database_integrity.py`, a read-only audit for missing tables, Alembic version, duplicate answer keys, and orphan business rows.
- Replaced database `ORDER BY RAND()` with ID-only candidate loading plus Python `random.sample`; progressive papers sort the sampled questions easy-to-hard.
- Added explicit `exam|practice` request validation, configurable CORS origins, safe wildcard credential behavior, and current Pydantic settings configuration.
- Added pytest configuration that avoids the inaccessible administrator-owned cache/temp directories and sets the asyncio fixture scope explicitly.
- Verification: backend `pytest -q` passes 31 tests. Only the third-party `python-jose` UTC deprecation warning remains.
- Verification: Alembic `upgrade head --sql` generates valid MySQL DDL for both revisions.
- Verification: MP-Weixin production build succeeds; only Sass legacy JS API warnings remain.

### Immediate Next Action

After the user starts `MySQL80` as administrator:

1. Run `server/.venv/Scripts/python scripts/check_database_integrity.py`.
2. Back up the existing database.
3. Run `server/.venv/Scripts/python -m alembic stamp 0001_initial_schema` from `server`.
4. Run `server/.venv/Scripts/python -m alembic upgrade head`.
5. Re-run the integrity audit, importer verification, API smoke tests, and PDF endpoint smoke test.

## Progress Update (2026-08-16, MySQL Migration and Real Smoke Verification)

- The user started `MySQL80` from an administrator PowerShell; the service is running.
- Pre-migration integrity audit found 2567 questions, no duplicate answer natural keys, and no orphan rows across papers, answers, wrongbook, knowledge statistics, or streak records.
- Created a pre-migration backup at `database/backups/csca_hks_exam_before_alembic_20260816_170437.sql` (1,436,753 bytes). `database/backups/` is ignored by Git.
- Stamped the existing database at `0001_initial_schema` and upgraded it to `0002_answer_record_uniqueness`.
- The migration added the unique constraint on `(user_id, paper_id, question_id)` and renamed legacy indexes to descriptive globally unique names.
- Post-migration audit is clean: Alembic is at `0002_answer_record_uniqueness`, question count remains 2567, duplicate answer keys are 0, and every checked orphan count is 0.
- Real FastAPI + MySQL smoke test passed: health HTTP 200, HKS practice-paper generation, answer submission, result review, wrongbook retrieval, and PDF export.
- The smoke paper has ID 8 with 5 questions. The deliberately wrong answer produced one unmastered HKS wrongbook entry. PDF response was HTTP 200, `application/pdf`, 3254 bytes, with a valid `%PDF-` header.
- Fixed ORM/MySQL metadata drift for four `TINYINT(1)` fields and table comments. The fields use SQLAlchemy dialect variants so MySQL retains `TINYINT(1)` while SQLite tests use `INTEGER`.
- Final Alembic verification: `python -m alembic check` reports `No new upgrade operations detected`.
- Final backend verification: `31 passed`; only the third-party `python-jose` UTC deprecation warning remains.
- Final database verification: `scripts/check_database_integrity.py` reports `integrity=clean`.
- Final frontend verification: MP-Weixin production build succeeds and outputs to `client/dist/build/mp-weixin`; only Sass legacy JS API warnings remain.

### Immediate Next Action

Run the complete mini-program workflow in WeChat DevTools against the real backend, then repeat the critical login and PDF-preview paths on a physical device with production WeChat credentials.

## Progress Update (2026-08-17, WeChat DevTools Regression)

- Completed a real WeChat DevTools regression against `client/dist/build/mp-weixin` and the MySQL-backed API.
- Confirmed the local tourist-AppID login failure does not block development data access: the frontend handles `uni.login` failure and the backend's explicit `AUTH_ALLOW_DEV_OPENID=true` mode supplies the development identity. Real production login still requires valid WeChat credentials.
- Fixed per-question wrong-reason state in the answer page. Unanswered questions no longer show the wrong-reason prompt, reasons no longer leak between questions, and a selected reason remains when returning to the original question.
- The regression deliberately answered questions and confirmed live dashboard changes: 11 questions today, 45% correct, 6 wrong today, and 12 unmastered wrongbook entries.
- Confirmed the wrongbook refreshes with 12 real entries and the newest circuit question appears first.
- Confirmed wrongbook PDF export opens successfully and Chinese questions and explanations render correctly.
- Fixed the wrongbook redo type mismatch. The `all` list no longer silently treats redo as CSCA; it now asks the user to choose CSCA or HKS. Filtered lists enter their selected type directly.
- Profile, result, and wrongbook-detail redo entries now pass the user's target exam, the current paper exam, and the current question exam respectively.
- Wrongbook list responses now include `exam_type`, and cards visibly identify CSCA/HKS. The redo page no longer silently defaults a missing type to CSCA.
- Real DevTools verification confirmed HKS redo shows `1 / 1` and CSCA redo shows `1 / 11`. The console showed no business errors, only WeChat hot-reload, platform, SharedArrayBuffer, and worker capability warnings.
- Final verification: backend `pytest -q` passes 32 tests; MP-Weixin production build succeeds; `GET /api/v1/health` returns HTTP 200.

### Immediate Next Action

Continue the remaining profile regression: verify accumulated question count, total correct rate, streak, target exam/date editing, and the target-specific redo entry. Then run the critical login and PDF-preview paths on a physical device with production WeChat credentials.

## Progress Update (2026-08-17, Profile and Target Regression)

- Completed the remaining profile regression in WeChat DevTools against the real MySQL-backed API.
- Confirmed the profile displays real accumulated values: 21 answered questions, 38% total correct rate, and a 2-day streak.
- Confirmed the profile only exposes implemented entries: paper history, wrongbook statistics, wrongbook redo, target settings, about, and logout. The old achievement, learning-report, reminder, and feedback placeholders are absent.
- Confirmed the target-settings panel expands correctly with CSCA/HKS selection, the native date picker, and save behavior.
- Changed the target to HKS with exam date `2026-08-18`. The profile header and menu value updated to HKS and the success notification appeared.
- Confirmed the home page immediately synchronized the saved target and displayed the live HKS countdown (`1 day, 19 hours, 33 minutes` at verification time).
- Confirmed the profile wrongbook-redo entry uses the saved HKS target directly and opens the HKS redo session with `1 / 1`; it does not prompt for a type or fall back to CSCA.
- DevTools showed no business errors during the complete profile-target-home-redo workflow. Only the known hot-reload, platform API, SharedArrayBuffer, and worker-capability warnings remained.

### Immediate Next Action

Run the critical login and wrongbook PDF-preview workflows on a physical device with production WeChat credentials. After that, perform release configuration review and a final end-to-end acceptance pass.
