# Question Bank Import Contract

Date: 2026-08-11

The importer reads the sibling folder `E:\Deng\original_question_bank` and normalizes importable exam questions into the existing `questions` table.

## Supported Sources

1. Canonical question lists

   Files shaped as a JSON list whose records already contain `stem_text`, `options`, and `answer`.

   Required normalized fields:

   - `exam_type`: `CSCA` or `HKS`; source folder name `HSK` is mapped to database enum value `HKS`.
   - `subject`
   - `knowledge_point`
   - `difficulty`: `easy`, `medium`, or `hard`
   - `question_type`: `single`, `multi`, `judge`, or `fill`
   - `stem_text`
   - `options`: list of `{ key, text }`; blank options are ignored for `fill` questions.
   - `answer`

2. HSK4 raw quiz files

   Files shaped as an object with a `questions` list, such as `HSK\4级\raw_test_01.json`.

   Mapping:

   - `listening_true_false` -> `judge`, subject `听力`, knowledge point `听力判断`
   - `listening_choice` -> `single`, subject `听力`, knowledge point `听力选择`
   - `reading_comprehension` -> `single`, subject `阅读`, knowledge point `阅读理解`
   - `reading_ordering` -> `single`, subject `阅读`, knowledge point `语序排列`
   - `fill_in_blank` -> `single`, subject `阅读`, knowledge point `选词填空`
   - `writing_construction` -> `fill`, subject `书写`, knowledge point `完成句子`

   `audio` and `image` are preserved as `stem_audio` and `stem_image`. Explanations and source IDs are preserved in `analysis`.

## Skipped Resources

The current database schema stores exam questions only. These learning-resource files are parsed as valid JSON but skipped by design:

- `HSK\4级\grammar-patterns.json`
- `HSK\4级\sentences.json`
- `HSK\4级\vocabulary.json`

They should receive dedicated tables or a richer learning-resource model before import.

## Idempotency

The importer uses this natural key to avoid duplicate rows:

`exam_type + subject + knowledge_point + question_type + stem_text + answer`

When run with `--apply`, existing rows with the same key are updated; otherwise new rows are inserted.

## Commands

Dry-run validation:

```powershell
server\.venv\Scripts\python.exe scripts\import_questions.py
```

Apply to the configured MySQL database:

```powershell
server\.venv\Scripts\python.exe scripts\import_questions.py --apply
```

Verify database counts after import:

```powershell
server\.venv\Scripts\python.exe scripts\import_questions.py --verify-db
```

Database-backed commands automatically load `server/.env`, so they can be run from the project root.

Current dry-run result:

- Importable questions: 2562
- Source duplicates skipped: 128
- Exam counts: `CSCA=265`, `HKS=2297`
- Skipped non-question resources: 1018 records
