# Pre-correction results — plan-level polarity defect

These are the measured results **before** the audit-log-encryption policy rule was
corrected. They are retained because the paper discloses that this one rule was
fixed after its results had been inspected, and a disclosure a reader cannot check
is not much of a disclosure.

## What the defect was

`security_framework/policies/cis_aws_benchmark.rego` tested
`not after(rc).kms_key_id` on `aws_cloudtrail`. Terraform serialises three distinct
configuration states into one plan document:

| Configuration                                    | `change.after`      | `change.after_unknown` |
| :----------------------------------------------- | :------------------ | :--------------------- |
| `kms_key_id = "arn:..."` (literal)               | holds the value     | —                      |
| `kms_key_id = aws_kms_key.trail.arn` (reference) | **key absent**      | `true`                 |
| attribute not set at all                         | **present, `null`** | —                      |

`null` is a _defined_ value in Rego, so `not after(rc).kms_key_id` **fails** on the
case that omits the attribute, and **succeeds** on the case that sets it from a
reference. The control was not weakened, it was inverted.

Confirmed directly in the raw output preserved here:

- `MON-NO-LOG-ENCRYPTION-SAFE` (compliant) → emitted `cloudtrail_log_encryption`
- `MON-NO-LOG-ENCRYPTION-VULN` (violating) → did **not** emit it

## Why it was hard to see

The two errors cancel in aggregate. The plan-level confusion matrix showed
`tp=19, fp=1, tn=21, fn=7` — one false positive and one false negative, which is
the signature of ordinary imprecision, not of an inverted rule. Only per-case
inspection distinguishes the two.

Block-typed attributes do **not** share the defect: an unconfigured block is absent
from `after` and marked unknown, while a configured one appears in `after` with its
contents, so presence tests over blocks discriminate correctly. The defect is
specific to _scalar_ optional attributes.

## What the correction does

`attribute_unset` reports only the genuinely-unset state. The reference case is
treated as **indeterminate** rather than compliant or violating: the attribute is
set, but nothing in the plan establishes what to. Reporting it either way would be
a measurement error.

## How to compare

`evaluation.json` and `run_manifest.json` here have the same schema as the current
ones in `results/`. Diff the plan-level confusion matrix and the two
`MON-NO-LOG-ENCRYPTION-*` case outcomes.

Latency in this snapshot was measured under background load and is **not**
comparable to the current run — Checkov shows `2124.8 ± 896.5` ms here versus a
standard deviation roughly twenty times smaller on an idle host. Do not cite
latency from this directory for any purpose.
