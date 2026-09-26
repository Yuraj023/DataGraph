---
type: Runbook
title: Incident Response Process
description: Step-by-step process for handling production and staging outages.
owner: devops-team@company.com
severity_levels: [SEV1, SEV2, SEV3]
escalation_contacts:
  SEV1: "#incidents-sev1"
  SEV2: "#incidents-sev2"
related_infrastructure:
  - ../infrastructure/aws_ec2_staging.md
  - ../infrastructure/aws_rds_prod.md
---
# Incident Response Process

## Severity Classification
- **SEV1**: Production down, data loss, security breach. Response time: 5 minutes.
- **SEV2**: Staging down, degraded performance. Response time: 15 minutes.
- **SEV3**: Non-critical service issue. Response time: 1 hour.

## Step-by-Step Process

### 1. Acknowledge (0-5 min)
- Post in the appropriate Slack channel (`#incidents-sev1` or `#incidents-sev2`).
- Assign an Incident Commander (IC).

### 2. Triage (5-15 min)
- Check CloudWatch dashboards for the affected service.
- For staging issues, check [Staging EC2 Instances](../infrastructure/aws_ec2_staging.md).
- For production database issues, check [Production RDS](../infrastructure/aws_rds_prod.md).

### 3. Mitigate (15-60 min)
- If EC2 issue: Check instance status, restart if necessary.
- If database issue: Check connections, slow queries, disk space.
- If deployment issue: Rollback using [Deployment Pipeline](../infrastructure/deployment_pipeline.md).

### 4. Resolve & Post-Mortem
- Confirm service is healthy.
- Write post-mortem within 24 hours.
- Update [Data Quality Runbook](../runbooks/data_quality.md) if data was affected.