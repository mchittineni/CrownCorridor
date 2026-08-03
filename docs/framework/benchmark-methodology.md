# IaCSecBench Benchmark Methodology

This document outlines the evaluation methodology and metrics used to benchmark Infrastructure-as-Code security tools.

---

## 🔬 Benchmark Dataset Architecture & Design

The evaluation dataset consists of two primary components:

1. **IaCSecBench Controlled Benchmark (Internal)** — labelled vulnerable/compliant
   pairs, each self-contained and validated against its declared provider.
2. **External Validation Collection** — independently sourced configurations, used
   as a check that the harness operates on cases it did not generate.

The design target is 345 internal and 175 external cases across 12 domains. What
is **present and admissible** is smaller, and only the present figure is ever a
denominator here:

```
                 IaCSecBench
                      |
        ------------------------------
        |             |              |
 Internal        External       Production
 Benchmark       Validation     Observation
 44 present      4 present         61 PRs
 (345 designed)  (175 declared)
```

The external gap is not attrition: two of the three external collections contain
no Terraform files at all, so their manifest entries are citations rather than
cases. `results/corpus_report.json` reports declared and present counts per
collection, and `evaluation/corpus.py` refuses to treat a declared count as a
usable one.

### Internal Benchmark Dataset Composition

The domains below are the designed taxonomy. Four of them — K8S, ID, PII and TF —
have no cases on disk, so nothing is measured over them:

IAM: IAM roles, wildcard policies, privilege escalation, inline statements.
NET: Security groups open to 0.0.0.0/0, public SSH/RDP, ALB drop headers, VPC flow logs.
STO: S3 bucket public access blocks, versioning, Object Lock, EBS encryption.
ENC: KMS key rotation, TLS 1.2+ minimum protocols, RDS/DynamoDB KMS encryption.
CMP: IMDSv2 enforcement, public IP assignment, ECR image vulnerability scanning.
K8S: Pod Security Standards, privileged containers, RBAC wildcard bindings.
SRV: Lambda execution roles, API Gateway throttling, CORS configuration.
MON: CloudTrail multi-region logging, GuardDuty, Security Hub enablement.
SEC: Zero hardcoded secrets, SSM Parameter Store encryption, Vault integrations.
ID: SAML / OIDC trust policies, MFA enforcement, federated role trust.
PII: Zero customer names, emails, or phone numbers in IaC tags and metadata.
TF: Native .tftest.hcl, custom variable validation, dynamic blocks, for_each.

### External Validation Dataset Composition

| Dataset                | Source                                                    | Cases | Purpose                                                                                          |
| :--------------------- | :-------------------------------------------------------- | :---: | :----------------------------------------------------------------------------------------------- |
| **Terraform Registry** | Open-source modules (VPC, EKS, RDS, IAM, Security Groups) |  50   | Real-world HCL complexity, dynamic blocks, variables, nested resources                           |
| **SecureFlag**         | Intentionally vulnerable security scenarios               |  75   | Real-world vulnerability patterns (public S3, open SG, insecure IAM, unencrypted RDS)            |
| **CIS Benchmark**      | Compliance-driven security controls                       |  50   | Compliance-driven security failure scenarios mapped directly to CIS AWS Foundations Benchmark v3 |

---

## 📊 Evaluation Formulae

For each evaluated tool:

- **Accuracy (%)**:
  \[
  \text{Accuracy} = \frac{TP + TN}{TP + FP + TN + FN} \times 100
  \]

- **Precision (%)**:
  \[
  \text{Precision} = \frac{TP}{TP + FP} \times 100
  \]

- **Recall (%)**:
  \[
  \text{Recall} = \frac{TP}{TP + FN} \times 100
  \]

- **F1 Score (%)**:
  \[
  \text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
  \]

- **False Positive Rate (FPR %)**:
  \[
  \text{FPR} = \frac{FP}{FP + TN} \times 100
  \]

- **False Negative Rate (FNR %)**:
  \[
  \text{FNR} = \frac{FN}{TP + FN} \times 100
  \]

- **Latency (ms)**: Total execution runtime measured in milliseconds per scan round.
