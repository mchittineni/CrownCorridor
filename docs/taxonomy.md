# IaCSecBench — Research Benchmark Taxonomy

This document outlines the hierarchical taxonomy of **IaCSecBench**, a publication-grade Infrastructure as Code (IaC) security, privacy, quality, and performance benchmark suite.

---

## Benchmark Hierarchy

> **Read this first.** The hierarchy and the allocation table below describe the
> *designed* taxonomy — the target shape of a complete corpus. They are not a
> census of what exists. The corpus currently present on disk is smaller and
> covers fewer domains, and every metric in this repository is computed over the
> present-and-admissible cases only. Both numbers are reported side by side in
> `results/corpus_report.json`; see [Present Corpus](#present-corpus) below.

```
IaCSecBench (designed taxonomy)
├── 1. Internal Controlled Benchmark (345 Cases, designed)
│   ├── IAM (Identity & Access Management)
│   ├── Networking (VPC, Security Groups, ALB, Firewalls)
│   ├── Storage (S3, EFS, EBS, Block Storage)
│   ├── Encryption (KMS, TLS/SSL, Data-at-Rest, Transit)
│   ├── Compute (EC2, AutoScaling, EKS, Container Registries)
│   ├── Kubernetes (Pods, RBAC, Network Policies, SecurityContext)
│   ├── Serverless (Lambda, API Gateway, EventBridge)
│   ├── Logging & Monitoring (CloudTrail, VPC Flow Logs, GuardDuty)
│   ├── Secrets (Hardcoded Keys, SSM Parameter Store, Vault)
│   ├── Identity (SSO, IAM Identity Center, OIDC Federated Roles)
│   ├── PII (Personally Identifiable Information Scrubbing)
│   └── Terraform Quality & Native Testing (HCL2, Variable Validation, .tftest.hcl)
│
├── 2. External Validation Datasets (175 Cases declared by manifest; 4 present)
│   ├── Terraform Registry Modules (declares 50 — no configurations on disk)
│   ├── SecureFlag IaC Vulnerabilities (declares 75 — no configurations on disk)
│   └── CIS AWS Misconfigurations (declares 50 — 4 configurations on disk)
│
├── 3. Operational Production Observation
│   └── 61 Continuous Integration Pull Requests
│
└── Designed total: 581 scenarios. Present and admissible: see corpus report.
```

---

## Category Breakdown & Case Allocation — DESIGN TARGET, NOT A CENSUS

The `Total Cases` and `Target Split` columns state the intended allocation for a
complete corpus. Four of the twelve domains below (K8S, ID, PII, TF) have no
cases on disk at all, so no metric in this repository is computed over them.
Quoting a number from this table as a measured corpus size would overstate the
evaluation by roughly an order of magnitude.


| Category Code | Domain            | Description                                                           | Total Cases | Target Split (Secure / Insecure) |
| :------------ | :---------------- | :-------------------------------------------------------------------- | :---------: | :------------------------------: |
| **IAM**       | Identity & Access | IAM roles, wildcard policies, privilege escalation, inline policies   |     35      |        18 Pass / 17 Fail         |
| **NET**       | Networking        | Security groups, public ingress, VPC Flow Logs, ALB drop headers      |     35      |        18 Pass / 17 Fail         |
| **STO**       | Storage           | S3 bucket public access, versioning, Object Lock, EBS encryption      |     30      |        15 Pass / 15 Fail         |
| **ENC**       | Encryption        | KMS key rotation, TLS 1.2+ constraints, RDS/DynamoDB KMS encryption   |     30      |        15 Pass / 15 Fail         |
| **CMP**       | Compute           | IMDSv2 enforcement, public IP assignment, ECR image scanning          |     30      |        15 Pass / 15 Fail         |
| **K8S**       | Kubernetes        | Pod Security Standards, privileged containers, RBAC wildcard bindings |     35      |        18 Pass / 17 Fail         |
| **SRV**       | Serverless        | Lambda execution roles, API Gateway throttling & CORS configurations  |     25      |        13 Pass / 12 Fail         |
| **MON**       | Logging & Audit   | CloudTrail multi-region logging, GuardDuty, Security Hub enablement   |     25      |        13 Pass / 12 Fail         |
| **SEC**       | Secrets           | Zero hardcoded keys, SSM parameter encryption, Vault integrations     |     30      |        15 Pass / 15 Fail         |
| **ID**        | Federated Auth    | SAML / OIDC trust policies, MFA enforcement, federated roles          |     20      |        10 Pass / 10 Fail         |
| **PII**       | Data Privacy      | Zero PII customer names/emails/phones in IaC tags & metadata          |     25      |        13 Pass / 12 Fail         |
| **TF**        | HCL Quality       | Native `.tftest.hcl`, variable validation, dynamic blocks, for_each   |     25      |        12 Pass / 13 Fail         |

---

## Present Corpus

What actually exists and is scanned, as distinct from the design target above:

| | Cases |
| :--- | :---: |
| Internal, present on disk | 44 (22 vulnerable / 22 compliant) |
| External, present on disk | 4 (CIS AWS examples, all vulnerable) |
| **Total admissible** | **48 (26 vulnerable / 22 compliant)** |

Domains with cases present: IAM, NET, STO, ENC, CMP, MON, SEC, SRV.
Domains designed but absent: K8S, ID, PII, TF.

The canonical control taxonomy defines 28 controls, of which 22 are exercised by
at least one present case. The remaining six are defined but unmeasured, and are
reported as such rather than counted as covered.

Regenerate these counts rather than trusting them:

```bash
python -m evaluation.corpus --report --mode terraform
```

---

## Benchmark Construct Badges (`benchmark_features`)

Test cases exercise modern, complex Terraform constructs to evaluate parser robustness:

- `dynamic_blocks`: Nested `dynamic` HCL block evaluation.
- `nested_modules`: Multi-level child module instantiation.
- `remote_module`: External Git / Terraform Registry module sources.
- `locals`: Complex local variable expressions and data manipulation.
- `for_each`: Resource map iterations.
- `count`: Conditional resource provisioning via `count = var.enabled ? 1 : 0`.
- `variable_validation`: Input variable custom validation rules.
- `depends_on`: Explicit dependency graph declarations.
- `lifecycle_rules`: Prevent destroy and ignore changes configuration.
- `tfvars`: Environment-specific variable file overrides.
- `opa`: Open Policy Agent Rego policy constraints.
- `native_tests`: Native `.tftest.hcl` assertions.
