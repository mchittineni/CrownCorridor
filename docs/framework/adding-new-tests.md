# Adding New Benchmark Scenarios to IaCSecBench

This step-by-step guide explains how to add new security test scenarios to the benchmark suite.

---

## ➕ Step 1: Register the Case in `benchmark/benchmark.json`

Append your new test case entry to the `test_cases` array of the master catalog (mirror the same entry in `benchmark/datasets/benchmarks.json`). Case IDs follow the `<CATEGORY>-<NNN>` convention (e.g. `STO-031`):

```json
{
  "id": "ENC-031",
  "module": "database",
  "category": "ENC",
  "has_violation": true,
  "title": "Encryption Benchmark Scenario #31 (FAIL)",
  "description": "DynamoDB table missing KMS encryption key.",
  "terraform_module": "infrastructure/modules/database",
  "terraform_version": "1.15.0",
  "provider": "aws",
  "expected_result": "FAIL",
  "severity": "HIGH",
  "benchmark_category": "ENC",
  "cis_control": "2.3.1",
  "mitre_attack": "T1530",
  "owasp_category": "A02:2021-Cryptographic Failures",
  "tags": ["encryption", "fail", "medium"],
  "difficulty": "Medium",
  "benchmark_features": ["locals", "for_each"]
}
```

---

## 🧪 Step 2: Add a Self-Contained Case Folder

Create a matching folder under `benchmark/internal/cases/<CASE-ID>/` containing the Terraform scenario and its ground truth:

```
benchmark/internal/cases/ENC-031/
├── main.tf         # The Terraform scenario under test
├── variables.tf    # Input variables (if any)
├── expected.json   # Ground truth: expected_result, severity, violations[]
└── metadata.json   # Case metadata (category, difficulty, constructs)
```

Example `expected.json` (see [benchmark_protocol.md](../benchmark_protocol.md) for the full ground truth format):

```json
{
  "benchmark_id": "ENC-031",
  "expected_result": "FAIL",
  "severity": "HIGH",
  "violations": [
    {
      "resource": "aws_dynamodb_table.unencrypted",
      "property": "server_side_encryption",
      "rule_id": "CIS_AWS_2.3_1",
      "description": "DynamoDB table missing KMS encryption key"
    }
  ]
}
```

---

## 🔄 Step 3: Re-run the Reproducible Suite

Execute the test harness to verify your scenario is processed and the leaderboard regenerates cleanly:

```bash
python evaluation/score.py
./experiments/run_all.sh
```

Finally, update the category case counts in [docs/taxonomy.md](../taxonomy.md) if your addition changes the allocation table.
