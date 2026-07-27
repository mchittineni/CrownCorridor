# IaCSecBench Benchmark Methodology

This document outlines the evaluation methodology and metrics used to benchmark Infrastructure-as-Code security tools.

---

## 🔬 Benchmark Dataset Design

The research benchmark suite ([benchmark/benchmark.json](file:///Users/manideepchittineni/Desktop/GitHub/Personal/CrownCorridor/benchmark/benchmark.json)) contains 345 self-contained test scenarios across 12 infrastructure domains:

1. **IAM**: IAM roles, wildcard policies, privilege escalation, inline statements.
2. **NET**: Security groups open to `0.0.0.0/0`, public SSH/RDP, ALB drop headers, VPC flow logs.
3. **STO**: S3 bucket public access blocks, versioning, Object Lock, EBS encryption.
4. **ENC**: KMS key rotation, TLS 1.2+ minimum protocols, RDS/DynamoDB KMS encryption.
5. **CMP**: IMDSv2 enforcement, public IP assignment, ECR image vulnerability scanning.
6. **K8S**: Pod Security Standards, privileged containers, RBAC wildcard bindings.
7. **SRV**: Lambda execution roles, API Gateway throttling, CORS configuration.
8. **MON**: CloudTrail multi-region logging, GuardDuty, Security Hub enablement.
9. **SEC**: Zero hardcoded secrets, SSM Parameter Store encryption, Vault integrations.
10. **ID**: SAML / OIDC trust policies, MFA enforcement, federated role trust.
11. **PII**: Zero customer names, emails, or phone numbers in IaC tags and metadata.
12. **TF**: Native `.tftest.hcl`, custom variable validation, dynamic blocks, `for_each`.

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
