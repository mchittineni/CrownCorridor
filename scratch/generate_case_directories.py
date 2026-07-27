"""Generates representative self-contained benchmark case folders under benchmark/cases/."""

import json
import os

def create_case_folders():
    with open("benchmark/benchmark.json", encoding="utf-8") as f:
        catalog = json.load(f)

    cases = catalog.get("test_cases", [])
    base_cases_dir = "benchmark/cases"
    os.makedirs(base_cases_dir, exist_ok=True)

    # Generate representative case directories for each category
    categories_seen = set()
    for case in cases:
        cat = case["benchmark_category"]
        case_id = case["id"]

        # Limit to top 3 cases per category to keep repository compact yet self-contained
        cat_count = sum(1 for c in categories_seen if c.startswith(cat))
        if cat_count >= 3:
            continue
        categories_seen.add(f"{cat}_{cat_count}")

        case_dir = os.path.join(base_cases_dir, case_id)
        os.makedirs(case_dir, exist_ok=True)

        # 1. main.tf
        main_tf = f"""# Benchmark Case: {case['id']} - {case['title']}
# Difficulty: {case['difficulty']} | Category: {case['benchmark_category']}

terraform {{
  required_version = ">= {case['terraform_version']}"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 6.56.0"
    }}
  }}
}}

locals {{
  environment = "benchmark"
  case_id     = "{case['id']}"
}}

resource "aws_{cat.lower()}_resource" "target" {{
  name = "target-${{local.case_id}}"
  tags = {{
    Environment = local.environment
    ManagedBy   = "IaCSecBench"
  }}
}}
"""
        with open(os.path.join(case_dir, "main.tf"), "w", encoding="utf-8") as f:
            f.write(main_tf)

        # 2. variables.tf
        var_tf = """variable "environment" {
  type        = string
  default     = "benchmark"
  description = "Target deployment environment."
}
"""
        with open(os.path.join(case_dir, "variables.tf"), "w", encoding="utf-8") as f:
            f.write(var_tf)

        # 3. expected.json
        expected_data = {
            "benchmark_id": case["id"],
            "expected_result": case["expected_result"],
            "severity": case["severity"],
            "violations": case["expected_violations"]
        }
        with open(os.path.join(case_dir, "expected.json"), "w", encoding="utf-8") as f:
            json.dump(expected_data, f, indent=2)

        # 4. metadata.json
        with open(os.path.join(case_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(case, f, indent=2)

    print(f"✓ Created representative self-contained case folders in {base_cases_dir}/")

if __name__ == "__main__":
    create_case_folders()
