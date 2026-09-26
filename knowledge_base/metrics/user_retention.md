---
type: Metric
title: User Retention Rate
description: Percentage of users who return to the platform within 30 days of signup.
owner: product-analytics@company.com
tags: [product, engagement, growth]
contains_pii: true
related_tables: 
  - ../tables/users.md
  - ../tables/user_events.md
related_security:
  - ../security/pii_handling.md
---
# User Retention Rate

## Definition
Retention is calculated as: (Users with at least 1 event in days 1-30) / (Total new users in cohort) * 100

## Critical Security Requirement
Because this metric requires joining user behavioral data with PII (email, user_id), you **MUST** follow the PII handling rules in [PII Handling Policy](../security/pii_handling.md).

## Calculation Logic