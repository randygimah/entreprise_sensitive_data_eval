# Dataset Plan

This plan is the blueprint for the first 40 synthetic dataset samples. It is
designed to keep the dataset balanced across source types, entity types, and
difficulty levels before the final JSONL rows are written.

The plan is not the dataset itself. It describes what each sample should test,
so the final `data/synthetic_samples.jsonl` file can be built intentionally.

## Plan Table

| sample_id | source_type | difficulty | target entities | scenario | purpose |
| --- | --- | --- | --- | --- | --- |
| sample-001 | support_ticket | easy | person_name, email, account_identifier | Support ticket asks an agent to contact a named employee about a customer account. | Tests straightforward contact and account information. |
| sample-002 | incident_report | medium | ip_address, token | Incident note includes an internal service IP and a token pasted into chat. | Tests structured infrastructure data plus token-like secret detection. |
| sample-003 | internal_comment | medium | password, account_identifier | Internal comment discloses a temporary password for a username-style account. | Tests contextual password disclosure. |
| sample-004 | support_ticket | easy | email, phone_number | Customer asks support to call a contact and includes email follow-up details. | Tests common customer contact information. |
| sample-005 | support_ticket | hard | person_name, account_identifier, password | Ticket describes a password reset where the password is embedded in prose. | Tests contextual sensitivity beyond obvious key-value formats. |
| sample-006 | operational_note | medium | ip_address, account_identifier | Operations note mentions a host IP and service account involved in a deployment. | Tests operational text with infrastructure and account references. |
| sample-007 | config_snippet | easy | ip_address, access_key | Configuration snippet contains a host value and access-key-like credential. | Tests regex-friendly structured configuration data. |
| sample-008 | internal_comment | hard | token, password | Developer comment mentions a copied bearer token and a temporary password. | Tests multiple high-risk disclosures in informal text. |
| sample-009 | change_request | medium | person_name, email, account_identifier | Change request names an approver, their email, and the target account. | Tests governance-style text with several entity types. |
| sample-010 | internal_comment | easy | person_name, email | Internal comment routes a task to a named colleague with an email address. | Tests simple name and email detection. |
| sample-011 | attachment_text | medium | phone_number, account_identifier | OCR-like attachment text includes a phone number and account reference. | Tests noisy extracted text with business identifiers. |
| sample-012 | support_ticket | medium | phone_number, password | Ticket includes a callback number and a phrase like "the temp pass is ...". | Tests mixed contact info and contextual password disclosure. |
| sample-013 | incident_report | hard | access_key, token, ip_address | Incident report describes leaked credentials and affected service IP. | Tests dense incident text with multiple secret-like values. |
| sample-014 | operational_note | easy | ip_address | Operations note records a single server IP during routine maintenance. | Tests a simple deterministic IP baseline case. |
| sample-015 | config_snippet | medium | token, account_identifier | Config snippet includes an API token and service account name. | Tests structured token and account fields. |
| sample-016 | attachment_text | hard | person_name, email, password | Extracted attachment text contains a named owner, email, and password-like phrase. | Tests OCR-style text with contextual and contact entities. |
| sample-017 | config_snippet | hard | access_key, password | Config block includes access-key-like value and password field. | Tests structured secrets likely handled well by rules. |
| sample-018 | incident_report | medium | person_name, ip_address, token | Incident report assigns a named responder to rotate a token for a host. | Tests incident workflow context and secret-like value. |
| sample-019 | support_ticket | medium | account_identifier, token | Support ticket includes a customer account and copied session token. | Tests token leakage in a customer-support style message. |
| sample-020 | internal_comment | medium | account_identifier, phone_number | Internal comment mentions a user account and direct contact number. | Tests account and phone extraction from casual text. |
| sample-021 | change_request | easy | person_name, account_identifier | Change request names requester and affected account ID. | Tests basic change-management metadata. |
| sample-022 | operational_note | hard | password, token | Operational note includes a temporary password and a deployment token. | Tests multiple contextual sensitive values in runbook-like prose. |
| sample-023 | config_snippet | easy | email, ip_address | Config snippet includes admin email and bind IP. | Tests structured fields that are not always secrets. |
| sample-024 | attachment_text | medium | account_identifier, access_key | Attachment-derived text includes an account ID and access-key-like string. | Tests extracted text where formatting may be irregular. |
| sample-025 | incident_report | easy | ip_address, email | Incident report includes impacted IP and escalation email. | Tests common incident-report observables. |
| sample-026 | support_ticket | hard | person_name, phone_number, password | Customer writes a natural-language note containing callback details and a password. | Tests realistic support-ticket oversharing. |
| sample-027 | internal_comment | hard | access_key, account_identifier | Internal comment asks someone to rotate an access key tied to a service account. | Tests informal secret handling and account references. |
| sample-028 | change_request | medium | email, token | Change request includes reviewer email and pasted deployment token. | Tests governance text with accidental secret inclusion. |
| sample-029 | operational_note | medium | person_name, ip_address, account_identifier | Operations note names an on-call engineer, host IP, and service account. | Tests mixed operational entities. |
| sample-030 | config_snippet | medium | phone_number, password | Config-like support block contains support phone and password variable. | Tests structured value detection with mixed sensitivity. |
| sample-031 | attachment_text | easy | email, phone_number | OCR-like contact page includes email and phone number. | Tests attachment-derived contact details. |
| sample-032 | support_ticket | medium | person_name, email, token | Support ticket references an engineer and includes a copied auth token. | Tests contextual token leakage in support workflow. |
| sample-033 | incident_report | hard | password, account_identifier, ip_address | Incident report says a service password was shared for a host and account. | Tests contextual secret disclosure during incident response. |
| sample-034 | change_request | hard | access_key, person_name | Change request asks a named owner to approve rotating an access key. | Tests key-like secret in approval workflow. |
| sample-035 | operational_note | easy | account_identifier, ip_address | Routine operations note maps an account to a host IP. | Tests simple account and infrastructure pair. |
| sample-036 | config_snippet | hard | token, access_key, ip_address | Dense config block includes callback IP, token, and access-key-like value. | Tests multi-secret structured text. |
| sample-037 | internal_comment | medium | email, password | Internal comment asks someone to email a user about a temporary password. | Tests contact plus password context. |
| sample-038 | attachment_text | hard | person_name, account_identifier, token | Extracted attachment text has a named owner, account, and token-like value. | Tests noisy multi-entity attachment text. |
| sample-039 | change_request | easy | email, phone_number | Change request includes reviewer contact email and phone number. | Tests simple contact info in approval text. |
| sample-040 | operational_note | hard | token, password, access_key | Runbook note contains several credential-like values needing rotation. | Tests high-density sensitive content and future deduplication behavior. |

## Coverage Notes

- Each core entity type appears multiple times.
- Each source type appears at least five times.
- Difficulty is intentionally mixed so detectors are tested on obvious structured
  values and harder contextual disclosures.
- Several samples contain multiple entity types to support later failure-mode
  analysis.
