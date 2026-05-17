## Dataset Format

Synthetic samples are stored as JSONL, with one labelled enterprise text sample per line. Each sample contains raw text, source type, optional difficulty/metadata, and labelled sensitive spans using inclusive-start, exclusive-end character offsets.

See `docs/dataset_schema.md` for the full schema and validation rules.

## Synthetic dataset

40 synthetic datasets that mimic realistic enterprise datasets are generated and validated. A dataset table plan was first built before the dataset was generated to ensure balance across source types, entity types, and
difficulty levels.

See `docs/dataset_plan.md` for the full dataset plan

 The dataset simulates enterprise text sources such as support tickets, internal comments, change requests, operational notes, config snippets and attachment texts. Each appears atleast 5 times in the dataset.

See `data/synthetic_samples.jsonl` for the full dataset generated




