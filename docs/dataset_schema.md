# Dataset Schema

This document defines the JSONL dataset schema used for synthetic enterprise
text samples and their sensitive-content span labels.

## Purpose

The dataset uses JSONL, also known as JSON Lines, where each line is one
independently loadable labelled enterprise text sample. Each line is a
self-contained JSON object.

JSONL is used because it is easy to append, diff, stream, and inspect. It also
makes row-level errors easy to locate when validation fails.

## Top-Level Sample Fields

Each row has this shape:

```json
{
  "sample_id": "sample-001",
  "text": "Support ticket text...",
  "source_type": "support_ticket",
  "difficulty": "easy",
  "metadata": {},
  "labels": []
}
```

A complete example:

```json
{
  "sample_id": "sample-001",
  "text": "Contact alice@example.com for access.",
  "source_type": "support_ticket",
  "difficulty": "easy",
  "metadata": {
    "team": "support"
  },
  "labels": [
    {
      "span": {
        "start": 8,
        "end": 25
      },
      "entity_type": "email",
      "text": "alice@example.com",
      "notes": null
    }
  ]
}
```

## Sample Fields

- `sample_id`: non-empty string identifier for the sample.
- `text`: non-empty raw synthetic enterprise text.
- `source_type`: source category for the sample.
- `difficulty`: optional difficulty label, or `null`.
- `metadata`: optional key-value metadata object.
- `labels`: list of sensitive-content span labels.

## Allowed `source_type` Values

These values come from `SourceType` in `sensitive_eval/core/models.py`:

- `support_ticket`
- `incident_report`
- `change_request`
- `operational_note`
- `internal_comment`
- `config_snippet`
- `attachment_text`

## Allowed `difficulty` Values

These values come from `DifficultyLevel` in `sensitive_eval/core/models.py`:

- `easy`
- `medium`
- `hard`
- `null`

## Label Schema

Each label identifies one sensitive span inside the sample text:

```json
{
  "span": {
    "start": 8,
    "end": 25
  },
  "entity_type": "email",
  "text": "alice@example.com",
  "notes": "Employee contact email."
}
```

## Label Fields

- `span.start`: inclusive character offset where the labelled span begins.
- `span.end`: exclusive character offset where the labelled span ends.
- `entity_type`: sensitive-content category for the span.
- `text`: optional labelled text. When provided, it must match
  `sample["text"][start:end]`.
- `notes`: optional annotation note.

## Allowed `entity_type` Values

These values come from `EntityType` in `sensitive_eval/core/models.py`:

- `email`
- `phone_number`
- `ip_address`
- `person_name`
- `account_identifier`
- `access_key`
- `token`
- `password`

## Span Convention

Spans use Python slicing semantics:

- `start` is inclusive.
- `end` is exclusive.

That means:

```python
sample["text"][start:end] == label["text"]
```

Example:

```python
text = "Contact alice@example.com"
start = 8
end = 25

assert text[start:end] == "alice@example.com"
```

## Validation Rules

The loader enforces these rules:

- `sample_id` must be a non-empty string.
- `text` must be a non-empty string.
- `source_type` must match a known source type.
- `difficulty` must be known or `null`.
- label spans must be valid.
- label spans must be inside the sample text.
- if `label.text` is provided, it must match `text[start:end]`.

## Privacy Note

This dataset is synthetic only. Public artifacts should avoid real secrets,
customer data, and personally identifiable information.

Future result files should store masked values or deterministic hashes, not raw
sensitive findings.

## Example JSONL Row

```json
{"difficulty":"medium","labels":[{"entity_type":"ip_address","notes":"Internal service IP address.","span":{"end":36,"start":26},"text":"10.24.8.15"},{"entity_type":"token","notes":"Token-like secret pasted into operational text.","span":{"end":80,"start":56},"text":"sk_live_51HxExampleToken"}],"metadata":{"created_for":"seed_dataset","split":"dev"},"sample_id":"sample-002","source_type":"incident_report","text":"Incident note: service at 10.24.8.15 failed after token sk_live_51HxExampleToken was pasted into chat."}
```
