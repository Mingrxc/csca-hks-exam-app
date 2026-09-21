# Codex Project Memory

## Authoritative Current Snapshot

- Snapshot date: 2026-09-21.
- Project: CSCA & HKS exam-prep WeChat mini-program for international students.
- Workspace: `D:\Projects\Deng\csca-hks-exam-app`.
- External question source: `D:\Projects\Deng\original_question_bank`.
- Git branch: `main`.
- Version `v1.2.0` is commit `88a06dcf`. All approved work after it is consolidated locally into one `V1.3.0 后端结构重构完毕 前端未优化` commit.
- The remote `origin/main` currently retains the pre-squash multi-commit history. Do not force-push or otherwise rewrite the remote without separate explicit user approval.
- Phases 0 through 4 are complete. Phase 5 product and visual direction is agreed, but implementation is deliberately paused for a server/deployment selection discussion.

## Product Goal and Direction

The core learning loop remains:

`刷题 -> 组卷 -> 答题 -> 成绩反馈 -> 错题本 -> 复习`

The current product is a functional MVP, not yet a production-quality experience. The agreed direction is to stabilize the repository, backend contracts, data flow, and network behavior first, then perform a substantial frontend UX and visual redesign.

Confirmed Phase 5 product decisions:

1. Keep the public name `老外1点通` for now. `DYH` is a friend's name and is not a product brand.
2. Use a warm academic companion style: warm, restrained, scholarly, and youthful rather than blue exam-software, childish gamification, or an administrative-system appearance.
3. Make the home page approximately 70% study dashboard and 30% international-study content. Goals, countdown, resume/next action, daily metrics, practice entries, and recent learning precede content.
4. Current consultation/content and club-ad entries are placeholders, not real editorial content. Remove fictional promotional cards during redesign, show a professional empty state, and preserve a future real-content module.
5. Keep one dominant action per screen, a restrained radius/elevation system, semantic colors beyond the warm primary palette, and consistent TDesign-based components.
6. Phase 5 order: design baseline plus App Shell/navigation/home; paper/answer; results/review/wrong-book/favorites/history; AI/profile/content. Validate each vertical slice before continuing.

## Current Technology Baseline

1. Frontend: `uni-app + Vue 3 + Pinia + TypeScript + TDesign UniApp + Vite`.
2. Backend: `FastAPI + Pydantic + SQLAlchemy + Alembic`.
3. Database: MySQL 8.4.11, Windows service `MySQL84`.
4. Local database: `csca_hks_exam`; application user is `deng@localhost`.
5. Python: Miniforge Conda environment `deng`, Python 3.11.16 at `C:\Users\Theo\miniforge3\envs\deng\python.exe`.
6. Backend packages match `server/requirements.txt` exactly.
7. Redis remains reserved and is not required by the current core flow.
8. JWT is used for API authentication; OSS / WeChat cloud storage remain future media-storage options.

Never store passwords, JWT secrets, API keys, or other secret values in this memory file.

## Current Database and Data State

- Local configuration is in ignored `server/.env.local`; it overrides the legacy tracked `server/.env`.
- The user has authorized direct use of the local MySQL credentials stored in `server/.env.local`. Load them through the application settings; do not ask for, echo, copy, or record the plaintext password elsewhere.
- Alembic is at `0006_ownership_foreign_keys`.
- All 92 column comments and 10 table comments in the local database are English.
- `alembic check` reports no pending schema operations.
- `scripts/check_database_integrity.py` reports `integrity=clean`.
- Current imported question count is 1,876:
  - CSCA: 265
  - HKS: 1,611
  - easy: 242
  - medium: 1,634
  - single: 1,515
  - judge: 136
  - fill: 225
- The importer skipped 14 duplicate source questions and 8 non-question grammar resources.
- The current source contains 28 JSON files and one PDF; older memory entries describing 60 JSON files and 2,562 imported questions are historical and no longer authoritative.
- Phase 0 read-only baseline verification passed on 2026-09-21: Alembic is at head with no pending operations, database integrity is clean, importer database statistics match 1,876 questions, and real local HTTP smoke checks returned 200 for health, CSCA/HKS special options, and question detail. Question detail did not expose solution fields. The temporary Uvicorn process was stopped after verification.

## Current Working Tree State

The approved work after `v1.2.0` is represented by one local `V1.3.0` commit. It includes database/schema cleanup, repository hygiene, backend contract and integrity restructuring, runtime reliability, frontend architecture foundations, active-exam recovery, and documentation. Phase 5 visual redesign has not started.

`server/.env.local`, frontend mode-local environment files, installed dependencies, and build output are intentionally ignored and must never be committed. The expired `trycloudflare.com` URL was removed from both local frontend mode files; they now target the local API for development. No GitHub push has been performed for this refactor stage.

Current backend test result: 40 passed, 0 failed, with one third-party Starlette/AnyIO deprecation warning. Alembic is at `0006_ownership_foreign_keys`; database integrity, required foreign keys, paper JSON references, and answer ownership are clean.

### Progress Update (2026-09-21, Baseline, Cleanup, and Frontend Runtime)

- Phase 0 is complete: database migration, import verification, integrity checks, backend tests, and local API smoke tests are green.
- The repository no longer tracks 26,454 dependency files, 116 generated build files, 38 Python cache files, `server/.env`, or `client/.env.development`. Local copies were preserved.
- `.gitignore` now matches the intended policy: project memory and sanitized `.env.example` files are tracked; real environment files and generated output are ignored.
- README commands now use `conda activate deng`, MySQL 8.4, `server/.env.local`, the current migration/import workflow, and the verified 40-test baseline.
- Local frontend environment overrides no longer reference the expired temporary tunnel.
- The active uni-app source root is confirmed as `client/src`. Root-level duplicate entry/config files were removed after their valid startup-login logic was merged.
- The frontend now uses one explicit API base URL per build, a configurable 15-second timeout, one network retry for GET requests only, no automatic write retry, one 401 re-login attempt, and normalized request errors.
- Phase 2 is complete for the current `v1` scope: blocking database routes run synchronously, async routes are limited to external HTTP I/O, routers no longer own write commits, all JSON routes have typed OpenAPI envelopes, all errors are normalized, and request IDs correlate client errors with server logs.
- Ownership foreign keys now enforce cascade/restrict policies. Ordered `papers.question_ids` remains JSON by explicit decision until question versioning, per-question scoring, sharing, or SQL analytics justify normalization.
- Phase 3 is complete for local/runtime implementation: one endpoint per environment, production missing-address failure, 15-second timeout, GET-only retry, no write retry, one 401 refresh, deterministic messages, and documented local/LAN/tunnel/production workflows.
- Post-change verification passed: 40 backend tests, Alembic at `0006_ownership_foreign_keys` with no pending operations, clean database integrity, successful WeChat mini-program build, and typed HTTP 200 responses for health, content, question options/detail, user, dashboard, favorites, wrong book, and OpenAPI. Question detail does not expose solution fields.
- Phase 4 is complete: transport is centralized, domain APIs and page-query composables live under `features`, durable state boundaries are documented, shared loading/empty/error/confirmation foundations are available, dead mocks are removed, and active exam progress survives route exit and app background/restart for up to seven days.
- Local runtime incident on 2026-09-21: MySQL84 was healthy, but no FastAPI process was listening on port 8000. Starting Uvicorn restored live content, user, dashboard, option, and paper-generation requests. The frontend now waits for login recovery before loading authenticated home/exam data when those pages are shown.
- Phase 5 direction is approved, but no Phase 5 visual code has started. The next discussion is production server/deployment selection.

## Confirmed Remaining Repository Problems

1. Several legacy Vue pages remain visually large. Their shared architecture is now available, and they should be decomposed only while each Phase 5 vertical slice is redesigned.
2. Production device behavior for local-progress storage still requires WeChat DevTools and physical-device regression during release hardening.
3. Aggregate counters use transactional read-modify-write logic. Unique-key races are handled, but high-volume horizontal scaling would require database-native atomic counter updates and load tests.
4. `papers.question_ids` intentionally remains an ordered JSON snapshot. The decision and triggers for future normalization are recorded in `docs/backend-architecture.md`.
5. The formerly tracked `server/.env` contained a non-placeholder database password. It is no longer tracked in the current tree, but credentials exposed in Git history must be rotated before publication; history rewriting requires a separate explicit decision.
6. The frontend build passes but reports Dart Sass legacy API and `@import` deprecation warnings. These should be addressed with the planned style-system refactor rather than a standalone dependency upgrade.
7. Production WeChat credentials, fixed HTTPS hosting, and physical-device weak-network acceptance remain Phase 6 work; they cannot be completed from the local development configuration alone.

## Agreed Optimization Path

### Phase 0: Establish a Reproducible Green Baseline

1. Fix the related-question correctness failure and run the complete backend test suite.
2. Verify Alembic state, database integrity, importer idempotency, and a minimal real-MySQL API smoke test.
3. Separate the current approved schema/comment work into a focused, reviewable commit.
4. Record exact baseline commands and expected results.

Exit gate: clean working tree after intentional commits, all backend tests pass, database integrity is clean, and the health/core API smoke tests pass.

### Phase 1: Repository Hygiene and Configuration

1. Remove tracked generated artifacts and local dependencies from the Git index: `node_modules`, `dist`, Python caches, test caches, and local runtime output.
2. Stop tracking real `.env` and mode-specific `.local` files; retain sanitized `.env.example` templates only.
3. Decide separately whether Git history should be rewritten. Do not rewrite history without explicit user approval.
4. Consolidate the frontend onto one source root, expected to be `client/src`, after verifying the uni-app build entry behavior.
5. Update README with Conda `deng`, MySQL 8.4, migration, import, start, test, build, and troubleshooting workflows.
6. Add only lightweight, justified repository conventions; do not add dependencies merely for tooling aesthetics.

Exit gate: a clean clone can be configured from documented templates without hidden local files, generated output, or duplicate entry points.

### Phase 2: Backend Structure and Contract Stabilization

Status: complete for the current `v1` scope on 2026-09-21. High-scale counter atomics remain a documented scaling trigger, not a current blocking defect.

1. Preserve domain modules (`user`, `question`, `exam`, `wrongbook`, `favorite`, `content`, `ai`) rather than performing a wholesale rewrite.
2. Make boundaries explicit: router handles HTTP, schemas define contracts, services enforce business rules and transactions, and query persistence is isolated where it reduces coupling.
3. Decide and document synchronous versus asynchronous database access; do not keep async route signatures around blocking work without intent.
4. Standardize errors, pagination, logging/request IDs, transaction ownership, and API response rules.
5. Review foreign keys, deletion/retention policy, paper-question normalization, counter concurrency, and importer natural keys before changing schema relationships.
6. Treat OpenAPI as the authoritative frontend/backend contract and reduce duplicated hand-maintained types.

Exit gate: stable versioned API contracts, explicit transaction/integrity rules, focused tests for every critical learning-loop transition, and no known blocking correctness defects.

### Phase 3: Network and Runtime Reliability

Status: implementation complete on 2026-09-21. Production-host and physical-device acceptance remains part of Phase 6.

1. Use one explicit API endpoint per environment. Remove the expired temporary tunnel and implicit multi-host guessing.
2. Define development, LAN-device, temporary-tunnel, and production configurations separately.
3. Add intentional request timeouts, safe retry rules for idempotent operations, normalized network errors, and observable authentication refresh behavior.
4. Keep localhost for DevTools/H5, allow LAN IP for controlled same-network testing, and use a fixed HTTPS endpoint for production.
5. A permanent traditional server is not required for local development; production still requires a reachable HTTPS API through a VM, container, serverless platform, WeChat cloud hosting, or another stable deployment target.

Exit gate: no recurring `request fail` in local DevTools, deterministic error messages, and a documented path for physical-device testing.

### Phase 4: Frontend Architecture Foundation

Status: complete on 2026-09-21. Visual redesign is intentionally deferred to Phase 5.

1. Establish one app shell, one router/page manifest, one API client, and one environment-loading strategy.
2. Organize frontend code by feature domain while keeping genuinely shared components, types, styles, and utilities centralized.
3. Define the state boundary: Pinia for cross-page durable application state; composables/query helpers for page-scoped server state; pages do not construct URLs or duplicate authentication behavior.
4. Introduce design tokens for color, typography, spacing, radius, elevation, and semantic states.
5. Build reusable loading, empty, error, confirmation, question, answer, result, and navigation components.
6. Add answer-progress persistence and deliberate weak-network/background-resume behavior before visual polish.

Exit gate: new screens can be built without duplicating networking, state logic, or page-level visual rules.

### Phase 5: Incremental Product and Visual Redesign

Status: direction approved on 2026-09-21; implementation paused until the server/deployment discussion is complete.

Confirmed direction: keep `老外1点通`, use a warm academic companion visual language, structure the home page as roughly 70% study dashboard and 30% future real content, and remove fictional placeholder advertising during redesign.

Recommended order:

1. App shell, navigation, and brand system.
2. Study dashboard/home page after its product role is decided.
3. Paper configuration.
4. Answering experience, including audio/image questions and progress recovery.
5. Results and full review.
6. Wrong-book list, detail, redo, and PDF flow.
7. Profile, goals, history, favorites, and AI integration.
8. Decide whether content administration belongs in the learner mini-program or a separate administrative surface.

Each vertical slice must preserve the working learning loop and pass functional/device checks before the next slice begins.

### Phase 6: Release Hardening

1. Production WeChat `code2session`, AppID/secret, fail-closed auth, CORS, and request-domain configuration.
2. Fixed HTTPS endpoint and deployment decision.
3. Database backup/restore rehearsal, migration procedure, logging, rate limits, and secret rotation.
4. WeChat DevTools regression followed by physical-device tests for login, weak network, audio/image questions, PDF preview, long content, background/resume, and token expiry.

Exit gate: documented deployment/rollback process and end-to-end acceptance on a physical device.

## Change and Commit Strategy

- Prefer incremental vertical changes over a big-bang rewrite.
- Keep commits single-purpose: baseline correctness, schema/comment migration, repository hygiene, backend contracts, network layer, frontend foundation, then individual screen redesigns.
- Never mix generated-file cleanup, secret removal, architecture changes, and visual redesign in one commit.
- Preserve user work and review `git status` before and after every stage.
- Run verification proportional to the change: unit tests, Alembic checks, integrity audit, frontend build, and targeted real-API/device smoke tests.
- Do not push, rewrite history, deploy, or publish without the user's explicit approval for that stage.
- Do not create Git commits automatically. Leave changes uncommitted unless the user explicitly requests a commit. The requested V1.3.0 squash is the current one-time exception.

## Environment and Cleanliness Rules

- Do not autonomously download environments, packages, configuration files, binaries, readers, or other tools.
- Python work must use the Conda environment `deng`; do not create `.venv`.
- If another Python version or environment is required, discuss it with the user first.
- Use existing installed tools whenever possible. Ask before introducing any new dependency.
- Never echo or record MySQL passwords, JWT secrets, WeChat secrets, Qwen keys, or other credentials.
- Keep backend and frontend development servers in separate terminals.
- Backend development command from `server`:
  `C:\Users\Theo\miniforge3\envs\deng\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000`
- Frontend development command from `client`:
  `npm.cmd run dev:mp-weixin`
- Retry a network/environment operation at most three times, then report the concrete blocker.

## Immediate Next Decision Gate

Before Phase 5 code work begins, discuss and select the production server/deployment shape. Compare at minimum:

1. A conventional cloud VM with FastAPI, MySQL, reverse proxy, HTTPS, backups, and process supervision.
2. Managed application/container hosting plus managed MySQL.
3. WeChat/Tencent cloud-native hosting where it fits the current FastAPI/MySQL architecture.

Evaluate mainland-China WeChat request-domain requirements, ICP implications, HTTPS/domain ownership, expected traffic, operational effort, database backup/recovery, media storage, AI outbound access, cost, and migration lock-in. Do not purchase, deploy, or create cloud resources without explicit user approval.

## Historical Review and Progress Log

Everything below this heading is historical context. When it conflicts with the authoritative snapshot above, the authoritative snapshot wins.

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

## Progress Update (2026-08-30, Workspace Cleanup and Documentation)

- Removed reproducible intermediate products from the working tree: `client/node_modules`, `client/dist`, `server/.venv`, project pytest caches, and all accessible Python `__pycache__` directories. Dependencies and build output can be regenerated from the lock/requirements files.
- `.test-cache` and `.test-tmp` at the project root were created by an administrator-owned test run. The current account cannot read or delete them (`Access denied`); they remain ignored by Git and can be removed later from an elevated PowerShell.
- Preserved `database/backups/csca_hks_exam_before_alembic_20260816_170437.sql` because it is the pre-migration rollback backup. Preserved the external `E:\Deng\original_question_bank` source data because it is required for full question import and is intentionally outside the repository.
- Updated `.gitignore` so environment templates remain shareable via `!**/.env.example`. `CODEX_MEMORY.md` remains ignored by policy, but it is already tracked in the existing Git index; ignore rules do not remove tracked files automatically.
- Rewrote `README.md` with the current feature status, clean-clone setup, environment configuration, MySQL/Alembic initialization, question import, development startup, verification commands, generated-output policy, and remaining production validation.
- The working tree still records deletions for previously tracked `client/node_modules` and `client/dist` files. Those deletions will take effect when committed; no unrelated source files were reverted.
- Security follow-up: `server/.env` is currently tracked in the existing index. Before publishing, remove it from the index, ensure no secrets are committed, and rotate any credentials that have appeared in Git history. This was not altered automatically because history rewriting is destructive.

### Next Actions

1. Remove the administrator-owned `.test-cache` and `.test-tmp` with elevated permissions when convenient.
2. Reinstall `client` and `server` dependencies from `package-lock.json` and `requirements.txt` before running fresh tests or builds.
3. Clean tracked generated files and the tracked `server/.env` from the Git index, then review the staged diff before publishing.
4. Complete physical-device verification with production WeChat credentials and a reachable HTTPS API endpoint.
