---
type: Infrastructure Resource
title: Production RDS Database
description: Primary PostgreSQL database for production workloads.
owner: database-team@company.com
engine: PostgreSQL 15.4
instance_class: db.r6g.2xlarge
storage: 500 GB (gp3)
multi_az: true
backup_retention: 30 days
related_runbooks:
  - ../runbooks/incident_response.md
  - ../runbooks/data_quality.md
related_security:
  - ../security/access_control.md
  - ../security/audit_requirements.md
---
# Production RDS Database

## Connection Details
- **Endpoint**: prod-db.cluster-abc123.us-east-1.rds.amazonaws.com
- **Port**: 5432
- **Database Name**: prod_analytics
- **Master Username**: admin (stored in AWS Secrets Manager)

## Performance Metrics
- **Max Connections**: 5000 (current avg: 1200)
- **Read Replicas**: 2 (us-east-1a, us-east-1b)
- **IOPS**: 3000 provisioned (gp3)
- **Memory**: 64 GB

## Backup & Recovery
- **Automated Backups**: Daily at 03:00 UTC
- **Retention Period**: 30 days
- **Point-in-Time Recovery**: Enabled (up to 5 minutes granularity)
- **Cross-Region Replication**: Disabled (cost optimization)

## Maintenance Windows
- **Preferred Window**: Sunday 04:00-05:00 UTC
- **Major Version Upgrades**: Require 2-week advance notice to application teams

## Monitoring & Alerts
- **CloudWatch Alarms**:
  - CPU > 80% for 5 minutes → SEV2
  - Free Storage < 50 GB → SEV1
  - Replica Lag > 100 MB → SEV2
- **Slow Query Log**: Enabled (threshold: 10 seconds)

## Access Control
- Direct SSH access: **DISABLED**
- Database access: Via IAM authentication only
- See [Access Control Policy](../security/access_control.md) for connection approval process

## Incident Response
For database outages or performance issues, follow the [Incident Response Runbook](../runbooks/incident_response.md).