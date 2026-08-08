# Weekly V1 Plan

This plan tracks the first 6-8 weeks of the project as a research-engineering
build. Each week has one major mission, concrete engineering outputs, and a
README/report update so the project grows as both software and research.

Assumed pace: 10-12 hours per week.

## Progress Tracker

| Week | Mission | Status |
| --- | --- | --- |
| 1 | Define the shared data model and dataset schema | Done |
| 2 | Build the first synthetic labelled dataset | Done |
| 3 | Implement the regex detector baseline | Started |
| 4 | Build the evaluation harness | Not started |
| 5 | Implement the NER detector baseline | Not started |
| 6 | Implement the local LLM detector baseline | Not started |
| 7 | Run comparison experiments and latency benchmarks | Not started |
| 8 | Write failure analysis and polish the research report | Not started |

## Week 1: Shared Models And Dataset Schema✅

Major mission: define the core data contracts that every detector, evaluator,
and report will use.

Build:
- `TextSpan`, `SensitiveSpan`, `Finding`, and `DetectorResult` ✅
- shared enums for entity types, source types, and difficulty levels ✅
- `DatasetSample` schema ✅
- validation tests for span boundaries and sample labels ✅

README/report update:
- describe the shared finding format ✅
- explain why consistent span-based evaluation matters ✅
- document the initial entity taxonomy ✅

Done when:
- core models are implemented and immutable
- dataset samples can represent raw text plus labelled sensitive spans
- tests cover valid and invalid spans

## Week 2: Synthetic Labelled Dataset✅

Major mission: create a small but realistic synthetic enterprise dataset.

Build:
- hand-authored seed samples across support tickets, incident reports, change
  requests, operational notes, comments, and config snippets ✅
- labelled spans for emails, phone numbers, IP addresses, names, account IDs,
  access-key-like secrets, token-like secrets, and password disclosures ✅
- JSONL loader and saver ✅
- tests that confirm labels align with the source text ✅

README/report update:
- document the dataset design ✅
- explain why synthetic data is used ✅
- include examples with masked sensitive values ✅

Done when:
- at least 40 labelled samples exist
- every core entity type appears in the dataset
- the loader validates all labels against the raw text

## Week 3: Regex Detector Baseline

Major mission: implement the deterministic baseline.

Build:
- detector base interface ✅
- regex detector for structured targets ✅
- phone-number rule with digit-count, boundary, and negative-case tests ✅
- rule IDs and confidence defaults ✅
- privacy-safe result output using masked values ✅
- tests for each implemented regex rule ✅
- false-positive guards for password, token, access-key, and phone-like strings ✅
- deterministic finding order and repeated-run regression test ✅
- dataset-wide smoke test over the development JSONL
- document the supported and intentionally unsupported regex entity types ✅

README/report update:
- describe regex strengths and expected blind spots ✅
- document detector output format ✅
- include first qualitative examples ✅

Done when:
- regex detector runs over representative synthetic samples ✅
- findings use the shared `Finding` format ✅
- tests cover common true positives ✅
- all rule-level positive, negative, masking, and exact-boundary tests pass ✅
- the detector processes the full development dataset without errors
- outputs are deterministic and contain no raw matched values ✅
- the frozen rule set and baseline version are documented ✅

## Week 4: Evaluation Harness

Major mission: make performance measurement reproducible.

Build:
- pure exact-span match predicate with boundary and wrong-entity tests
- one-to-one exact matching over prediction and gold collections
- secondary one-to-one overlap diagnostic using the frozen IoU >= 0.5 threshold
- TP, FP, FN, and boundary-error extraction
- micro, macro, and per-entity precision, recall, and F1 metrics
- zero-denominator behavior defined in Evaluation Protocol v0.1
- results by source type, difficulty, and challenge tag
- false-positive count and false-positive ticket rate for zero-label samples
- false positive and false negative extraction
- privacy-safe result serialization with no raw text or value-derived hashes
- baseline experiment script and one clean evaluation command

README/report update:
- define the evaluation protocol
- explain exact vs overlap matching
- publish first regex baseline metrics

Done when:
- one command evaluates the regex detector on the dataset
- metrics are saved under `results/`
- README includes the first results table

## Week 5: NER Detector Baseline

Major mission: add a model-based detector for names and contextual entities.

Build:
- implement the `BaseDetector` adapter for `nvidia/gliner-PII`
- keep GLiNER as an optional dependency with lazy local model loading
- pin the model repository revision, GLiNER/PyTorch versions, and device
- prefer the published `safetensors` weights where supported
- inventory native GLiNER labels and map supported labels to project
  `EntityType` values
- explicitly document project entity types that the NER model does not support
- validate model character offsets against the source text and exact-span policy
- test label mapping, confidence filtering, offsets, empty results, and model
  failures using mocked outputs
- tune the confidence threshold on development data only using a predefined
  threshold grid and selection criterion
- freeze the model revision, mapping, and threshold before held-out evaluation
- measure model-load time separately from per-sample inference latency

README/report update:
- document model choice and local inference constraints
- compare regex vs NER at a high level
- add early observations about names and contextual ambiguity

Done when:
- NER detector runs locally or has a clean optional dependency path
- the pinned `nvidia/gliner-PII` revision is reproducible from configuration
- native labels, unsupported entities, and the development-tuned threshold are
  documented
- mocked tests do not require downloading or loading the model
- NER results are evaluated with the same harness
- per-entity metrics compare regex and NER

## Week 6: Local LLM Detector Baseline

Major mission: implement the prompt-based local LLM detector.

Build:
- verify the local Ollama runtime on the target M4 Pro hardware
- pre-register a development-only model pilot and selection rule, initially
  comparing `qwen3:30b-instruct` with `gpt-oss:20b`
- pin the selected model name, immutable digest, quantisation, Ollama version,
  context length, and hardware configuration
- version the sensitive-content prompt and project entity definitions
- request non-streaming structured output using an explicit JSON Schema
- validate structured responses with Pydantic before creating findings
- validate entity types, offsets, and source-text alignment, including repeated
  values and ambiguous spans
- use a frozen decoding configuration such as temperature 0 and disabled or
  minimal reasoning where supported
- implement timeout, unavailable-model, malformed JSON, schema failure,
  invalid-span, and empty-result handling
- sanitize exceptions and ensure prompts and raw ticket text are not persisted
  in result artifacts or logs
- test parsing and all failure paths using fixed mocked responses
- measure schema-valid rate, invalid-span rate, model-load time, p50/p95 latency,
  throughput, and repeated-run agreement on development data
- freeze the model, prompt, parser, and decoding configuration before held-out
  evaluation

README/report update:
- document the prompt design
- explain privacy assumptions for local inference
- compare where LLM detection may add contextual value

Done when:
- local LLM detector can run on a subset of samples
- outputs are converted into the shared finding format
- failures are captured without breaking the full experiment
- the selected model and immutable runtime configuration are reproducible
- model selection and prompt tuning use development data only
- repeated runs and privacy-safe logs are covered by tests

## Week 7: Comparison Experiments And Benchmarking

Major mission: run the first full detector comparison.

Build:
- experiment runner for regex, NER, and LLM detectors
- latency benchmark script
- aggregated metrics tables
- per-entity comparison outputs
- regex-plus-NER union/hybrid comparison for measuring incremental LLM value
- exact-match, boundary-error, source, difficulty, challenge-tag, and negative
  ticket breakdowns
- model-load time, p50/p95 inference latency, throughput, and resource metadata
- result artifacts that avoid raw sensitive values

README/report update:
- publish detector comparison tables
- include latency and resource observations
- summarize which method works best for each entity type

Done when:
- all available detectors run through the same pipeline
- results are reproducible from documented commands
- metrics and latency artifacts are saved under `results/`

## Week 8: Failure Analysis And Research Report

Major mission: turn the project into a portfolio-quality research artifact.

Build:
- false positive and false negative categorization
- representative masked examples
- tradeoff analysis across quality, latency, privacy, and auditability
- final README/report structure

README/report update:
- write the mini-paper-style findings
- add limitations and future work
- connect results back to the research question

Done when:
- README explains the research question, method, results, and limitations
- failure modes are documented with masked examples
- the repo can be shown as a coherent v1 research-engineering project

## Optional Buffer / Extension Week

Use this week if earlier work takes longer than expected or if the v1 needs one
extra polish pass.

Possible missions:
- implement a simple hybrid detector
- add plots for metrics and latency
- improve synthetic dataset difficulty categories
- add more robust privacy-safe serialization
- prepare thesis proposal notes from the README/report

## Weekly Review Ritual

At the end of each week:
- mark the week status as complete or partially complete
- add one short README update
- record what changed in the project
- record one research observation or open question
- choose the next week's exact implementation target
