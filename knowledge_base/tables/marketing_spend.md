---
type: BigQuery Table
title: Marketing Spend
description: Daily aggregated spend data from Google Ads, Meta, and LinkedIn.
owner: marketing-ops@company.com
resource: bigquery://project-analytics.prod.marketing_spend
---
# Marketing Spend Table

## Schema Definition
| Column | Type | Description | Constraints / Notes |
|---|---|---|---|
| `date` | DATE | The day the spend occurred. | Partitioning key. |
| `campaign_id` | STRING | Internal campaign identifier. | Maps to `users.acquisition_campaign_id`. |
| `channel` | STRING | Advertising platform. | `'google_ads'`, `'meta'`, `'linkedin'`. |
| `spend_amount` | FLOAT | Total spend in USD for that day/campaign. | |
| `impressions` | INT | Total ad impressions. | |

## Data Latency
Marketing data has a 48-hour latency due to API attribution windows. Do not calculate CAC for the current or previous day; it will be incomplete.