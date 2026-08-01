"""Test for validating actual benchmark sample dataset"""

from pathlib import Path

from sensitive_eval.core.models import (
    DifficultyLevel,
    EntityType,
    SourceType,
)
from sensitive_eval.dataset.loaders import (
    load_jsonl,
)

# Project root below ensures the test can be run regardless of where pytest is
# called from.
# Path(__file__).resolve().parents[1] is /repo path.
# Path(__file__).resolve().parents[0] will be /repo/tests path
# Path(__file__).resolve() will be /repo/tests/test_synthetic_dataset.py repo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "synthetic_samples.jsonl"


def test_file_loads_successfully() -> None:
    samples = load_jsonl(DATASET_PATH)

    assert len(samples) == 40


def test_sample_ids_unique() -> None:
    samples = load_jsonl(DATASET_PATH)
    sample_ids = [sample.sample_id for sample in samples]

    assert len(sample_ids) == len(set(sample_ids))


def test_label_text_aligns_raw_text() -> None:
    samples = load_jsonl(DATASET_PATH)
    for sample in samples:
        for label in sample.labels:
            assert sample.text[label.span.start : label.span.end] == label.text


def test_entity_type_appears_once() -> None:
    samples = load_jsonl(DATASET_PATH)
    observed_entities = {
        label.entity_type for sample in samples for label in sample.labels
    }
    assert (observed_entities) == set(EntityType)


def test_source_type_appears_once() -> None:
    samples = load_jsonl(DATASET_PATH)
    observed_source_types = {sample.source_type for sample in samples}
    assert (observed_source_types) == set(SourceType)


def test_every_difficulty_level_appears() -> None:
    samples = load_jsonl(DATASET_PATH)
    observed_difficulty = {sample.difficulty for sample in samples}
    assert (observed_difficulty) == set(DifficultyLevel)
