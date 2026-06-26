# Security Policy

## Supported Versions

We currently provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |
| < 1.0   | :x:                |

## Reporting a Vulnerability

Security is a core priority for an AI Operating System dealing with corporate or personal memory data. 

If you discover a security vulnerability, please **DO NOT** open a public issue.

Instead, please send an email to: **[MAINTAINER: Insert Security Contact Email Here]**

We will acknowledge your report within 48 hours and provide a timeline for triage and resolution. 

## Disclosure Policy

* We will privately patch the vulnerability and request a CVE if applicable.
* We will credit the reporter in our release notes (unless you wish to remain anonymous).
* We ask that reporters abide by coordinated disclosure and wait until a patch is released before publishing details.

## Security Best Practices

When deploying BizOS, ensure you follow these practices:
* **Never commit `.env` files** or hardcode API keys (Supabase, Gemini, OpenAI).
* **Network Isolation:** Ensure Qdrant and PostgreSQL are not exposed to the public internet. They should only be accessible via the FastAPI backend.
* **Secrets Management:** Use Doppler, HashiCorp Vault, or AWS Secrets Manager in production instead of plain `.env` files where possible.
* **Authentication:** The current `v2.0.0` architecture defers Authentication to an API Gateway (e.g., Kong, AWS API Gateway) or a proxy. Do not expose BizOS directly to the internet without an AuthZ layer protecting the endpoints.
