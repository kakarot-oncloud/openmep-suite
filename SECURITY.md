# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | ✅ Yes    |
| 0.1.x   | ✅ Yes    |

## Reporting a Vulnerability

OpenMEP is an engineering calculation tool. Two categories of issues require private, responsible disclosure:

### 1. Calculation Errors Affecting Safety

If you discover a bug where OpenMEP produces an **incorrect result that could lead to an unsafe design** (e.g., undersizing a cable, undersizing a fire pump, incorrect short-circuit current), please report it **privately** before posting publicly.

**Why?** Engineers may have already generated reports using the incorrect calculation. A public disclosure gives time to notify users before they act on incorrect results.

### 2. Software Security Vulnerabilities

If you discover a security vulnerability in the API server, Streamlit app, or Docker configuration (e.g., injection attack, credential exposure, remote code execution):

- **Do not** open a public GitHub issue
- **Do** email the maintainers at the address listed in the GitHub repository
- Include: description, reproduction steps, affected versions, potential impact
- You will receive a response within 72 hours
- We aim to release a fix within 14 days of confirmed vulnerabilities

## Disclosure Timeline

1. **Day 0** — Report received, acknowledged within 24 hours
2. **Day 7** — Fix developed and tested internally
3. **Day 14** — Fix released as a patch version
4. **Day 21** — Public disclosure with credit to the reporter (unless reporter requests anonymity)

## Security Design Notes

### API Authentication (v0.2.0+)

OpenMEP includes optional API key authentication. When the `API_KEY` environment variable is set, every API request must include the header:

```
X-API-Key: <your-key>
```

The following paths are always public (no auth required):
- `GET /` — API status
- `GET /health` — health check
- `GET /docs` — Swagger UI
- `GET /redoc` — ReDoc
- `GET /openapi.json` — OpenAPI schema

When `API_KEY` is **not** set (the default), the API operates in open mode — appropriate for local development and deployments on private networks or behind a reverse proxy that handles authentication at the network layer.

To generate a strong API key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add it to your `.env` file:
```
API_KEY=<generated-key>
```

### Container Security

- Containers run as a non-root user (`appuser`) — the Dockerfile creates a dedicated system user and `chown`s the application directory before switching with `USER appuser`
- The `docker-compose.yml` `api` and `streamlit` services each run a single process — no process supervision anti-patterns

### Other Notes

- All calculation inputs are validated by Pydantic v2 before processing
- No user data is persisted in the default configuration (stateless)
- Docker secrets are managed via environment variables — see `.env.example`
- CORS is restricted to configured origins — set `ALLOWED_ORIGINS` in production

## Responsible Disclosure Recognition

Reporters of valid security vulnerabilities will be listed in the `CHANGELOG.md` for the patched release (unless they prefer to remain anonymous).

---

*Made by Luquman A — Copyright © 2025 Luquman A. MIT License.*
