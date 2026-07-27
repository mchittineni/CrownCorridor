# Benchmark Evaluation Metrics Reference

This document defines the metrics measured by **IaCSecBench**.

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
