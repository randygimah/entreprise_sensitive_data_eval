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

Weeks 1 and 2 are complete. Week 3 has a working regex detector baseline and
focused tests.

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
- Detector base interface in `sensitive_eval/detectors/base.py`
- Regex detector baseline in `sensitive_eval/detectors/regex_detector.py`
  - email addresses
  - IPv4 addresses
  - AWS/access-key-like strings
  - contextual password disclosures
  - token-like secrets
- Regex detector tests in `tests/test_regex_detector.py`

Current verification snapshot:

- `pytest --tb=short`: 33 passed
- `mypy sensitive_eval`: passed

## Files In Flight

Active or recently touched files:

- `sensitive_eval/core/models.py`
  - contains the shared models
- `sensitive_eval/detectors/base.py`
  - defines `BaseDetector`
- `sensitive_eval/detectors/regex_detector.py`
  - contains detector-specific `RegexRule`
  - contains `DEFAULT_RULES`
  - returns one `DetectorResult` per sample with many `Finding` objects
- `sensitive_eval/postprocessing/masking.py`
  - has masking helpers used by future detector findings
- `sensitive_eval/postprocessing/hashing.py`
  - has deterministic SHA-256 hashing helper
- `tests/test_postprocessing.py`
  - tests masking and hashing helpers
- `tests/test_synthetic_dataset.py`
  - validates the real JSONL dataset
- `tests/test_regex_detector.py`
  - covers current regex rules and multi-finding output
- `docs/weekly_v1_plan.md`
  - Week 1 and Week 2 are marked `Done`
  - Week 3 should be marked `Started`

## Changed

Most recent work focused on implementing the Week 3 regex baseline:

- Discussed the regex detector pipeline.
- Confirmed detector contract should be:
  - `detect(sample: DatasetSample) -> DetectorResult`
  - one `DetectorResult` per sample
  - many `Finding` objects inside `DetectorResult.findings`
- Added `BaseDetector` in `sensitive_eval/detectors/base.py`.
- Implemented `RegexDetector.detect`.
- Moved detector-specific `RegexRule` into `regex_detector.py`.
- Added `DEFAULT_RULES` for email, IPv4 address, AWS/access-key-like strings,
  contextual passwords, and token-like secrets.
- Used named capture groups for contextual passwords so spans cover only the
  secret value, not the surrounding phrase.
- Added masked detector output through `mask_value`.
- Added postprocessing helpers for privacy-safe output:
  - `mask_value`
  - `mask_email`
  - `mask_ip_address`
  - `mask_keep_prefix`
  - `mask_keep_edges`
  - `mask_person_name`
  - `hash_value`
- Added tests for postprocessing helpers.
- Added regex detector tests for individual rule behavior and multiple findings
  inside one `DetectorResult`.
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
- `RegexRule` was initially considered as a core model, but that was the wrong
  boundary.
  - It now lives in `regex_detector.py` because it is detector-specific.
- A detector named-group span bug used `match.start(...)` for both start and
  end.
  - Correct implementation uses `match.end(...)` for the end offset.
- The initial password regex only handled `password:` and `password=`.
  - It now also catches natural-language phrasing such as `password is ...`.
- Full style checks should be rerun before the next checkpoint.

## Next Step

Continue Week 3 polish, then move into Week 4 evaluation.

Recommended next sequence:

   - Run Black on `tests/test_synthetic_dataset.py`.
1. Finalize `BaseDetector`. ✅
   - Keep only the abstract interface in `base.py`.
   - Ensure the method is lowercase: `detect`.
2. Move `RegexRule` from `core/models.py` into `regex_detector.py`.✅
   - It is detector-specific, not a shared core model.
3. Implement compiled regex patterns in `regex_detector.py`.✅
   - email
   - IPv4 address
   - AWS/access-key-like strings
   - token-like strings
   - contextual password disclosures
4. Implement `RegexDetector.detect`.✅
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
5. Add `tests/test_regex_detector.py`.
   - Unit test each regex rule. ✅
   - Test that raw matched values are not stored.
   - Test that detector output uses the shared `Finding` format. ✅
   - Add a smoke test over `data/synthetic_samples.jsonl`.
   - Add false-positive guards for token-like strings.
6. Optional remaining Week 3 detector coverage:
   - phone number rule
   - account identifier rule, if useful as a regex baseline
   - smoke test that runs the regex detector over all 40 synthetic samples

After Week 3, the project should have a working deterministic baseline that can
run over the 40-sample synthetic dataset. Evaluation metrics come next in Week 4.
