"""Test for regex detection"""

import pytest

from sensitive_eval.core.models import DatasetSample, EntityType, Finding, SourceType
from sensitive_eval.detectors.regex_detector import RegexDetector


class TestRegexFinding:
    def test_detect_email_finding(self):
        ticket1 = DatasetSample(
            sample_id="sample-001",
            text=(
                "Support ticket: Please contact Alice Morgan at "
                "alice.morgan@example.com for account ACC-10492."
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
                "Deploy note: billing-prod used account svc-billing and reached "
                "database host 172.16.4.22."
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
                "Internal comment: temporary password is Winter2026! for user "
                "jordan.lee."
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

    def test_detect_phone_number(self):
        ticket6 = DatasetSample(
            sample_id="sample-006",
            text=(
                "Alice's phone number is 0447576617230 if you would want to "
                "contact her."
            ),
            source_type=SourceType.INCIDENT_REPORT,
            difficulty=None,
        )
        results = RegexDetector().detect(ticket6)
        assert len(results.findings) == 1

        assert results.sample_id == "sample-006"
        assert results.detector_name == "regex"

        finding = results.findings[0]
        assert finding.masked_value == "0447******230"
        assert finding.detector_name == "regex"
        assert finding.confidence_score == 0.88
        assert finding.span.start == 24
        assert finding.span.end == 37
        assert finding.entity_type == EntityType.PHONE_NUMBER
        assert finding.rule_id == "phone_number"

    @pytest.mark.parametrize(
        "text",
        (
            "Build 123456 completed successfully.",
            "Reference abc1234567890 is not a phone number.",
            "Invalid contact 1234567890123456 is too long.",
        ),
    )
    def test_phone_number_rejects_invalid_candidates(self, text):
        sample = DatasetSample(
            sample_id="phone-negative",
            text=text,
            source_type=SourceType.INTERNAL_COMMENT,
        )

        results = RegexDetector().detect(sample)

        assert all(
            finding.entity_type != EntityType.PHONE_NUMBER
            for finding in results.findings
        )

    def test_detect_multiple_findings_in_one_result(self):
        ticket7 = DatasetSample(
            sample_id="sample-007",
            text=(
                "Incident note: service at 10.24.8.15 failed after token "
                "sk_live_51HxExampleToken was pasted into chat."
            ),
            source_type=SourceType.INCIDENT_REPORT,
            difficulty=None,
        )
        results = RegexDetector().detect(ticket7)
        assert len(results.findings) == 2

        entity_types = {finding.entity_type for finding in results.findings}
        assert entity_types == {EntityType.IP_ADDRESS, EntityType.TOKEN}


class TestRegexSupportedVariants:
    @pytest.mark.parametrize(
        "text, raw_value, entity_type, rule_id",
        (
            (
                "Contact (ops-team+alerts@example.co.uk).",
                "ops-team+alerts@example.co.uk",
                EntityType.EMAIL,
                "email",
            ),
            (
                "Host (255.255.255.255).",
                "255.255.255.255",
                EntityType.IP_ADDRESS,
                "ip_address",
            ),
            (
                'CLOUD_ACCESS_KEY="ASIA1234567890ABCDEF";',
                "ASIA1234567890ABCDEF",
                EntityType.ACCESS_KEY,
                "aws_access_key",
            ),
            (
                'DB_PASSWORD="Winter2026!".',
                "Winter2026!",
                EntityType.PASSWORD,
                "quoted_password",
            ),
            (
                "PORTAL_PASSWORD=SilverKey88!; rotate it.",
                "SilverKey88!",
                EntityType.PASSWORD,
                "unquoted_password",
            ),
            (
                "Rotate (ghp_abcdefgh12345678), then close the incident.",
                "ghp_abcdefgh12345678",
                EntityType.TOKEN,
                "token_like_secret",
            ),
            (
                "Call (+44 20 7946 0812).",
                "+44 20 7946 0812",
                EntityType.PHONE_NUMBER,
                "phone_number",
            ),
        ),
    )
    def test_detects_supported_variant_with_exact_boundaries(
        self,
        text,
        raw_value,
        entity_type,
        rule_id,
    ):
        sample = DatasetSample(
            sample_id="supported-variant",
            text=text,
            source_type=SourceType.INTERNAL_COMMENT,
        )

        result = RegexDetector().detect(sample)
        matching_findings = [
            finding for finding in result.findings if finding.entity_type == entity_type
        ]

        assert len(matching_findings) == 1

        finding = matching_findings[0]
        expected_start = text.index(raw_value)
        assert finding.span.start == expected_start
        assert finding.span.end == expected_start + len(raw_value)
        assert text[finding.span.start : finding.span.end] == raw_value
        assert finding.rule_id == rule_id


class TestRegexFalsePositiveGuards:
    @pytest.mark.parametrize(
        "entity_type, text",
        (
            (EntityType.EMAIL, "Contact alice@example for access."),
            (EntityType.EMAIL, "Contact alice@@example.com for access."),
            (EntityType.IP_ADDRESS, "Invalid host 256.1.1.1."),
            (EntityType.IP_ADDRESS, "Invalid host 10.20.30.40.50."),
            (EntityType.IP_ADDRESS, "Identifier host172.16.4.22 is not an IP."),
            (EntityType.ACCESS_KEY, "Key xAKIAIOSFODNN7EXAMPLE is embedded."),
            (EntityType.ACCESS_KEY, "Key AKIAIOSFODNN7EXAMPLEx is embedded."),
            (EntityType.ACCESS_KEY, "Key AKIA123 is too short."),
            (EntityType.PASSWORD, "A password is required for access."),
            (EntityType.PASSWORD, "The password is redacted in this ticket."),
            (EntityType.PASSWORD, "Please reset the password today."),
            (EntityType.TOKEN, "Value xsk_live_abcdefghij is embedded."),
            (EntityType.TOKEN, "Value sk_live_short is too short."),
            (EntityType.PHONE_NUMBER, "Deployment date: 2026-08-01."),
            (EntityType.PHONE_NUMBER, "Build 123456 completed successfully."),
            (
                EntityType.PHONE_NUMBER,
                "Invalid contact 1234567890123456 is too long.",
            ),
        ),
    )
    def test_rejects_invalid_or_embedded_candidate(self, entity_type, text):
        sample = DatasetSample(
            sample_id="guard-negative",
            text=text,
            source_type=SourceType.INTERNAL_COMMENT,
        )

        result = RegexDetector().detect(sample)

        assert all(finding.entity_type != entity_type for finding in result.findings)


class TestRegexDetectorContract:
    def test_empty_result_preserves_detector_identity(self):
        sample = DatasetSample(
            sample_id="no-findings",
            text="The deployment completed successfully.",
            source_type=SourceType.OPERATIONAL_NOTE,
        )

        result = RegexDetector().detect(sample)

        assert result.sample_id == sample.sample_id
        assert result.detector_name == "regex"
        assert result.findings == ()

    def test_findings_are_valid_masked_and_do_not_store_raw_values(self):
        sample = DatasetSample(
            sample_id="contract-sample",
            text=(
                "Contact alice@example.com from 10.20.30.40 or +44 20 7946 0812; "
                'CLOUD_ACCESS_KEY="AKIAIOSFODNN7EXAMPLE"; '
                'DB_PASSWORD="Winter2026!"; token sk_live_abcdefgh12345678.'
            ),
            source_type=SourceType.CONFIG_SNIPPET,
        )

        result = RegexDetector().detect(sample)

        assert len(result.findings) == 6
        assert "raw_value" not in Finding.__dataclass_fields__

        for finding in result.findings:
            raw_value = sample.text[finding.span.start : finding.span.end]

            assert 0 <= finding.span.start < finding.span.end <= len(sample.text)
            assert finding.detector_name == result.detector_name
            assert finding.rule_id is not None
            assert finding.confidence_score is not None
            assert finding.masked_value is not None
            assert finding.masked_value != raw_value
            assert raw_value not in repr(finding)

    def test_detection_is_deterministic(self):
        sample = DatasetSample(
            sample_id="deterministic-sample",
            text=(
                "Contact alice@example.com from 10.20.30.40 and rotate "
                "sk_live_abcdefgh12345678."
            ),
            source_type=SourceType.INCIDENT_REPORT,
        )
        detector = RegexDetector()

        first_result = detector.detect(sample)
        second_result = detector.detect(sample)

        assert first_result == second_result
