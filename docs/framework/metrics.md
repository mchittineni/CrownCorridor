# Benchmark Evaluation Metrics Reference

This document defines the metrics measured by **IaCSecBench**.

> [!IMPORTANT]
> The **Target Goal** column states design aspirations, **not measured results**. No tool
> in this benchmark meets all of them: the best measured recall is 88.46% against a 100%
> target, and the fastest source-level scanner takes 419 ms against a < 200 ms target.
> Measured values live in `results/evaluation.json` and the generated tables in
> `results/tables/`; nothing in this table is a finding.

| Metric                  | Short Name | Definition                                                                                                    | Target Goal |
| :---------------------- | :--------- | :------------------------------------------------------------------------------------------------------------ | :---------- |
| **Accuracy**            | ACC        | Percentage of total benchmark predictions (violations and compliant cases) correctly classified.              | > 95%       |
| **Precision**           | PREC       | Ratio of true detected security violations to all reported violations (low false positive rate).              | > 95%       |
| **Recall**              | REC        | Ratio of true detected security violations to actual total vulnerabilities present (low false negative rate). | 100%        |
| **F1 Score**            | F1         | Harmonic mean of Precision and Recall.                                                                        | > 95%       |
| **False Positive Rate** | FPR        | Rate of false alarms on secure/compliant benchmark cases.                                                     | < 5%        |
| **False Negative Rate** | FNR        | Rate of missed security vulnerabilities on insecure cases.                                                    | 0%          |
| **Execution Latency**   | LAT        | Total elapsed clock time (in ms) to parse, evaluate policies, and generate telemetry reports.                 | < 200 ms    |
| **PII Exposure**        | PII        | Total count of unmasked personal data strings or secrets detected in IaC configurations.                      | 0           |
