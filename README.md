## Dataset Format

Synthetic samples are stored as JSONL, with one labelled enterprise text sample per line. Each sample contains raw text, source type, optional difficulty/metadata, and labelled sensitive spans using inclusive-start, exclusive-end character offsets.

See `docs/dataset_schema.md` for the full schema and validation rules.
