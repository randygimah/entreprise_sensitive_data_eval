"""Tests for shared internal data models"""

import re
from dataclasses import FrozenInstanceError

import pytest

from sensitive_eval.core.models import (
    DatasetSample,
    DetectorResult,
    EntityType,
    Finding,
    SensitiveSpan,
    SourceType,
    TextSpan,
)


class TestTextSpan:
    def test_text_spans(self):

        # test valid spans
        result = TextSpan(
            start=2,
            end=10,
        )
        assert result.start == 2
        assert result.end == 10
        assert result.length == 8

        # test frozen behaviour
        with pytest.raises(FrozenInstanceError):
            result.end = 20

    def test_invalid_fields(self):
        # test invalid spans
        with pytest.raises(
            ValueError, match="Span end must be greater than span start"
        ):
            TextSpan(start=10, end=2)

        # test negative spans
        with pytest.raises(ValueError, match="Span start must be non-negative"):
            TextSpan(start=-1, end=2)


class TestFindingResult:
    def test_confidence_validation(self):

        # test valid confidence score
        result = Finding(
            span=TextSpan(start=0, end=5),
            entity_type=EntityType.EMAIL,
            detector_name="regex",
            confidence_score=0.9,
        )

        assert result.confidence_score == 0.9

        # test invalid confidence score
        with pytest.raises(
            ValueError, match="Finding confidence should be between 0 and 1"
        ):
            Finding(
                span=TextSpan(start=0, end=5),
                entity_type=EntityType.EMAIL,
                detector_name="regex",
                confidence_score=1.2,
            )

    def test_none_confidence_boundary(self):
        # test valid confidence score
        result = Finding(
            span=TextSpan(start=0, end=5),
            entity_type=EntityType.EMAIL,
            detector_name="regex",
            confidence_score=None,
        )

        assert result.confidence_score is None


class TestDetectorResult:
    def test_detector_result(self):

        # test valid latency, sample_id and detector name
        result = DetectorResult(
            sample_id="001",
            detector_name="regex",
            latency_ms=20,
        )

        assert result.sample_id == "001"
        assert result.latency_ms == 20
        assert result.detector_name == "regex"

    def test_invalid_fields(self):
        with pytest.raises(
            ValueError, match="Detector result sample id must not be empty."
        ):
            DetectorResult(
                sample_id="",
                detector_name="regex",
                latency_ms=20,
            )

        # test invalid latency
        with pytest.raises(ValueError, match="Detector latency must be non-negative"):
            DetectorResult(
                sample_id="001",
                detector_name="regex",
                latency_ms=-20,
            )

        # test invalid detector name
        with pytest.raises(ValueError, match="Detector name must not be empty"):
            DetectorResult(
                sample_id="001",
                detector_name="",
                latency_ms=20,
            )

    def test_detector_result_accepts_tuple(self):
        finding = Finding(
            span=TextSpan(start=8, end=25),
            entity_type=EntityType.EMAIL,
            detector_name="regex",
            confidence_score=1.0,
            masked_value="a***@example.com",
            rule_id="email_regex",
        )

        result = DetectorResult(
            sample_id="001", detector_name="regex", latency_ms=20, findings=(finding,)
        )

        assert result.findings == (finding,)
        assert result.findings[0].rule_id == "email_regex"


class TestDatasetSample:
    def test_dataset_sample_accepts_tuple_of_labels(self):
        text = "Contact alice@example.com for access."

        label = SensitiveSpan(
            span=TextSpan(start=8, end=25),
            entity_type=EntityType.EMAIL,
            text="alice@example.com",
        )

        sample = DatasetSample(
            sample_id="001",
            text=text,
            source_type=SourceType.SUPPORT_TICKET,
            labels=(label,),
        )

        assert sample.labels == (label,)
        assert sample.labels[0].entity_type == EntityType.EMAIL

    def test_inavlid_results(self):
        text = "Contact alice@example.com for access."
        text_length = len(text)

        label = SensitiveSpan(
            span=TextSpan(start=8, end=500),
            entity_type=EntityType.EMAIL,
            text="alice@example.com",
        )

        expected_message = f"Label span {label.span} exceeds text span {text_length}"

        with pytest.raises(ValueError, match=re.escape(expected_message)):
            DatasetSample(
                sample_id="001",
                text=text,
                source_type=SourceType.SUPPORT_TICKET,
                labels=(label,),
            )

        with pytest.raises(ValueError, match="Dataset sample id must not be empty."):
            DatasetSample(
                sample_id="",
                text=text,
                source_type=SourceType.SUPPORT_TICKET,
                labels=(label,),
            )

        with pytest.raises(ValueError, match="Dataset text must not be empty."):
            DatasetSample(
                sample_id="001",
                text="",
                source_type=SourceType.SUPPORT_TICKET,
                labels=(label,),
            )
