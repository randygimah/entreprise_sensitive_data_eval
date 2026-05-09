"""Tests for JSONL dataset loading and writing."""

import json
import re

import pytest

from sensitive_eval.core.models import (
    DatasetSample,
    DifficultyLevel,
    EntityType,
    SensitiveSpan,
    SourceType,
    TextSpan,
)
from sensitive_eval.dataset.loaders import (
    load_jsonl,
    sample_from_dict,
    sample_to_dict,
    write_jsonl,
)


def test_sample_to_dict_serializes_enums_and_labels() -> None:
    label = SensitiveSpan(
        span=TextSpan(start=8, end=25),
        entity_type=EntityType.EMAIL,
        text="alice@example.com",
    )
    sample = DatasetSample(
        sample_id="sample-001",
        text="Contact alice@example.com for access.",
        source_type=SourceType.SUPPORT_TICKET,
        labels=(label,),
        difficulty=DifficultyLevel.EASY,
        metadata={"team": "support"},
    )

    row = sample_to_dict(sample)

    assert row["source_type"] == "support_ticket"
    assert row["difficulty"] == "easy"
    assert row["labels"][0]["entity_type"] == "email"
    assert row["labels"][0]["span"] == {"start": 8, "end": 25}


def test_sample_from_dict_validates_label_text_alignment() -> None:
    row = {
        "sample_id": "sample-001",
        "text": "Contact alice@example.com for access.",
        "source_type": "support_ticket",
        "difficulty": "easy",
        "metadata": {"team": "support"},
        "labels": [
            {
                "span": {"start": 8, "end": 25},
                "entity_type": "email",
                "text": "alice@example.com",
                "notes": None,
            }
        ],
    }

    sample = sample_from_dict(row)

    assert sample.sample_id == "sample-001"
    assert sample.source_type == SourceType.SUPPORT_TICKET
    assert sample.labels[0].text == "alice@example.com"


def test_sample_from_dict_rejects_misaligned_label_text() -> None:
    row = {
        "sample_id": "sample-001",
        "text": "Contact alice@example.com for access.",
        "source_type": "support_ticket",
        "labels": [
            {
                "span": {"start": 8, "end": 25},
                "entity_type": "email",
                "text": "wrong@example.com",
            }
        ],
    }

    with pytest.raises(ValueError, match="does not match sample text"):
        sample_from_dict(row)


def test_write_and_load_jsonl_round_trip(tmp_path) -> None:
    label = SensitiveSpan(
        span=TextSpan(start=8, end=25),
        entity_type=EntityType.EMAIL,
        text="alice@example.com",
    )
    sample = DatasetSample(
        sample_id="sample-001",
        text="Contact alice@example.com for access.",
        source_type=SourceType.SUPPORT_TICKET,
        labels=(label,),
    )
    path = tmp_path / "samples.jsonl"

    write_jsonl([sample], path)
    loaded_samples = load_jsonl(path)

    assert loaded_samples == [sample]


def test_load_jsonl_reports_line_number_for_invalid_rows(tmp_path) -> None:
    path = tmp_path / "samples.jsonl"
    path.write_text(
        json.dumps(
            {
                "sample_id": "sample-001",
                "text": "Contact alice@example.com for access.",
                "source_type": "support_ticket",
                "labels": [
                    {
                        "span": {"start": 8, "end": 500},
                        "entity_type": "email",
                        "text": "alice@example.com",
                    }
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    expected = re.escape(f"Invalid dataset row at {path}:1")
    with pytest.raises(ValueError, match=expected):
        load_jsonl(path)
