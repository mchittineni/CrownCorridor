# IaCSecBench Benchmark Methodology

This document outlines the evaluation methodology and metrics used to benchmark Infrastructure-as-Code security tools.

---

## 🔬 Benchmark Dataset Architecture & Design

The evaluation dataset consists of two primary components:

1. **IaCSecBench Controlled Benchmark (Internal)**: 345 labelled cases across 12 core infrastructure domains (IAM, Networking, Storage, Encryption, Compute, Kubernetes, Serverless, Monitoring, Secrets, Identity, Zero-PII, Terraform Native).
2. **External Validation Collection**: 175 independent cases evaluating scanner generalizability across external, unseen IaC security cases.

```
                 IaCSecBench
                      |
        ------------------------------
        |             |              |
 Internal        External       Production
 Benchmark       Validation     Observation
 345 cases       175 cases        61 PRs
```

### Internal Benchmark Dataset Composition

The internal benchmark suite contains 345 self-contained test scenarios across 12 infrastructure domains:

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

| Dataset | Source | Cases | Purpose |
| :--- | :--- | :---: | :--- |
| **Terraform Registry** | Open-source modules (VPC, EKS, RDS, IAM, Security Groups) | 50 | Real-world HCL complexity, dynamic blocks, variables, nested resources |
| **SecureFlag** | Intentionally vulnerable security scenarios | 75 | Real-world vulnerability patterns (public S3, open SG, insecure IAM, unencrypted RDS) |
| **CIS Benchmark** | Compliance-driven security controls | 50 | Compliance-driven security failure scenarios mapped directly to CIS AWS Foundations Benchmark v3 |


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
