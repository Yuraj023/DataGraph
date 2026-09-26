---
type: Product Documentation
title: API Contracts & Standards
description: Standards and contracts for internal and external APIs.
owner: platform-engineering@company.com
version: 2.3
last_updated: 2026-09-15
related_infrastructure:
  - ../infrastructure/deployment_pipeline.md
related_security:
  - ../security/access_control.md
---
# API Contracts & Standards

## API Design Principles

### 1. RESTful Standards
- Use nouns for resources: `/users`, `/subscriptions` (not `/getUsers`)
- Use HTTP methods correctly: GET (read), POST (create), PUT (update), DELETE (remove)
- Return appropriate status codes: 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error)

### 2. Versioning
- URL-based versioning: `/api/v1/users`, `/api/v2/users`
- Deprecation policy: 6-month notice before removing old versions
- Sunset headers: `Sunset: Sat, 01 Mar 2027 00:00:00 GMT`

### 3. Authentication
- **Internal APIs**: JWT tokens (issued by Auth0)
- **External APIs**: API keys (issued via developer portal)
- **Rate Limiting**: 1000 requests/minute per API key

## Request/Response Format

### Standard Request
```http
GET /api/v1/users/{user_id} HTTP/1.1
Host: api.company.com
Authorization: Bearer <jwt_token>
Content-Type: application/json