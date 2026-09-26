---
type: Security Policy
title: GDPR Compliance Requirements
description: Mandatory rules for handling EU customer data under GDPR regulations.
owner: legal-compliance@company.com
compliance: [GDPR]
effective_date: 2026-01-01
last_audit: 2026-07-20
related_security:
  - ../security/pii_handling.md
  - ../security/audit_requirements.md
related_tables:
  - ../tables/users.md
  - ../tables/user_events.md
---
# GDPR Compliance Requirements

## Scope
This policy applies to all data belonging to EU residents (identified by `users.country = 'EU'` or IP geolocation).

## Key Requirements

### 1. Right to Access (Article 15)
- Users can request a copy of all their personal data
- **Response Time**: 30 days maximum
- **Process**: Customer support creates a ticket → Data team runs export query → Encrypted delivery via secure portal
- **Query Template**: See `scripts/gdpr_data_export.sql` (requires security team approval)

### 2. Right to Erasure (Article 17 - "Right to be Forgotten")
- Users can request deletion of all personal data
- **Response Time**: 30 days maximum
- **Deletion Scope**:
  - `users.email`: Replace with `deleted_[user_id]@deleted.com`
  - `users.id`: Retain for audit trail (anonymized)
  - `user_events.user_id`: Replace with anonymized ID
  - `transactions.user_id`: Retain for financial compliance (anonymized)
- **Process**: Legal team approval required → Automated deletion script → Verification query

### 3. Data Minimization (Article 5)
- Only collect data that is strictly necessary for the stated purpose
- **Prohibited**: Collecting IP addresses for analytics (use anonymized session IDs instead)
- **Required**: Privacy policy must be presented at signup

### 4. Consent Management
- Explicit consent required for marketing emails
- Consent timestamp must be stored: `users.marketing_consent_at`
- Users can withdraw consent at any time via account settings

### 5. Data Breach Notification (Article 33)
- **Internal Notification**: Within 1 hour of detection
- **Regulatory Notification**: Within 72 hours to Data Protection Authority
- **User Notification**: Without undue delay if high risk to rights/freedoms
- **Process**: Follow [Incident Response Runbook](../runbooks/incident_response.md) with GDPR-specific checklist

## Enforcement
- Quarterly audits by external compliance firm
- Non-compliance penalties: Up to €20M or 4% of global annual revenue
- Internal violations: Immediate access revocation + HR review

## Related Policies
- [PII Handling Policy](../security/pii_handling.md)
- [Audit Requirements](../security/audit_requirements.md)