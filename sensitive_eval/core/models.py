"""Shared internal data models/enums for all pipelines."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional


# Enums for sensitive data finding type
class EntityType(str, Enum):
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    IP_ADDRESS = "ip_address"
    PERSON_NAME = "person_name"
    ACCOUNT_IDENTIFIER = "account_identifier"
    ACCESS_KEY = "access_key"
    TOKEN = "token"
    PASSWORD = "password"


# Enums for sensitive data source type
class SourceType(str, Enum):
    SUPPORT_TICKET = "support_ticket"
    INCIDENT_REPORT = "incident_report"
    CHANGE_REQUEST = "change_request"
    OPERATIONAL_NOTE = "operational_note"
    INTERNAL_COMMENT = "internal_comment"
    CONFIG_SNIPPET = "config_snippet"
    ATTACHMENT_TEXT = "attachment_text"


# Enums for difficulty level of finding sensitive data
class DifficultyLevel(str, Enum):
    HARD = "hard"
    MEDIUM = "medium"
    EASY = "easy"


@dataclass(frozen=True)
class TextSpan:
    start: int
    end: int

    # validation after __init__ runs
    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("Span end must be greater than span start")
        if self.start < 0:
            raise ValueError("Span start must be non-negative")

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass(frozen=True)
class SensitiveSpan:
    span: TextSpan
    entity_type: EntityType
    text: Optional[str] = None
    notes: Optional[str] = None


@dataclass(frozen=True)
class Finding:
    span: TextSpan
    entity_type: EntityType
    detector_name: str
    confidence_score: Optional[float] = None
    masked_value: Optional[str] = None
    rule_id: Optional[str] = None

    def __post_init__(self) -> None:
        if (
            self.confidence_score is not None
            and not 0.0 <= self.confidence_score <= 1.0
        ):
            raise ValueError("Finding confidence should be between 0 and 1")


@dataclass(frozen=True)
class DatasetSample:
    sample_id: str
    text: str
    source_type: SourceType
    labels: tuple[SensitiveSpan, ...] = field(default_factory=tuple)
    difficulty: Optional[DifficultyLevel] = None
    # A caller-provided dict can still be mutated outside this frozen dataclass.
    # Convert this later if stronger nested immutability becomes important.
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sample_id:
            raise ValueError("Dataset sample id must not be empty.")
        if not self.text:
            raise ValueError("Dataset text must not be empty.")

        text_length = len(self.text)
        for label in self.labels:
            if label.span.end > text_length:
                raise ValueError(
                    f"Label span {label.span} exceeds text span {text_length}"
                )


@dataclass(frozen=True)
class DetectorResult:
    sample_id: str
    detector_name: str
    latency_ms: Optional[float] = None
    findings: tuple[Finding, ...] = field(default_factory=tuple)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sample_id:
            raise ValueError("Detector result sample id must not be empty.")
        if not self.detector_name:
            raise ValueError("Detector name must not be empty")
        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("Detector latency must be non-negative")
