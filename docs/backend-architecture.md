# Backend Architecture Decisions

This document records the backend rules for API version `v1`. These are implementation constraints, not aspirational diagrams.

## Execution model

- SQLAlchemy uses the synchronous PyMySQL driver.
- Routes that perform database work are synchronous `def` handlers so FastAPI runs them in its worker thread pool.
- Async handlers are reserved for real asynchronous I/O. The current examples are WeChat code exchange and the Qwen HTTP request.
- The WeChat login route completes its database work in a worker thread with a worker-owned session.
- A full async SQLAlchemy migration is not justified unless profiling demonstrates database-thread saturation.

## Module boundaries

- `router.py` owns HTTP parsing, dependencies, permissions, and response wrapping.
- `schemas.py` owns request and response contracts exposed through OpenAPI.
- `service.py` owns business rules and write transactions.
- `models.py` owns persistence mapping and database constraints.
- A repository layer is introduced only when a query is reused or complex enough to obscure a service. Simple SQLAlchemy queries stay in the service.

Routers must not call `commit()`. Write services commit only after all related aggregates are updated. The database dependency rolls back any unhandled transaction before closing its session.

## API contract

Successful JSON responses use:

```json
{
  "code": 0,
  "message": "成功",
  "data": {},
  "request_id": "opaque-request-id"
}
```

Application, HTTP, validation, and unexpected errors use the same envelope with a non-zero code. Validation responses expose field and rule information but never echo the rejected input. Unexpected errors never expose internal exception text.

The `X-Request-ID` request header is accepted when it contains a short safe identifier. Otherwise the server generates an ID. The same ID is returned in the response header and JSON envelope and is written to request logs.

OpenAPI response models are the authoritative backend contract. Frontend TypeScript interfaces still mirror these models manually and should be generated or contract-tested in the frontend foundation phase.

## List and pagination policy

Version `v1` preserves its existing array response shapes to avoid breaking the mini-program. Bounded endpoints use a validated `limit`. The wrong-book filtered list remains an array because the current UI loads the complete filtered result for PDF and redo workflows. Any endpoint that can grow beyond this use case must introduce a new paginated contract rather than silently changing an existing response shape.

## Referential integrity and deletion

- User-owned rows cascade when a user is deleted: papers, answers, wrong-book entries, knowledge statistics, streak records, favorites, and exam targets.
- Answers cascade when their paper is deleted.
- Question references use `RESTRICT`; questions are retired through `is_active` rather than hard-deleted.
- Migration `0006_ownership_foreign_keys` refuses to run when orphan rows exist.
- `scripts/check_database_integrity.py` verifies ownership, JSON paper references, owner consistency, and required foreign keys.

## Paper question snapshot

`papers.question_ids` remains an ordered JSON snapshot in `v1`. It is compact, preserves question order, and matches the current immutable generated-paper behavior. Replacing it with a `paper_questions` table would add migration and ordering complexity without fixing a current correctness defect. Normalize it only when question versioning, per-question scoring, shared papers, or SQL-level paper analytics become requirements.

## Import identity

The importer natural key is the tuple of exam type, subject, knowledge point, question type, normalized stem, and answer. Source duplicates are removed before database writes, and reruns update the matching row. A database unique index is intentionally not added because the stem is `TEXT` and source corrections may legitimately change the answer; importer verification remains the controlled write path.

## Concurrency

- Unique constraints protect login identity, one answer per paper question, favorites, wrong-book rows, knowledge statistics, streak dates, and exam targets.
- User creation, answer submission, and favorite toggling recover from uniqueness races with a bounded retry after rollback.
- Write requests are not retried automatically by the frontend.
- Counter updates remain part of the same answer transaction. If production load introduces concurrent high-volume submissions for one user or question, replace read-modify-write counters with database-native atomic statements and add load tests before scaling horizontally.
