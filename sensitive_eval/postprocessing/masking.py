"""Privacy-safe masking helpers for reporting detector findings."""

from sensitive_eval.core.models import EntityType


def mask_value(entity_type: EntityType, raw_value: str) -> str:
    """Return a display-safe version of a raw sensitive value."""

    if entity_type == EntityType.EMAIL:
        return mask_email(raw_value)

    if entity_type == EntityType.IP_ADDRESS:
        return mask_ip_address(raw_value)

    if entity_type == EntityType.PERSON_NAME:
        return mask_person_name(raw_value)

    if entity_type == EntityType.ACCESS_KEY:
        return mask_keep_edges(raw_value, prefix_chars=4, suffix_chars=4)

    if entity_type == EntityType.PHONE_NUMBER:
        return mask_keep_edges(raw_value, prefix_chars=4, suffix_chars=3)

    if entity_type == EntityType.PASSWORD:
        return mask_keep_prefix(raw_value, visible_chars=2)

    if entity_type == EntityType.TOKEN:
        return mask_keep_prefix(raw_value, visible_chars=2)

    if entity_type == EntityType.ACCOUNT_IDENTIFIER:
        return mask_keep_prefix(raw_value, visible_chars=2)


def mask_email(raw_value: str) -> str:
    local_part, _, domain = raw_value.partition("@")
    if not domain:
        return mask_keep_prefix(raw_value)

    visible = local_part[:2]
    return f"{visible}***@{domain}"


def mask_ip_address(raw_value: str) -> str:
    parts = raw_value.split(".")
    if len(parts) != 4:
        return mask_keep_prefix(raw_value)

    return f"{parts[0]}.{parts[1]}.xxx.xxx"


def mask_keep_prefix(raw_value: str, visible_chars: int = 2) -> str:
    if len(raw_value) <= visible_chars:
        return "*" * len(raw_value)
    return raw_value[:visible_chars] + "*" * (len(raw_value) - visible_chars)


def mask_keep_edges(
    raw_value: str, prefix_chars: int = 2, suffix_chars: int = 2
) -> str:
    visible_chars = prefix_chars + suffix_chars

    if len(raw_value) <= visible_chars:
        return "*" * len(raw_value)

    middle_length = len(raw_value) - visible_chars
    return raw_value[:prefix_chars] + "*" * middle_length + raw_value[-suffix_chars:]


def mask_person_name(raw_value: str) -> str:
    masked_parts = []
    for part in raw_value.split():
        if len(part) <= 2:
            masked_parts.append("*" * len(part))
            continue

        visible_chars = part[:2]
        masked_chars = "*" * (len(part) - 2)
        masked_parts.append(visible_chars + masked_chars)

    return " ".join(masked_parts)
