# Backend Architecture Decisions

This document records the backend rules for API version `v1`. These are implementation constraints, not aspirational diagrams.

## Execution model

- SQLAlchemy uses the synchronous PyMySQL driver.
- Routes that perform database work are synchronous `def` handlers so FastAPI runs them in its worker thread pool.
- Async handlers are reserved for real asynchronous I/O, such as WeChat code exchange. The retained Qwen HTTP implementation is not exposed in1.5.3.
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

Stable source question_id maps to unique questions.bank_id. Corrections update the same row even when the stem or answer changes. Unnumbered legacy records retain the earlier natural-key parser. Full source metadata stays private in source_data; serializers explicitly allow public and post-submission fields. See question-bank-import-contract.md.

## Versioned bank and assessment

- HSK generation requires a version and level; CSCA uses subjects and knowledge modules.
- Shared materials keep related questions contiguous and complete. Timed practice uses per-level non-oral module profiles and refuses insufficient inventory.
- Practice and exam generation both redact solutions. Practice submission returns its solution; finished exam results return solutions.
- Only multi-select grading ignores order. Character responses retain order and declared acceptable variants.
- Open expression stores is_correct=NULL, a self-review status and score. Completion includes these submissions; automatic accuracy and wrong-book aggregation exclude them.
- Media routes expose only permitted binary assets. Source JSON and audio maintenance records remain private.

## Concurrency

- Unique constraints protect login identity, one answer per paper question, favorites, wrong-book rows, knowledge statistics, streak dates, and exam targets.
- User creation, answer submission, and favorite toggling recover from uniqueness races with a bounded retry after rollback.
- Write requests are not retried automatically by the frontend.
- Counter updates remain part of the same answer transaction. If production load introduces concurrent high-volume submissions for one user or question, replace read-modify-write counters with database-native atomic statements and add load tests before scaling horizontally.

## Feedback, announcements and AI rules (1.5.1)

- Private feedback and content administration require an explicit valid JWT, without the anonymous development fallback. Admin access uses `CONTENT_ADMIN_OPENIDS`.
- Feedback ownership comes from the token. Submissions use a per-user idempotency key, a user-row lock and bounded frequency checks; public receipts contain no feedback body or user identifiers. Only admins can list or change feedback status.
- Versioned announcements reuse `content_items`. Public lists and details filter inactive and future publications; normal reads no longer seed demo content. Migration0008 adds the new table/columns and an unpublished release-notes draft, preserving learning data.
- Only the backend constructs AI system messages. User-supplied question/topic/context stays in a user message; inbound chat roles are restricted to user/assistant. HKS is displayed as HSK in the prompt.
- See [release-1.5.1.md](release-1.5.1.md) for contracts and incremental deployment steps.

## AI withdrawal (1.5.3)

The API aggregator no longer imports or mounts the AI router. `/api/v1/ai/chat` returns404 and AI contracts are absent from OpenAPI; the implementation under `modules/ai` and its configuration remain available for a future restoration. No other business route or authentication rule changes. Migration0010 adds only the approved1.5.3 announcement, preserving existing data and editorial records. See [release-1.5.3.md](release-1.5.3.md).
