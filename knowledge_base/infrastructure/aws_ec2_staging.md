---
type: Infrastructure Resource
title: Staging EC2 Instances
description: AWS EC2 instances for staging environment.
owner: devops-team@company.com
region: us-east-1
instance_type: t3.medium
count: 3
auto_scaling: true
related_runbooks:
  - ../runbooks/incident_response.md
related_security:
  - ../security/access_control.md
---
# Staging EC2 Instances

## Instance Details
- **Instance IDs**: i-0abc123def456, i-0def456ghi789, i-0ghi789jkl012
- **Private IPs**: 10.0.1.10, 10.0.1.11, 10.0.1.12
- **Security Group**: sg-staging-web (allows 443, 22 from VPN only)
- **Load Balancer**: alb-staging-123456

## Access Requirements
- SSH access requires VPN connection + MFA.
- See [Access Control Policy](../security/access_control.md) for approval process.

## Monitoring
- CloudWatch alarms configured for CPU > 80% for 5 minutes.
- Logs shipped to CloudWatch Logs Group: `/aws/ec2/staging`

## Incident Response
If staging is down, follow the [Incident Response Runbook](../runbooks/incident_response.md).