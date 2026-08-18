# Security Policy

## Security Architecture & Philosophy

ScrollSense is built with a defense-in-depth, offline-first security posture:

1. **Zero Secrets in Repository**:
   - All `.env` and credential files are strictly excluded via `.gitignore`.
   - API keys are read exclusively from runtime process environment variables (`LLM_API_KEY`).
   - Default execution runs 100% offline via validated local cache files, requiring no external credentials or network egress.

2. **Strict Input Whitelisting & Schema Validation**:
   - API endpoints enforce strict JSON schema typing via Pydantic models.
   - Evaluation cases, signal extractors, explanation modes, and LLM providers are constrained to explicit enumeration whitelists.
   - Unknown fields, malformed payloads, or non-whitelisted parameters are rejected immediately with HTTP 422 Unprocessable Entity.

3. **No Dynamic Execution**:
   - The entire codebase uses static type-checked Python standard library modules.
   - `eval()`, `exec()`, and dynamic code generation are strictly prohibited.

4. **Security Headers**:
   The local UI demo server emits strict HTTP defense headers on every response:
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `Referrer-Policy: no-referrer`

5. **Deterministic Fail-Safe Fallback**:
   - If an optional AI endpoint fails, returns non-JSON, or violates schema boundaries, the pipeline automatically falls back to deterministic heuristic rules (`fallback_used = True`).
   - The system is physically incapable of exposing private API keys or failing open.

## Reporting a Vulnerability

If you discover a potential security issue in ScrollSense, please open a private GitHub advisory or contact the project maintainers directly. Vulnerabilities will be triaged and addressed promptly.
