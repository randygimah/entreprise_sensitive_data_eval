# Project Handoff

## Goal

Build a research-grade evaluation framework for detecting sensitive content in
synthetic enterprise ticket-style text.

The project compares multiple detector families under privacy-preserving,
resource-constrained, and auditable deployment assumptions:

- regex / rule-based baseline
- NER-based detector
- prompt-based local LLM detector
- optional hybrid detector

The intended v1 output is a portfolio-quality AI research-engineering artifact
with:

- realistic synthetic enterprise samples
- labelled sensitive spans
- shared detector output format
- privacy-safe masking/hashing
- precision, recall, and F1 evaluation
- latency/runtime comparison
- failure-mode analysis
- mini-paper-style README/report

## Current State

Weeks 1 and 2 are mostly complete.

Implemented so far:

- Core immutable data models in `sensitive_eval/core/models.py`
  - `EntityType`
  - `SourceType`
  - `DifficultyLevel`
  - `TextSpan`
  - `SensitiveSpan`
  - `Finding`
  - `DatasetSample`
  - `DetectorResult`
- JSONL dataset loader/writer in `sensitive_eval/dataset/loaders.py`
- Synthetic dataset schema docs in `docs/dataset_schema.md`
- Dataset planning table in `docs/dataset_plan.md`
- Canonical synthetic dataset in `data/synthetic_samples.jsonl`
  - 40 samples
  - 93 labelled spans
  - all core entity types represented
  - all source types represented
- Dataset validation tests in `tests/test_synthetic_dataset.py`
- Postprocessing helpers:
  - masking in `sensitive_eval/postprocessing/masking.py`
  - SHA-256 hashing in `sensitive_eval/postprocessing/hashing.py`
- Postprocessing tests in `tests/test_postprocessing.py`
- Detector base interface started in `sensitive_eval/detectors/base.py`

Current verification snapshot:

- `pytest --tb=short`: 27 passed
- `mypy sensitive_eval`: passed
- `flake8 sensitive_eval tests`: failing on formatting/style issues
- `black --check sensitive_eval tests`: failing because
  `tests/test_synthetic_dataset.py` needs formatting

## Files In Flight

Active or recently touched files:

- `sensitive_eval/core/models.py`
  - contains the shared models
  - currently also contains `RegexRule`, but that should probably move into
    `sensitive_eval/detectors/regex_detector.py` because it is detector-specific
- `sensitive_eval/detectors/base.py`
  - defines `BaseDetector`
  - should be cleaned up slightly before the regex detector depends on it
- `sensitive_eval/detectors/regex_detector.py`
  - currently only has a starter docstring
  - next major implementation target
- `sensitive_eval/postprocessing/masking.py`
  - has masking helpers used by future detector findings
- `sensitive_eval/postprocessing/hashing.py`
  - has deterministic SHA-256 hashing helper
- `tests/test_postprocessing.py`
  - tests masking and hashing helpers
- `tests/test_synthetic_dataset.py`
  - validates the real JSONL dataset
  - passes, but needs Black/Flake8 formatting cleanup
- `docs/weekly_v1_plan.md`
  - Week 3 has started
  - Week 2 status may need to be changed from `Started` to `Done`

## Changed

Most recent work focused on preparing Week 3:

- Discussed the regex detector pipeline.
- Confirmed detector contract should be:
  - `detect(sample: DatasetSample) -> DetectorResult`
  - one `DetectorResult` per sample
  - many `Finding` objects inside `DetectorResult.findings`
- Added/started `BaseDetector` in `sensitive_eval/detectors/base.py`.
- Started `regex_detector.py` with an initial module docstring.
- Added postprocessing helpers for privacy-safe output:
  - `mask_value`
  - `mask_email`
  - `mask_ip_address`
  - `mask_keep_prefix`
  - `mask_keep_edges`
  - `mask_person_name`
  - `hash_value`
- Added tests for postprocessing helpers.
- Fixed a Python 3.9 compatibility issue in `RegexRule`:
  - changed `str | None` to `Optional[str]`

## Failed Attempts

Known issues and lessons:

- `DetectorResult` should not be returned as a list from a detector.
  - Correct shape is `DetectorResult(findings=tuple(...))`.
- `Finding` should not store raw matched values.
  - Use `masked_value` and derive raw text only transiently from regex matches.
- `mask_value` originally compared enum values to strings like `"password"`.
  - Correct comparison is `entity_type == EntityType.PASSWORD`.
- Early masking helpers had string-indexing and string/int concatenation bugs.
  - These were fixed and covered with tests.
- `RegexRule` was added to `core/models.py`, but this is probably the wrong
  long-term home.
  - It is specific to the regex detector and should likely move into
    `regex_detector.py`.
- Full style checks are not clean yet.
  - `pytest` and `mypy` pass.
  - `flake8` fails on formatting in:
    - `sensitive_eval/dataset/synthetic_generator.py`
    - `sensitive_eval/detectors/base.py`
    - `tests/test_synthetic_dataset.py`
  - `black --check` fails on `tests/test_synthetic_dataset.py`.

## Next Step

Continue Week 3: implement the regex detector baseline.

Recommended next sequence:

1. Clean up formatting/style blockers. ✅
   - Run Black on `tests/test_synthetic_dataset.py`.
   - Shorten long docstring/comment lines in `base.py` and
     `synthetic_generator.py`.
2. Finalize `BaseDetector`.
   - Keep only the abstract interface in `base.py`.
   - Ensure the method is lowercase: `detect`.
3. Move `RegexRule` from `core/models.py` into `regex_detector.py`.
   - It is detector-specific, not a shared core model.
4. Implement compiled regex patterns in `regex_detector.py`.
   - email
   - IPv4 address
   - phone number
   - AWS/access-key-like strings
   - token-like strings
   - contextual password disclosures
   - possibly account identifiers
5. Implement `RegexDetector.detect`.
   - Iterate through rules with `pattern.finditer(sample.text)`.
   - Use named capture groups for contextual password rules so the span covers
     only the sensitive value.
   - Create `Finding` objects with:
     - `TextSpan`
     - `EntityType`
     - `detector_name="regex"`
     - `confidence_score`
     - `masked_value`
     - `rule_id`
   - Return one `DetectorResult` per sample.
6. Add `tests/test_regex_detector.py`.
   - Unit test each regex rule.
   - Test that raw matched values are not stored.
   - Test that detector output uses the shared `Finding` format.
   - Add a smoke test over `data/synthetic_samples.jsonl`.

After Week 3, the project should have a working deterministic baseline that can
run over the 40-sample synthetic dataset. Evaluation metrics come next in Week 4.
