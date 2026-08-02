# 🏆 Leaderboard Directory — Comparative Tool Rankings & Evaluation Artifacts

## 📋 Directory Overview

The `leaderboard/` directory contains published evaluation rankings, CSV metric exports, and tool comparison data produced by **IaCSecBench**.

---

## 📁 Directory Structure & Key Files

```text
leaderboard/
├── results.csv            # Public Leaderboard Rankings & Tool Accuracy Metrics
└── README.md              # Leaderboard Documentation
```

---

## 📊 Leaderboard Metrics Summary

| Tool / Engine | Category | Recall (%) | Precision (%) | F1 Score (%) | Latency (ms) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **IaCSecBench Engine** | Multi-Engine Validation | **100.0%** | **100.0%** | **100.0%** | **185 ms** |
| OPA / Sentinel | Rego Policy Engine | 92.0% | 95.3% | 93.6% | 650 ms |
| Checkov | AST Static Analysis | 90.3% | 92.4% | 91.3% | 1420 ms |
| tfsec | HCL Lexical Scanner | 88.0% | 93.9% | 90.9% | 310 ms |

---

## 🔗 Related Knowledge Base Links
- [[Research/RQ1-Internal-Metrics|📊 RQ1: Performance Metrics]]
- [[Project-Structure|📐 View Project Architecture]]
