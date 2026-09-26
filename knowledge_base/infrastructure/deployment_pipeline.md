---
type: Infrastructure Process
title: Deployment Pipeline
description: CI/CD pipeline for deploying application code to staging and production.
owner: devops-team@company.com
tools: [GitHub Actions, AWS CodeDeploy, Docker, Kubernetes]
environments: [dev, staging, production]
related_infrastructure:
  - ../infrastructure/aws_ec2_staging.md
  - ../infrastructure/aws_rds_prod.md
related_runbooks:
  - ../runbooks/incident_response.md
---
# Deployment Pipeline

## Pipeline Stages

### 1. Code Commit (GitHub)
- Developer pushes to feature branch
- Automated linting and unit tests run
- Code review required (minimum 2 approvals)

### 2. Build & Test (GitHub Actions)
- Docker image built and pushed to ECR
- Integration tests run against test database
- Security scan (Trivy) on container image
- **Gate**: All tests must pass before proceeding

### 3. Deploy to Staging (AWS CodeDeploy)
- Blue/Green deployment to [Staging EC2 Instances](../infrastructure/aws_ec2_staging.md)
- Automated smoke tests run
- QA team manual approval (if flagged)
- **Rollback**: Automatic if health checks fail within 5 minutes

### 4. Deploy to Production (AWS CodeDeploy)
- **Approval Required**: DevOps lead must manually approve
- Canary deployment (10% → 50% → 100% over 30 minutes)
- Real-time monitoring via CloudWatch dashboards
- **Automatic Rollback**: Triggered if error rate > 1% or latency > 500ms

## Environment Variables
- Managed via AWS Systems Manager Parameter Store
- Secrets stored in AWS Secrets Manager
- No environment variables in code or Docker images

## Rollback Procedures
1. **Staging**: Automatic rollback on failure. Manual rollback via GitHub Actions "Re-run" button.
2. **Production**: 
   - Quick rollback: `aws deploy stop-deployment --deployment-id <id>`
   - Full rollback: Redeploy previous Git tag via GitHub Actions

## Deployment Schedule
- **Staging**: Continuous (on merge to `main`)
- **Production**: 
  - Regular deployments: Tuesday & Thursday 14:00-16:00 UTC
  - Emergency deployments: Anytime with DevOps lead approval

## Incident Response
If a deployment causes an outage:
1. Immediately trigger rollback
2. Follow [Incident Response Runbook](../runbooks/incident_response.md)
3. Post-mortem required within 24 hours