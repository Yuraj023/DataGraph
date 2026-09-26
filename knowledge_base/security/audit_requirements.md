---
type: Security Policy
title: Audit Logging Requirements
description: Mandatory logging requirements for compliance, security monitoring, and incident response.
owner: security-team@company.com
compliance: [SOC2, GDPR, HIPAA]
retention: 7 years
related_security:
  - ../security/access_control.md
  - ../security/pii_handling.md
related_tables:
  - ../tables/users.md
  - ../tables/user_events.md
---
# Audit Logging Requirements

## Scope
All systems handling sensitive data (PII, financial, health) must implement comprehensive audit logging.

## Required Log Events

### 1. Authentication Events
- **Successful Login**: user_id, timestamp, IP address, device fingerprint, MFA status
- **Failed Login**: username (or email), timestamp, IP address, failure reason
- **Password Reset**: user_id, timestamp, IP address, reset method (email/SMS)
- **Session Expiration**: user_id, timestamp, session_duration

### 2. Authorization Events
- **Access Granted**: user_id, resource_accessed, permission_level, approver_id, timestamp
- **Access Denied**: user_id, resource_requested, reason, timestamp
- **Privilege Escalation**: user_id, old_role, new_role, approver_id, timestamp

### 3. Data Access Events
- **PII Query**: user_id, query_hash, tables_accessed, row_count, timestamp
- **Data Export**: user_id, export_format, record_count, destination, timestamp
- **Data Deletion**: user_id, records_deleted, deletion_reason, timestamp

### 4. System Events
- **Configuration Changes**: admin_id, change_type, before_value, after_value, timestamp
- **Deployment Events**: deployer_id, environment, version, deployment_id, timestamp
- **Security Alerts**: alert_type, severity, affected_system, timestamp

## Log Storage Requirements

### Retention Policy
- **Hot Storage** (searchable): 90 days
- **Warm Storage** (queryable within 24 hours): 2 years
- **Cold Storage** (archive, retrieval within 48 hours): 7 years

### Storage Locations
- **Application Logs**: CloudWatch Logs → S3 (encrypted at rest)
- **Database Audit Logs**: RDS Audit Logs → S3 (encrypted at rest)
- **Access Logs**: CloudTrail → S3 (encrypted at rest, versioning enabled)

### Encryption
- **In Transit**: TLS 1.3 required
- **At Rest**: AES-256 encryption (AWS KMS managed keys)
- **Key Rotation**: Automatic annual rotation

## Log Integrity
- **Immutability**: Logs cannot be modified or deleted (S3 Object Lock enabled)
- **Tamper Detection**: SHA-256 checksums for each log file
- **Chain of Custody**: Metadata includes log_shipper_id, ingestion_timestamp

## Monitoring & Alerting
- **Real-Time Alerts**:
  - Failed login attempts > 5 in 10 minutes → Security team notified
  - PII query by unauthorized user → Immediate access revocation
  - Log ingestion failure → DevOps team notified
- **Daily Reports**:
  - Top 10 users by data access volume
  - Unusual access patterns (geographic anomalies, time anomalies)
  - Expired access attempts

## Compliance Mapping
- **SOC2**: CC6.1 (Logical Access), CC7.2 (System Monitoring)
- **GDPR**: Article 30 (Records of Processing Activities)
- **HIPAA**: §164.312(b) (Audit Controls)

## Enforcement
- Systems without proper audit logging: Blocked from production deployment
- Log tampering: Immediate termination + legal action
- Quarterly audit by external firm

## Related Policies
- [Access Control Policy](../security/access_control.md)
- [PII Handling Policy](../security/pii_handling.md)