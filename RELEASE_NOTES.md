# Release v1.0.0

Release v1.0.0 — initial public release (ghosttrace-osint)

Highlights
- Restructured package into `ghosttrace/` with `ghosttrace/modules/`.
- CLI entrypoint maintained as `ghosttrace` and `console_scripts` configured.
- Environment-configured AbuseIPDB support: `ABUSEIPDB_KEY` (via env or `.env`).
- Added `--no-prompt` (`-n`) to skip the final press-Enter prompt for non-interactive runs.
- Robust handling for non-JSON upstream responses (rdap, crt.sh) to avoid crashes.
- Updated `README.md` with installation, configuration, and cleanup guidance.

Notes
- Package published on PyPI as `ghosttrace-osint` (to avoid name conflict).
- Git tag: `v1.0.0`

Security
- If you accidentally exposed a token (for example in a chat), revoke it immediately and rotate credentials.

Usage
```bash
pip install ghosttrace-osint
ghosttrace example.com --no-prompt
```
