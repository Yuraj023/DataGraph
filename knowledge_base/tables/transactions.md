---
type: BigQuery Table
title: Transactions
description: Individual payment records.
---
# Transactions Table

| Column | Type | Description |
|---|---|---|
| id | STRING | Primary Key |
| user_id | STRING | Foreign Key to users.id |
| amount | FLOAT | Payment amount in USD |
| status | STRING | 'success', 'failed', 'refunded' |