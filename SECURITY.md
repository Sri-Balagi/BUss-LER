# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 6.0.x   | ✅ Active |
| 5.x     | ⚠️ Security patches only |
| < 5.0   | ❌ End of life |

## Reporting a Vulnerability

BizOS handles sensitive organizational data. Security is a core priority.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities via: **security@bizos.ai** (or your configured security contact)

We will:
- Acknowledge within **48 hours**
- Provide a resolution timeline within **5 business days**
- Issue a CVE if applicable
- Credit the reporter in release notes (unless anonymity is requested)

Please allow time for a patch before public disclosure (coordinated disclosure).

---

## Security Architecture

### Defense in Depth

| Layer | Controls |
|-------|---------|
| HTTP | Security headers (HSTS, X-Frame-Options, X-Content-Type-Options, Permissions-Policy) |
| Transport | TLS enforced in production (HSTS: max-age=31536000) |
| API | Input validation via Pydantic v2 on all endpoints |
| Config | Startup validation of all required secrets (fails fast on invalid config) |
| Secrets | Never logged, never included in responses |
| Metrics | `/metrics` endpoint — internal network only in production |

### API Keys

All API keys (Supabase, Gemini) are:
- Validated at startup (minimum length check)
- Never exposed in logs, responses, or error messages
- Loaded exclusively from environment variables

### CORS

- Development: `*` (permissive)
- Production: Set `CORS_ORIGINS` to specific allowed domains

### Authentication

BizOS uses Supabase RLS (Row Level Security) for data isolation.
Do NOT expose the Supabase service role key to client-side code.

---

## Production Hardening Checklist

- [ ] `APP_ENV=production`, `APP_DEBUG=false`
- [ ] `CORS_ORIGINS` restricted to your domain
- [ ] `/metrics` not publicly exposed (bind to internal network)
- [ ] `/docs` and `/redoc` disabled (automatic when `APP_DEBUG=false`)
- [ ] TLS termination at load balancer
- [ ] Secrets injected via CI/CD secrets, not committed to git
- [ ] Supabase RLS enabled on all tables
- [ ] Dependency audit passing: `uv run pip-audit`
- [ ] Docker image scanned for CVEs before deployment

---

## Dependency Security

Run weekly: `uv run pip-audit`

The GitHub Actions `security.yml` workflow runs this automatically on every push to main
and on a weekly schedule.

---

## Known Limitations

- BizOS does not implement rate limiting internally. Use a reverse proxy (Nginx, Cloudflare, AWS WAF) for rate limiting in production.
- Session-based authentication is not implemented in v6.0.0. This is planned for v7.