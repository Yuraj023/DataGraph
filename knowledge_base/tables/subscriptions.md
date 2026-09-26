---
type: BigQuery Table
title: Subscriptions
description: One row per customer subscription record.
resource: bigquery://project-analytics.prod.subscriptions
---
# Subscriptions Table

| Column | Type | Description |
|---|---|---|
| id | STRING | Primary Key |
| user_id | STRING | Foreign Key to users.id |
| amount | FLOAT | Monthly price in USD |
| status | STRING | 'active', 'canceled', 'past_due', 'trial' |
| created_at | TIMESTAMP | When the subscription started |