# IaCSecBench Threat Model

## Overview

This document describes the primary threat model for the IaCSecBench security benchmark framework and the Crown Corridor infrastructure reference architecture.

## Assets

- IaCSecBench benchmark datasets (`benchmark/benchmark.json`, `benchmark/cases/`)
- Security evaluation engine (`security_framework/engine/engine.py`)
- OPA / Rego policy definitions (`security_framework/policies/`)
- Terraform reference architecture (`infrastructure/`)
- Application authentication and identity management (`infrastructure/modules/auth/`)
- Secret and PII scanning rules
- Reproducible experiment telemetry and benchmark outputs (`experiments/`, `results/`)

## Trust boundaries

- Developer workspace vs repository contents
- Benchmark engine runtime vs target IaC repository
- IaC inputs vs evaluation policy engine
- Application user client vs Cognito authentication
- Infrastructure deployment pipeline vs cloud provider APIs

## Threat categories (STRIDE)

### Spoofing

- Threat: attacker impersonates a user or service in the evaluation framework
- Assets: Cognito authentication, API tokens, GitHub CI credentials
- Mitigations:
  - Require strong authentication and MFA
  - Use AWS Cognito advanced security mode
  - Avoid hardcoded credentials in source code
  - Protect CI secrets and repository tokens

### Tampering

- Threat: attacker modifies benchmark datasets, policy definitions, or evaluation results
- Assets: `benchmark/`, `security_framework/policies/`, `results/`, `docs/`
- Mitigations:
  - Maintain benchmarks and policy code under version control
  - Verify file integrity in reproducible experiment workflows
  - Use signed release artifacts and cryptographic checksums where applicable

### Repudiation

- Threat: lack of audit or telemetry makes it difficult to prove changes or evaluation decisions
- Assets: benchmark execution logs, CI run output, experiment metadata
- Mitigations:
  - Record execution metadata and tool versions
  - Preserve experiment outputs in reproducible results artifacts
  - Use clear vulnerability reporting procedures in `SECURITY.md`

### Information Disclosure

- Threat: secrets, PII, or sensitive configurations leak via repository contents or scan outputs
- Assets: source files, Terraform variables, benchmark case metadata
- Mitigations:
  - Zero-PII scanning and hardcoded secret detection
  - Exclude customer data from benchmark datasets
  - Use GitHub Actions secret masking and CI validation

### Denial of Service

- Threat: a malicious or malformed benchmark case consumes excessive resources during evaluation
- Assets: engine execution, CI runners, experiment harness
- Mitigations:
  - Limit the scope of benchmark test case evaluation
  - Validate input file structure and avoid unbounded parsing loops
  - Use execution time telemetry and resource constraints

### Elevation of Privilege

- Threat: a malicious benchmark case or policy rule bypasses protection checks or grants unauthorized access
- Assets: evaluation engine, Terraform modules, authentication controls
- Mitigations:
  - Use policy-as-code rules with explicit deny semantics
  - Evaluate CIS and security benchmark rules consistently
  - Require MFA and strong auth settings in Cognito

## Attacker capabilities

- Low: scanning or probing the repository for sensitive data or policy gaps
- Medium: modifying benchmark or policy files in a fork or PR
- High: gaining access to CI credentials or deployment secrets

## Residual risk and recommendations

- Maintain a formal release process for benchmark datasets and policy updates.
- Treat benchmark case authorship as a security-sensitive activity.
- Continuously validate all IaC and policy changes with CI and reproducible experiments.
- Keep the threat model updated as the framework evolves.
