# Technical Note 1: Evaluation Protocol v0.1

## Purpose
The purpose of this project is to build a research-grade evaluation framework for detecting sensitive content using synthetic entreprise ticket-style text. This research underpins designing, building and evaluating secure, dependable AI systems for regulated or high-consequence environments.

*What does sensitive content mean in this project*

Sensitive content in its simplest form can be described as a personally identifiable information. Within a highly regulated environments, data is the biggest asset. These data can contain information of employees, teams, development work, legacy systems etc. This information when exposed can lead to cost and legal consequences. For example, passwords, api keys, ip addresses, etc.

## Research questions
The project compares multiple detector families under privacy-preserving, resource constrained and auditable deployment assumptions:
 
 * regex/ rule-based baseline
 * NER-based detector eg GLiNER
 * prompt-based local LLM detection
 * hybrid detector eg LLM against:
Regex alone.
NER alone.
The union or hybrid of regex and NER.

### RQ1:  Regex versus NER

Does model-based NER improve exact-span detection of contextual personal entities, particularly person names, compared with deterministic rules, and what new boundary and contextual false-positive modes does it introduce?

### RQ2: Incremental value of a local LLM

Does a local instruction-tuned LLM improve contextual sensitive-content detection beyond regex and NER baselines, and is any improvement sufficient to justify its latency, operational complexity, resource requirements, and reduced determinism?

## Entity types
### Included `entity_type` Values

These entity type values included are: 

- `email`
- `phone_number`
- `ip_address`
- `person_name`
- `account_identifier`
- `access_key`
- `token`
- `password`

### Excluded `entity_type` Values

The entity types excluded are:

- `organisation names`:
This is excluded because the system must determine not only whether some text is an organisation, but whether that particular organisation mention is confidential. That is closer to contextual sensitivity classification than ordinary NER. Context-dependent detection of confidential customers, partners, projects, and organisational relationships is reserved for future work.

*TODO: Add further exclusion*

## Dataset design and improvement

