# Security Policy

This project consists of a **static web portal and localized data files** for Andhra Pradesh and Telangana. There is no backend server storing user credentials, session logins, or private transaction records. All transaction data displayed is simulated/mocked based on public boundaries.

## Supported Versions

The deployed site always tracks the latest commit on `main`. Only `main` is supported; please report issues against the current version.

| Version             | Supported |
| ------------------- | --------- |
| `main` (latest)     | ✅        |
| older tags/releases | ❌        |

## Reporting a Vulnerability

Please **do not open a public issue** for security problems.

Instead, please report security concerns via **GitHub Private Vulnerability Reporting** or contact the repository maintainers privately.

When reporting, please include:
- A description of the issue and its potential impact
- Steps to reproduce (and a proof of concept if possible)
- The affected page/URL or file

We aim to acknowledge reports within a few days and to address confirmed issues promptly. Relevant examples include cross-site scripting (XSS) in map overlays, dependency vulnerabilities in CDNs, or configuration problems in GitHub deployment workflows.
