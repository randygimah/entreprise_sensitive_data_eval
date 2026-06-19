"""Test for regex detection"""

from sensitive_eval.detectors.regex_detector import RegexDetector
from sensitive_eval.core.models import DatasetSample, SourceType, EntityType


class TestRegexFinding:
    def test_detect_email_finding(self):
        ticket1 = DatasetSample(
            sample_id="sample-001",
            text=(
                "Support ticket: Please contact Alice Morgan at alice.morgan@example.com for account ACC-10492."
            ),
            source_type=SourceType.SUPPORT_TICKET,
            difficulty=None,
        )
        results = RegexDetector().detect(ticket1)
        assert len(results.findings) == 1

        assert results.sample_id == "sample-001"
        assert results.detector_name == "regex"

        finding = results.findings[0]
        assert finding.masked_value == "al***@example.com"
        assert finding.detector_name == "regex"
        assert finding.confidence_score == 0.95
        assert finding.span.start == 47
        assert finding.span.end == 71
        assert finding.entity_type == EntityType.EMAIL

    def test_detect_ip_address_finding(self):
        ticket2 = DatasetSample(
            sample_id="sample-002",
            text=(
                "Deploy note: billing-prod used account svc-billing and reached database host 172.16.4.22."
            ),
            source_type=SourceType.OPERATIONAL_NOTE,
            difficulty=None,
        )
        results = RegexDetector().detect(ticket2)
        assert len(results.findings) == 1

        assert results.sample_id == "sample-002"
        assert results.detector_name == "regex"

        finding = results.findings[0]
        assert finding.masked_value == "172.16.xxx.xxx"
        assert finding.detector_name == "regex"
        assert finding.confidence_score == 0.90
        assert finding.span.start == 77
        assert finding.span.end == 88
        assert finding.entity_type == EntityType.IP_ADDRESS

    def test_detect_access_key_finding(self):
        ticket3 = DatasetSample(
            sample_id="sample-003",
            text=("CLOUD_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE"),
            source_type=SourceType.CONFIG_SNIPPET,
            difficulty=None,
        )
        results = RegexDetector().detect(ticket3)
        assert len(results.findings) == 1

        assert results.sample_id == "sample-003"
        assert results.detector_name == "regex"

        finding = results.findings[0]
        assert finding.masked_value == "AKIA************MPLE"
        assert finding.detector_name == "regex"
        assert finding.confidence_score == 0.98
        assert finding.span.start == 17
        assert finding.span.end == 37
        assert finding.entity_type == EntityType.ACCESS_KEY

    def test_detect_password_finding(self):
        ticket4 = DatasetSample(
            sample_id="sample-004",
            text=(
                "Internal comment: temporary password is Winter2026! for user jordan.lee."
            ),
            source_type=SourceType.INTERNAL_COMMENT,
            difficulty=None,
        )
        results = RegexDetector().detect(ticket4)
        assert len(results.findings) == 1

        assert results.sample_id == "sample-004"
        assert results.detector_name == "regex"

        finding = results.findings[0]
        assert finding.masked_value == "Wi*********"
        assert finding.detector_name == "regex"
        assert finding.confidence_score == 0.85
        assert finding.span.start == 40
        assert finding.span.end == 51
        assert finding.entity_type == EntityType.PASSWORD

    def test_detect_token_finding(self):
        ticket5 = DatasetSample(
            sample_id="sample-005",
            text=(
                "Incident note: service failed after token "
                "sk_live_51HxExampleToken was pasted into chat."
            ),
            source_type=SourceType.INCIDENT_REPORT,
            difficulty=None,
        )
        results = RegexDetector().detect(ticket5)
        assert len(results.findings) == 1

        assert results.sample_id == "sample-005"
        assert results.detector_name == "regex"

        finding = results.findings[0]
        assert finding.masked_value == "sk**********************"
        assert finding.detector_name == "regex"
        assert finding.confidence_score == 0.88
        assert finding.span.start == 42
        assert finding.span.end == 66
        assert finding.entity_type == EntityType.TOKEN
        assert finding.rule_id == "token_like_secret"

    def test_detect_multiple_findings_in_one_result(self):
        ticket6 = DatasetSample(
            sample_id="sample-006",
            text=(
                "Incident note: service at 10.24.8.15 failed after token "
                "sk_live_51HxExampleToken was pasted into chat."
            ),
            source_type=SourceType.INCIDENT_REPORT,
            difficulty=None,
        )
        results = RegexDetector().detect(ticket6)
        assert len(results.findings) == 2

        entity_types = {finding.entity_type for finding in results.findings}
        assert entity_types == {EntityType.IP_ADDRESS, EntityType.TOKEN}
