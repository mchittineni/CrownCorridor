# IaCSecBench Benchmark Methodology

This document outlines the evaluation methodology and metrics used to benchmark Infrastructure-as-Code security tools.

---

## 🔬 Benchmark Dataset Design

The benchmark suite (`benchmark/datasets/benchmarks.json`) contains annotated test scenarios covering 5 critical vulnerability categories:

1. **ENCRYPTION**: Missing S3 bucket encryption, RDS KMS storage encryption, CloudFront TLS policies.
2. **NETWORKING**: Security groups allowing `0.0.0.0/0` ingress on port 22/3389, missing ALB header dropping.
3. **SECRETS**: Hardcoded AWS secret access keys, plain database passwords, API tokens.
4. **TESTING**: Missing native `.tftest.hcl` validation blocks.
5. **PII**: Customer personal identity strings or phone numbers stored in IaC tags.

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

- **Latency (ms)**: Total execution runtime measured in milliseconds per scan round.
