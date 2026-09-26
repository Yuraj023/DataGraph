---
type: Security Policy
title: Access Control Policy
description: Rules for granting and managing access to systems, databases, and sensitive data.
owner: security-team@company.com
framework: [Zero Trust, Least Privilege]
last_review: 2026-09-01
related_security:
  - ../security/audit_requirements.md
  - ../security/pii_handling.md
related_infrastructure:
  - ../infrastructure/aws_ec2_staging.md
  - ../infrastructure/aws_rds_prod.md
---
# Access Control Policy

## Core Principles

### 1. Least Privilege
- Users are granted the **minimum access necessary** to perform their job function
- Access is time-bound and must be renewed every 90 days
- No shared accounts or generic credentials

### 2. Separation of Duties
- Developers cannot have production database write access
- Security team cannot approve their own access requests
- All privileged actions require dual approval

### 3. Zero Trust Architecture
- No implicit trust based on network location
- All access requires authentication + authorization
- Continuous verification via session tokens (max 12 hours)

## Access Tiers

### Tier 1: Public (No Authentication Required)
- Public website
- Public API endpoints (read-only)
- Marketing materials

### Tier 2: Internal (Authentication Required)
- Internal dashboards
- Staging environments
- Non-sensitive analytics data
- **Requirements**: Company SSO + MFA

### Tier 3: Confidential (Authentication + Authorization Required)
- Production databases (read-only)
- Customer PII (masked)
- Financial reports
- **Requirements**: Manager approval + security training completion

### Tier 4: Restricted (Authentication + Authorization + Justification Required)
- Production database write access
- Raw customer PII
- Security logs
- **Requirements**: Director approval + business justification + 24-hour access window

## Access Request Process

### Standard Access (Tier 2-3)
1. Submit request via Okta Workflows
2. Manager approval (automatic if manager is in approval chain)
3. Security team review (within 24 hours)
4. Access granted via IAM role assignment
5. Access expires after 90 days (automatic revocation)

### Emergency Access (Tier 4)
1. Submit emergency request via PagerDuty
2. On-call security engineer approval
3. Access granted for 4 hours maximum
4. Automatic post-access review required
5. Audit log sent to security team

## Prohibited Practices
-  Sharing credentials via email, Slack, or password managers
-  Using personal accounts for company systems
-  Disabling MFA for any account
-  Hardcoding credentials in source code
-  Accessing production data from personal devices

## Enforcement
- Quarterly access reviews (automatic revocation of unused accounts)
- Violations: Immediate access revocation + HR disciplinary action
- Repeated violations: Termination + legal action

## Related Systems
- [Production RDS Access](../infrastructure/aws_rds_prod.md)
- [Staging EC2 Access](../infrastructure/aws_ec2_staging.md)
- [Audit Logging](../security/audit_requirements.md)