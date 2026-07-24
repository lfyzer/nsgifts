# Changelog

All notable changes to this project are documented in this file.

The format follows Keep a Changelog and Semantic Versioning.

## [2.0.0] - 2026-07-24

### Breaking

- Migrated the complete client from NS.Gifts API v1 to API v2.
- Replaced Bearer-only authentication with `user_id`, API-secret HMAC, and a
  short-lived `X-Token`.
- Replaced fixed order `quantity` and `data` arguments with dynamic
  `OrderField` values from `/stock`.
- Renamed the public groups to `account`, `catalog`, `orders`, and `steam`.
- Changed order creation, payment, and lookup to `create`, `pay`, and `get`.
- Raised the minimum supported Python version to 3.10.

### Added

- Exact HMAC-SHA256 signing of transmitted JSON bytes.
- Two-hour token lifecycle with lock-protected lazy refresh.
- Replay protection for identical requests within one process.
- Bounded bootstrap retry for cross-process replay collisions.
- Coalesced refresh when concurrent requests reject the same session token.
- Typed `/stock`, balance, order, exchange-rate, Steam apps, and Steam user
  models.
- PEP 561 metadata for type checking installed distributions.
- UUID4 validation and automatic `custom_id` generation.
- `Decimal` parsing for all monetary response values.
- TOTP support for purchase 2FA.
- `.env.example` and `NSGIFTS_*` settings through `pydantic-settings`.
- Complete English and Russian API v2 documentation.
- Unit tests for signing, retries, models, methods, secrets, and lifecycle.

### Changed

- Catalog access now uses the single partner-specific `GET /api/v2/stock`
  endpoint.
- Steam Gift creation and payment now use the common order flow.
- `order_info` now uses a path UUID and an HTTP GET request.
- Balance and Steam applications now use HTTP GET.
- Currency rates use `POST /api/v2/exchange_rate`.
- Logging is isolated to the package logger and never changes the root logger.

### Removed

- API v1 endpoint paths and compatibility aliases.
- Signup and user-info methods.
- API-managed IP whitelist methods.
- Separate category and service listing methods.
- Legacy Steam amount and Steam Gift create/pay/calculate methods.
- Bearer JWT refresh logic and v1 response models.

### Security

- Passwords, API secrets, session tokens, signatures, and TOTP codes are
  masked in representations and redacted from diagnostic fields and messages.
- Redirects are disabled for signed requests.
- Clear-text HTTP base URLs are rejected.
- Unsafe order creation and payment requests are not retried after uncertain
  network, response-stream, or server outcomes.
- `401` retries are limited to explicit replay and stale-token failures.
- `429`, `409`, `428`, IP whitelist, timestamp, and authentication failures
  have explicit error handling.
- Agent metadata, environment secrets, caches, coverage, and build artifacts
  are excluded from Git.

### Migration

- Request a `user_id` and Base64 API-secret from NS.Gifts support.
- Ask support to add the caller's public IP to the API whitelist.
- Replace v1 environment values with the documented `NSGIFTS_*` variables.
- Read `/stock` and build dynamic `OrderField` lists before creating orders.
- Replace all v1 method calls using the migration tables in `README.md`.
- Treat a payment timeout as unknown and reconcile through `orders.get()`.

[2.0.0]: https://github.com/lfyzer/nsgifts/releases/tag/v2.0.0
