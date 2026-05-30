# Weekly V1 Plan

This plan tracks the first 6-8 weeks of the project as a research-engineering
build. Each week has one major mission, concrete engineering outputs, and a
README/report update so the project grows as both software and research.

Assumed pace: 10-12 hours per week.

## Progress Tracker

| Week | Mission | Status |
| --- | --- | --- |
| 1 | Define the shared data model and dataset schema | Done |
| 2 | Build the first synthetic labelled dataset | Started |
| 3 | Implement the regex detector baseline | Not started |
| 4 | Build the evaluation harness | Not started |
| 5 | Implement the NER detector baseline | Not started |
| 6 | Implement the local LLM detector baseline | Not started |
| 7 | Run comparison experiments and latency benchmarks | Not started |
| 8 | Write failure analysis and polish the research report | Not started |

## Week 1: Shared Models And Dataset Schema

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

## Week 2: Synthetic Labelled Dataset

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
- regex detector for structured targets
- rule IDs and confidence defaults
- privacy-safe result output using masked values
- tests for each regex rule

README/report update:
- describe regex strengths and expected blind spots
- document detector output format
- include first qualitative examples

Done when:
- regex detector runs over the synthetic dataset
- findings use the shared `Finding` format
- tests cover common true positives and false positives

## Week 4: Evaluation Harness

Major mission: make performance measurement reproducible.

Build:
- exact span matching
- optional overlap-based span matching
- precision, recall, and F1 metrics
- per-entity metrics
- false positive and false negative extraction
- baseline experiment script

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
- NER detector interface implementation
- local model loading strategy
- mapping from NER labels to project `EntityType` values
- latency measurement for the NER detector
- tests using mocked model outputs

README/report update:
- document model choice and local inference constraints
- compare regex vs NER at a high level
- add early observations about names and contextual ambiguity

Done when:
- NER detector runs locally or has a clean optional dependency path
- NER results are evaluated with the same harness
- per-entity metrics compare regex and NER

## Week 6: Local LLM Detector Baseline

Major mission: implement the prompt-based local LLM detector.

Build:
- prompt template for sensitive-content detection
- structured JSON response parsing
- validation from LLM outputs into `Finding` objects
- timeout/error handling
- tests for parser behavior using fixed mock responses

README/report update:
- document the prompt design
- explain privacy assumptions for local inference
- compare where LLM detection may add contextual value

Done when:
- local LLM detector can run on a subset of samples
- outputs are converted into the shared finding format
- failures are captured without breaking the full experiment

## Week 7: Comparison Experiments And Benchmarking

Major mission: run the first full detector comparison.

Build:
- experiment runner for regex, NER, and LLM detectors
- latency benchmark script
- aggregated metrics tables
- per-entity comparison outputs
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
