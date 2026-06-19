"""Initial regex detection to find emails, IP addresses,
phone numbers, AWS access keys, passwords and tokens"""

import re
from dataclasses import dataclass
from typing import Optional, Pattern

from sensitive_eval.core.models import (
    DatasetSample,
    DetectorResult,
    EntityType,
    Finding,
    TextSpan,
)
from sensitive_eval.detectors.base import BaseDetector
from sensitive_eval.postprocessing.masking import mask_value


# dataclass for regex rule to prevent hardcoded loop per entity for regex detection
@dataclass(frozen=True)
class RegexRule:
    rule_id: str
    entity_type: EntityType
    pattern: Pattern[str]
    confidence_score: float
    group_name: Optional[str] = None


# default rules to specify specific entity rules
DEFAULT_RULES = (
    RegexRule(
        rule_id="email",
        entity_type=EntityType.EMAIL,
        pattern=re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}\b"),
        confidence_score=0.95,
    ),
    RegexRule(
        rule_id="ip_address",
        entity_type=EntityType.IP_ADDRESS,
        pattern=re.compile(
            r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\."
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        ),
        confidence_score=0.90,
    ),
    RegexRule(
        rule_id="aws_access_key",
        entity_type=EntityType.ACCESS_KEY,
        pattern=re.compile(r"\b(?:AKIA|ASIA|AIDA|AROA)[A-Z0-9]{16}\b"),
        confidence_score=0.98,
    ),
    RegexRule(
        rule_id="contextual_password",
        entity_type=EntityType.PASSWORD,
        pattern=re.compile(
            r"\b(?:password|passwd|pwd)\s*(?::|=|is)\s*(?P<secret>[^\s,;]+)",
            re.IGNORECASE,
        ),
        confidence_score=0.85,
        group_name="secret",  # This allows finding span to point only at the password
    ),
    RegexRule(
        rule_id="token_like_secret",
        entity_type=EntityType.TOKEN,
        pattern=re.compile(
            r"\b(?:"
            r"sk_(?:live|test)_[A-Za-z0-9_]{8,}|"
            r"ghp_[A-Za-z0-9_]{8,}|"
            r"(?:[A-Za-z]+_)*tok_[A-Za-z0-9_]{6,}|"
            r"sess_[A-Za-z0-9_]{8,}|"
            r"deploy_live_[A-Za-z0-9_]{8,}"
            r")\b"
        ),
        confidence_score=0.88,
    ),
)


class RegexDetector(BaseDetector):
    name = "regex"

    def detect(self, sample: DatasetSample) -> DetectorResult:
        self.rules = DEFAULT_RULES
        findings = []

        for rule in self.rules:
            for match in rule.pattern.finditer(sample.text):
                raw_value = (
                    match.group(rule.group_name) if rule.group_name else match.group(0)
                )

                if rule.group_name:
                    start = match.start(rule.group_name)
                    end = match.end(rule.group_name)
                else:
                    start = match.start()
                    end = match.end()

                findings.append(
                    Finding(
                        span=TextSpan(start=start, end=end),
                        entity_type=rule.entity_type,
                        detector_name=self.name,
                        confidence_score=rule.confidence_score,
                        masked_value=mask_value(rule.entity_type, raw_value),
                        rule_id=rule.rule_id,
                    )
                )
        return DetectorResult(
            sample_id=sample.sample_id,
            detector_name=self.name,
            findings=tuple(findings),
        )
