"""Tests for privacy-safe postprocessing helpers."""

from sensitive_eval.core.models import EntityType
from sensitive_eval.postprocessing.hashing import hash_value
from sensitive_eval.postprocessing.masking import (
    mask_email,
    mask_ip_address,
    mask_keep_edges,
    mask_keep_prefix,
    mask_person_name,
    mask_value,
)


def test_mask_value_dispatches_by_entity_type() -> None:
    assert mask_value(EntityType.EMAIL, "alice@example.com") == "al***@example.com"
    assert mask_value(EntityType.IP_ADDRESS, "192.168.10.45") == "192.168.xxx.xxx"
    assert mask_value(EntityType.PASSWORD, "Secret123!") == "Se********"
    assert mask_value(EntityType.TOKEN, "tok_abcdef") == "to********"
    assert mask_value(EntityType.ACCOUNT_IDENTIFIER, "ACC-10492") == "AC*******"


def test_mask_email_handles_malformed_email_like_value() -> None:
    assert mask_email("not-an-email") == "no**********"


def test_mask_ip_address_handles_non_ipv4_value() -> None:
    assert mask_ip_address("localhost") == "lo*******"


def test_mask_keep_prefix_masks_short_values() -> None:
    assert mask_keep_prefix("ab") == "**"
    assert mask_keep_prefix("abc") == "ab*"


def test_mask_keep_edges_masks_middle() -> None:
    assert mask_keep_edges("AKIAIOSFODNN7EXAMPLE", 4, 4) == "AKIA************MPLE"
    assert mask_keep_edges("short", 3, 3) == "*****"


def test_mask_person_name_masks_each_name_part() -> None:
    assert mask_person_name("Alice Morgan") == "Al*** Mo****"


def test_hash_value_is_deterministic_sha256() -> None:
    first_hash = hash_value("Secret123!")
    second_hash = hash_value("Secret123!")

    assert first_hash == second_hash
    assert len(first_hash) == 64
