# Security Policy & Vulnerability Disclosure

---

## 🔒 Security Commitments

We take the security of **IaCSecBench** seriously. We welcome security researchers and open-source contributors to inspect, test, and report security issues.

---

## 🛡️ Supported Versions

| Component                            | Version             | Supported |
| ------------------------------------ | ------------------- | --------- |
| IaCSecBench Engine                   | v1.0.x (latest)     | ✅ Yes    |
| AWS Terraform Reference Architecture | Terraform >= 1.15.0 | ✅ Yes    |

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability or secret leakage issue within this repository:

1. **Do NOT open a public GitHub issue**.
2. Report it privately through GitHub's
   [private vulnerability reporting](https://github.com/mchittineni/iacsecbench/security/advisories/new)
   on this repository, which opens a channel visible only to the maintainers.
3. Include the following details in your report:
   - Type of issue (e.g., secret leakage, policy bypass, logic flaw).
   - Component affected (scanner, evaluation harness, Terraform module, or policy set).
   - Step-by-step instructions to reproduce the flaw.

---

## ⏱️ Response SLA

- **Initial Response**: Within 48 hours.
- **Triage & Assessment**: Within 5 business days.
- **Fix & Patch Release**: High severity vulnerabilities will be patched within 14 business days.
