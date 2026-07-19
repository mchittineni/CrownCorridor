# Security Policy

Crown Corridor is a **static web portal with a lean server-side data pipeline**.
There is no backend storing user credentials, session tokens, or private records.
All transaction data is simulated and no personally identifiable information (PII)
is collected or stored by the portal.

---

## Supported Versions

The deployed site always tracks the latest commit on `main`. Only `main` is supported.

| Version                 | Supported       |
| ----------------------- | --------------- |
| `main` (latest)         | ✅              |
| `develop` (pre-release) | ⚠️ Testing only |
| Older tags / releases   | ❌              |

---

## Scope

The following components are **in scope** for security reports:

| Component               | Examples of relevant issues                                  |
| ----------------------- | ------------------------------------------------------------ |
| `app/portal.js`         | XSS via unsanitised map popup content, prototype pollution   |
| `app/index.html`        | Missing CSP headers, insecure CDN SRI hashes                 |
| `.github/workflows/`    | Secret exfiltration, workflow injection via untrusted inputs |
| `.github/actions/`      | Supply-chain risks in composite action steps                 |
| CDN dependencies        | Known CVEs in Leaflet, MapLibre GL, Chart.js, or PMTiles     |
| `pipeline/fetch_sro.py` | SSRF risk if URL inputs become user-controlled               |

The following are **out of scope**:

- Simulated/mock transaction data (it is intentionally synthetic).
- GitHub Pages infrastructure itself (report to GitHub).
- Rate-limiting or DoS on static file hosting.

---

## CDN Dependencies

The portal loads the following third-party scripts from CDN. If a CVE is found
in any of these libraries, please report it:

| Library             | Version pinned in `app/index.html` |
| ------------------- | ---------------------------------- |
| Leaflet             | 1.9.x                              |
| MapLibre GL JS      | 4.x                                |
| leaflet-maplibre-gl | latest                             |
| PMTiles JS          | latest                             |
| Chart.js            | 4.x                                |

All CDN `<script>` tags should have `integrity` (SRI) attributes. If you find a
tag missing an SRI hash, that is a valid security report.

---

## Reporting a Vulnerability

**Do not open a public GitHub issue for security problems.**

Use one of these private channels:

1. **GitHub Private Vulnerability Reporting** — go to the repository's
   [Security tab](https://github.com/mchittineni/CrownCorridor/security) and
   click _Report a vulnerability_.
2. **Direct contact** — reach the maintainer via the email listed on the
   GitHub profile.

### What to include

- A clear description of the issue and its potential impact.
- Steps to reproduce (with a proof of concept if possible).
- The affected file, URL, or workflow path.
- Your suggested fix or mitigation (optional but appreciated).

### Response timeline

| Action                                 | Target time                                   |
| -------------------------------------- | --------------------------------------------- |
| Acknowledgement                        | Within 3 business days                        |
| Triage and severity assessment         | Within 7 days                                 |
| Fix or mitigation for confirmed issues | Depends on severity — critical within 14 days |

We follow [responsible disclosure](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html):
confirmed vulnerabilities will be patched before any public disclosure.
