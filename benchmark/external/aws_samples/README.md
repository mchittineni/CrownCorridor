# Unlabelled external subset — AWS Samples Terraform

25 third-party Terraform repositories published by AWS under MIT-0, each pinned to
an exact commit in `manifest.json`. Selected from the 370 repositories matching
`org:aws-samples language:HCL` by criteria recorded in the manifest, the binding
one being that `terraform init -backend=false` against the pinned provider mirror
and `terraform validate` both succeed.

## These cases are unlabelled, and that is the point

They carry **no ground-truth vulnerable/compliant label**. Nothing measured here
may enter a confusion matrix, an accuracy figure, or any table that reports
detection rates. There is no key to score against, so such a figure would be
invented rather than measured. `evaluation/tests/test_external.py` asserts that no
scored-metric field appears in the recorded output.

They earn their place by answering questions the labelled corpus structurally
cannot. Every one of its 56 cases is a single flat directory with a median of 51
lines and no module indirection at all, so it cannot say whether a scanner
resolves a value across a `module` boundary, nor how many alerts adopting one
costs on production-shaped code. This subset carries 15,226 lines across 285
files, with module calls, `dynamic` blocks and `for_each` expressions.

## Nothing is vendored

The working trees are fetched on demand into `.external-corpus/`, which is
gitignored. A pinned commit is stronger evidence than a subtree: anyone can fetch
the same bytes and verify the hash, whereas vendored third-party code becomes
indistinguishable, after the fact, from code this project wrote. MIT-0 would
permit vendoring; provenance is the reason not to.

## Reproducing

```bash
python -m experiments.fetch_external          # materialise the pinned commits
python -m experiments.fetch_external --check  # verify; exit 1 if absent or moved
python -m evaluation.external                 # measure
```

Writes `results/external_subset.json` plus `results/tables/external.tex` and
`results/tables/external_agreement.tex`. The output is byte-reproducible: scan
duration is neither timed nor recorded, because latency describes the measuring
host rather than the subset.

## Do not rename `manifest.json`

`evaluation/corpus.py:load_catalogue_gap` sums `total_cases` from every
`benchmark/external/*/metadata.json` into the `external_declared` figure the
manuscript reports. Renaming this file to `metadata.json` would fold 25 unlabelled
repositories into a count of declared *labelled* cases, silently changing a
reported number.
