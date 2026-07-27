# Adding New Benchmark Scenarios to IaCSecBench

This step-by-step guide explains how to add new security test scenarios to the benchmark suite.

---

## ➕ Step 1: Update `benchmark/datasets/benchmarks.json`

Append your new test case entry to `test_cases`:

```json
{
  "id": "TC-11",
  "module": "database",
  "category": "ENCRYPTION",
  "rule": "DynamoDB Table Missing KMS Encryption Key",
  "has_violation": true,
  "severity": "HIGH",
  "cis_control": "CIS 2.3.1"
}
```

---

## 🧪 Step 2: Add Target Terraform Scenario File

Add a corresponding test file under `benchmark/scenarios/`:

```hcl
# benchmark/scenarios/tc11_dynamodb.tf
resource "aws_dynamodb_table" "unencrypted" {
  name         = "user_sessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "UserId"

  attribute {
    name = "UserId"
    type = "S"
  }
}
```

---

## 🔄 Step 3: Re-run Reproducible Suite

Execute the test harness to verify your scenario is processed:

```bash
./experiments/run_all.sh
```
