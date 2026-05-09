"""JSONL dataset loading and writing utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from sensitive_eval.core.models import (
    DatasetSample,
    DifficultyLevel,
    EntityType,
    SensitiveSpan,
    SourceType,
    TextSpan,
)


JsonDict = Dict[str, Any]


def sample_to_dict(sample: DatasetSample) -> JsonDict:
    """Convert a dataset sample into a JSON-serializable dictionary."""
    return {
        "sample_id": sample.sample_id,
        "text": sample.text,
        "source_type": sample.source_type.value,
        "difficulty": sample.difficulty.value if sample.difficulty else None,
        "metadata": dict(sample.metadata),
        "labels": [
            {
                "span": {
                    "start": label.span.start,
                    "end": label.span.end,
                },
                "entity_type": label.entity_type.value,
                "text": label.text,
                "notes": label.notes,
            }
            for label in sample.labels
        ],
    }


def sample_from_dict(row: JsonDict) -> DatasetSample:
    """Convert one parsed JSON object into a validated dataset sample."""
    text = _require_str(row, "text")
    labels = tuple(_label_from_dict(label, text) for label in row.get("labels", []))
    difficulty = _optional_difficulty(row.get("difficulty"))

    return DatasetSample(
        sample_id=_require_str(row, "sample_id"),
        text=text,
        source_type=SourceType(_require_str(row, "source_type")),
        labels=labels,
        difficulty=difficulty,
        metadata=dict(row.get("metadata", {})),
    )


def load_jsonl(path: Path) -> List[DatasetSample]:
    """Load dataset samples from a JSONL file."""
    samples: List[DatasetSample] = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            try:
                row = json.loads(stripped)
                if not isinstance(row, dict):
                    raise ValueError("JSONL row must be an object")
                samples.append(sample_from_dict(row))
            except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
                raise ValueError(
                    f"Invalid dataset row at {path}:{line_number}: {exc}"
                ) from exc

    return samples


def write_jsonl(samples: Iterable[DatasetSample], path: Path) -> None:
    """Write dataset samples to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        for sample in samples:
            file.write(json.dumps(sample_to_dict(sample), sort_keys=True))
            file.write("\n")


def _label_from_dict(row: JsonDict, sample_text: str) -> SensitiveSpan:
    span_row = row.get("span")
    if not isinstance(span_row, dict):
        raise ValueError("Label span must be an object")

    span = TextSpan(
        start=_require_int(span_row, "start"),
        end=_require_int(span_row, "end"),
    )
    label_text = _optional_str(row.get("text"))

    if label_text is not None and sample_text[span.start : span.end] != label_text:
        raise ValueError(
            f"Label text {label_text!r} does not match sample text at {span}"
        )

    return SensitiveSpan(
        span=span,
        entity_type=EntityType(_require_str(row, "entity_type")),
        text=label_text,
        notes=_optional_str(row.get("notes")),
    )


def _optional_difficulty(value: Any) -> Optional[DifficultyLevel]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Difficulty must be a string or null")
    return DifficultyLevel(value)


def _optional_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Expected optional string field to be a string or null")
    return value


def _require_str(row: JsonDict, key: str) -> str:
    value = row[key]
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _require_int(row: JsonDict, key: str) -> int:
    value = row[key]
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value
