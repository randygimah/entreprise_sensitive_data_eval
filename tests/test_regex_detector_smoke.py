"""Dataset-wide smoke tests for the deterministic regex baseline."""

from pathlib import Path

from sensitive_eval.core.models import EntityType
from sensitive_eval.dataset.loaders import load_jsonl
from sensitive_eval.detectors.regex_detector import RegexDetector

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_DATASET_PATH = PROJECT_ROOT / "data" / "synthetic_samples.jsonl"


def test_regex_detector_smoke_over_development_dataset() -> None:
    """Every development sample satisfies the detector output contract."""
    samples = load_jsonl(DEVELOPMENT_DATASET_PATH)
    detector = RegexDetector()

    first_results = tuple(detector.detect(sample) for sample in samples)
    second_results = tuple(detector.detect(sample) for sample in samples)

    assert len(first_results) == len(samples)
    assert first_results == second_results

    for sample, result in zip(samples, first_results):
        assert result.sample_id == sample.sample_id
        assert result.detector_name == detector.name
        assert isinstance(result.findings, tuple)

        for finding in result.findings:
            assert 0 <= finding.span.start < finding.span.end <= len(sample.text)
            assert isinstance(finding.entity_type, EntityType)
            assert finding.detector_name == detector.name
            assert finding.rule_id is not None
            assert finding.confidence_score is not None
            assert finding.masked_value is not None

            raw_value = sample.text[finding.span.start : finding.span.end]
            assert finding.masked_value != raw_value
            assert raw_value not in repr(result)
