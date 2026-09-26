---
type: Product Documentation
title: Feature Flags System
description: System for managing feature rollouts, A/B tests, and kill switches.
owner: product-engineering@company.com
tool: LaunchDarkly
environments: [development, staging, production]
related_infrastructure:
  - ../infrastructure/deployment_pipeline.md
related_product:
  - ./api_contracts.md
---
# Feature Flags System

## Overview
Feature flags allow us to:
- Deploy code to production without releasing features to users
- Run A/B tests and experiments
- Quickly disable features during incidents (kill switches)
- Gradually roll out features to percentages of users

## Flag Types

### 1. Release Flags
- **Purpose**: Control feature availability during rollout
- **Lifecycle**: Created → Gradual rollout (10% → 50% → 100%) → Removed from code
- **Duration**: Maximum 30 days (then must be removed or made permanent)
- **Example**: `new-checkout-flow`

### 2. Experiment Flags
- **Purpose**: A/B testing and multivariate experiments
- **Lifecycle**: Created → Experiment running → Winner selected → Flag removed
- **Duration**: Minimum 2 weeks (statistical significance)
- **Example**: `pricing-page-redesign` (variants: `control`, `variant-a`, `variant-b`)

### 3. Ops Flags (Kill Switches)
- **Purpose**: Quickly disable features during incidents
- **Lifecycle**: Permanent (never removed from code)
- **Default**: Always `true` (feature enabled)
- **Example**: `payment-processing-enabled`, `email-notifications-enabled`

### 4. Permission Flags
- **Purpose**: Control access to features based on user attributes
- **Targeting Rules**: User role, plan type, geographic region, beta tester status
- **Example**: `advanced-analytics` (only for `enterprise` plan users)

## Flag Naming Convention
- Format: `<team>-<feature>-<type>`
- Examples:
  - `checkout-new-flow-release`
  - `pricing-redesign-experiment`
  - `payments-killswitch-ops`
  - `analytics-advanced-permission`

## Implementation

### SDK Integration
```javascript
// Initialize LaunchDarkly client
const ldClient = LDClient.initialize('client-side-id', userContext);

// Check flag value
const showNewCheckout = ldClient.variation('checkout-new-flow-release', false);

if (showNewCheckout) {
  renderNewCheckoutFlow();
} else {
  renderLegacyCheckoutFlow();
}