# IaCSecBench — Pre-Submission Review

Reviewed 2026-08-04 against `paper/iacsecbench.tex` (working tree), `paper/refs.bib`,
`results/tables/*.tex`, `results/run_manifest.json`, `evaluation/stats.py`,
`evaluation/analyze.py`, and the three figures in `paper/figures/`.

Statistical claims were recomputed independently rather than taken from the text.
Citation metadata was checked against OpenAlex records retrieved 2026-08-04.

---

## Resolution status (updated 2026-08-04, after remediation)

**Applied: 22 of 23 findings.** The manuscript builds clean under `tectonic`
(13 pages, zero overfull boxes, zero errors, **no raster content anywhere**), and
`make dist` produces a bundle that compiles standalone.

One finding cannot be closed by editing: **independent human relabelling (#8)**
requires a second person and remains the paper's largest outstanding threat.

| # | Finding | Status |
|---|---|---|
| 1 | Figures contradict the manuscript | **Fixed and rendered.** Sources generated from recorded results by `experiments/generate_figures.py`; both rendered as single-page vector PDFs. Stale PNGs quarantined to `figures/superseded/`. |
| 2 | 24 dash-broken sentences | Fixed, all 24, by restructuring rather than restoring dashes. Verified 0 remain. |
| 3 | `\input` breaks submission bundle | Fixed. `make dist` + `flatten_for_submission.py`; verified to build standalone. |
| 4 | Wrong citation DOIs | Fixed. **Three**, not two: `verdet2024exploring` resolved to a smart-contract taxonomy and `opdebeeck2021smelly` to an off-by-one-mistakes study. |
| 5 | Uncited direct prior work | Fixed. Roe, Gokhale, Kapetanidou cited and differentiated; Böhme and Li et al. added and load-bearing. 31 → 46 references. |
| 6 | Corpus framing | Fixed. "Benchmark" dropped from title; reframed as methodology + harness. |
| 7 | Agresti–Coull misuse | Fixed. Now cited for the argument it makes, with a coverage-based justification for Clopper–Pearson. |
| 8 | Independent human relabelling | **Not done — requires a second human.** Still the paper's largest outstanding threat. |
| 9 | Full pairwise matrix | Fixed. New Table V, all 10 pairs, Holm–Bonferroni across the full family. |
| 10 | Two of three layers scored | Fixed, in abstract, architecture section, and contributions. |
| 11 | Terrascan justified twice | Fixed. Single honest justification: no successful execution was recorded. |
| 12 | Threat Model established nothing | Fixed. Compressed to two paragraphs, retitled, scope claim narrowed. |
| 13 | Reference-loses result buried | Fixed. Now in abstract, contributions, and conclusion. |
| 14 | Abstract lacked findings | Fixed. States the 24× criterion swing and the non-significance result. |
| 15 | `c` alignment in Tables III, V | Fixed, plus four overfull-box regressions the change exposed. |
| 16 | `artifact_structure` illegible | Fixed. Replaced with a `verbatim` directory tree built from the real repository. |
| 17 | Figure alpha / dpi | **Fixed.** Both figures are vector PDFs: no alpha channel, no dpi, no raster. The final PDF contains zero embedded images. |
| 18 | Precision CI conditional | Fixed. New paragraph in §RQ1. |
| 19 | "invalid" → "unreliable" | Fixed. |
| 20 | Stylistic repetition | Fixed. Three "we report X because Y" instances rewritten; caveat trimmed. |
| 21 | Missing actionability citations | Fixed. Vassallo, Tahaei, Ge cited where Layer 1 over-detection is claimed. |
| 22 | Verify `verdet` DOI | Fixed — it was wrong; see #4. |
| 23 | Two sentence fragments | Fixed. |

**One item remains, and it cannot be closed by editing: independent human
relabelling (#8).** At 48 cases this is a few hours of one person's time, and it
converts the paper's most serious threat from "outstanding" to "addressed". The
manuscript already names it as "the correct mitigation and remains outstanding",
which a reviewer will read as an invitation to ask why it was not simply done.

**One optional consistency choice.** The rendered figures are set in Times; the body
text is Latin Modern, which is what `IEEEtran` gives by default under `tectonic`.
Both are serif and the difference is subtle at figure scale. Adding
`\usepackage{newtxtext,newtxmath}` would make the body Times and match the figures
exactly, which is also closer to how IEEE Transactions appear in print. It is a
visible change to the document's appearance, so it is left as the author's call.

Note on re-measurement: the baselines were re-run during remediation. Every
detection figure reproduced **byte-identically**; latency shifted 20–35% (Checkov
2371 → 1853 ms), which is host variance and is why no latency value appears in prose.

---

## Headline verdict

**Not ready to submit to IEEE Transactions on Software Engineering.** Two defects
would stop it at desk-check regardless of scientific merit (§4.1, §4.2), and one
structural limitation puts it below TSE's empirical bar even after repair (§1.1).

The paper's *methodology and intellectual honesty are genuinely strong* — stronger
than most published work in this area. The problem is the evidence base is too thin
to carry a TSE claim, and the artefacts around the prose have decayed out of sync
with it.

| | |
|---|---|
| **TSE outcome, submitted as-is** | Reject (likely desk-reject or Reject-and-Resubmit) |
| **TSE acceptance probability, as-is** | **5–10%** |
| **TSE acceptance probability, after all Required + Major changes** | 35–45% |
| **Best-fit venue today** | EASE, MSR, or ICSE-SEIP (methodology + artifact track) |
| **Acceptance probability at EASE/MSR after Required changes** | 55–65% |
| **Reviewer scores (TSE 5-point, 5 = best)** | Novelty 2.5 · Rigour 4.0 · Evidence 2.0 · Presentation 2.0 · Reproducibility 4.5 |

The single highest-leverage action is not scientific: it is repairing the 24 broken
sentences in §5.1. The paper currently reads as careless, and that impression will
colour a reviewer's judgement of the science, which does not deserve it.

---

## 1. Academic review

### 1.1 The corpus is the existential problem

`Table~\ref{tab:admissibility}` reports **520 catalogue entries declared, 48
configurations present on disk, 48 admissible** (26 vulnerable, 22 compliant).

A reviewer will read "520 declared / 48 present" as a 91% shortfall and ask why the
artefact is described as a benchmark. The paper's own framing invites the question by
reporting the declared count at all. Three consequences follow, and the paper
concedes all three:

1. **No pairwise difference is significant after correction** (§RQ1). With 26
   violating cases the discordant cells are 2–5 wide. The exact test is behaving
   correctly; there is simply nothing to resolve. RQ1's honest answer is "this corpus
   cannot rank these tools."
2. **False-positive behaviour is barely characterised.** 22 compliant baselines yield
   precision intervals like `[73.00, 98.97]` — a 26-point span. Specificity and MCC
   are marked not-estimable for some configurations.
3. **RQ5 is unanswered.** Four external configurations, which were additionally
   found to have been *duplicated in a single directory* (§RQ5). The paper reports
   this defect with unusual candour, but four cases cannot support a generalisation
   claim and the paper says so.

**This is the difference between a methodology paper and a benchmark paper.** The
title claims "A Reproducible Benchmark and Finding-Normalization Methodology." The
methodology is delivered; the benchmark is not, at 48 cases. Reviewer 2 will write
exactly that sentence.

> **Required:** either enlarge the admissible corpus to the low hundreds, or retitle
> and reframe the contribution as a *methodology and reference harness*, dropping
> "Benchmark" from the title and the benchmark framing from the abstract. The second
> option is achievable in a week and is honest; the first is the path to TSE.

### 1.2 Single-investigator construct validity

The same person authored the corpus specifications and the reference policy set. §7.1
states this as "the most serious limitation" and does not oversell the mitigations.
That candour is to the paper's credit, but a reviewer still has to judge whether the
mitigation is sufficient, and it is not:

- The blind second-labelling pass used an **automated rater**. The paper is explicit
  that this is "not human inter-rater reliability" and that both raters read the same
  public documentation, so agreement is "biased upward." A reviewer may reasonably
  hold that an automated rater sharing provenance with the specifications is not a
  second rater at all, and that reporting κ = 0.958 alongside that caveat invites the
  number to be quoted without it.
- Five of 48 cases were previously inspected and are not blind. The paper reports the
  excluded-subset figure (42/43), which is the right thing to do.

The κ arithmetic is correct — I verified (0.9792 − 0.5017)/(1 − 0.5017) = 0.9583 — but
correctness is not the issue; *what it measures* is.

> **Required:** one independent human relabelling pass on all 48 cases by someone who
> has not read the policy set. At N = 48 this is a few hours of work and it converts
> the paper's most serious threat from "outstanding" to "addressed." The paper already
> names this as "the correct mitigation and remains outstanding" — a reviewer will ask
> why it was not simply done.

### 1.3 The reference implementation loses, and the paper says so

Checkov achieves 88.46% control-level recall against the plan-level layer's 76.92%
and the layer union's 80.77%. The abstract states plainly: "The reference pipeline
does not lead the comparison, and we report that outcome as measured."

**This is the paper's strongest moment and should be foregrounded, not buried.** Most
tool papers in this space are authored by the tool's developer and unsurprisingly win.
A benchmark paper whose own pipeline places third, reported without hedging, is
exactly the credibility signal the field lacks. Currently it appears in one abstract
sentence and is not mentioned in the conclusion.

> **Major:** promote this to a contribution bullet and a sentence in the conclusion.
> It is evidence that the methodology resists author bias, which is the paper's
> central claim.

### 1.4 Layer 2 has no evaluation

The framework is described throughout as three layers. Layer 2 (native module
testing) is:

- excluded from `tab:layers` ("not scored")
- excluded from `tab:performance`
- reported under RQ3 only as a **suite-size count** (11 files, 190/153/137 lines,
  11 `run`, 26 `assert`)
- and RQ3's comparative claim was **withdrawn** ("no independently authored external-
  framework suite exists")

So one third of the contributed architecture is supported by a line count. §RQ4 calls
its omission "a scope boundary, not a null result," which is fair, but a reviewer will
observe that the paper claims a three-layer framework and evaluates two layers.

> **Major:** either state in the abstract and contributions that the evaluation covers
> two of three layers, or drop Layer 2 to a subsection of the architecture description
> and stop counting it as an evaluated component.

### 1.5 Terrascan's exclusion is justified twice, which reads as post-hoc

§5.7 excludes Terrascan on paradigm grounds ("its analysis paradigm is Rego policy
evaluation, which the plan-level layer already represents") and then adds: "no
successful Terrascan execution was ever recorded against it."

Two independent justifications for one exclusion is a pattern reviewers read as
rationalisation — the second sentence suggests the tool was attempted and failed, and
the first was constructed afterward. **The attached figure makes this worse: it names
`Terrascan (v1.18.1)` as an evaluated engine** (§4.1).

> **Major:** pick one justification. If Terrascan could not be run, say that plainly
> as a limitation. If the paradigm argument is the real reason, delete the second
> sentence. Keeping both is the weakest option.

### 1.6 Comparison design: single reference, four comparisons

All McNemar tests are against OPA (plan-level) — the authors' own layer. Holm–Bonferroni
corrects across the family of four. This is defensible but means **no third-party
scanner is compared against another**. Checkov vs tfsec is the comparison a
practitioner wants, and it is absent.

> **Minor:** report the full pairwise matrix (10 comparisons for 5 tools), correcting
> across all of them. `evaluation/stats.py` already supports this; it is a change to
> `analyze.py`'s comparison loop, not to the statistics.

---

## 2. Technical accuracy review

**The statistics are correct.** I recomputed every reported quantity in
`tab:performance`, `tab:mcnemar`, and `tab:layers` independently:

| Claim | Reported | Recomputed | ✓ |
|---|---|---|---|
| Clopper–Pearson lower, precision 23/23 | 85.18 | $0.025^{1/23} = 0.85177$ | ✓ |
| Clopper–Pearson lower, precision 20/20 | 83.16 | $0.025^{1/20} = 0.83156$ | ✓ |
| McNemar exact $p$, $b{=}2, c{=}5$ | 0.453 | $2\sum_{i\le2}\binom{7}{i}/2^7 = 58/128$ | ✓ |
| McNemar exact $p$, $b{=}21, c{=}1$ | <0.001 | $46/2^{22} = 1.10\times10^{-5}$ | ✓ |
| Haldane–Anscombe OR, $b{=}21, c{=}1$ | 14.33 | $21.5/1.5 = 14.333$ | ✓ |
| Haldane–Anscombe OR, $b{=}2, c{=}5$ | 0.45 | $2.5/5.5 = 0.4545$ | ✓ |
| Cohen's $g$, $b{=}21, c{=}1$ | 0.455 | $|21/22 - 0.5| = 0.4545$ | ✓ |
| MCC, Checkov | 0.882 | $506/\sqrt{23\cdot26\cdot22\cdot25} = 0.8823$ | ✓ |
| Cohen's $\kappa$, labelling pass | 0.958 | $(0.9792-0.5017)/0.4983 = 0.9583$ | ✓ |
| Layer union recall | 80.77 | $21/26$, overlap 0, $1+20=21$ | ✓ |

`evaluation/stats.py` is better than the paper needs. Notable strengths:

- Clopper–Pearson via a hand-implemented regularised incomplete beta with
  bisection inverse — no SciPy dependency, and the test suite pins values to
  independently derived constants.
- `_binom_sf_le` uses `Fraction` and `math.comb`, so the exact binomial tail is
  computed in **exact rational arithmetic** and then converted. No floating-point
  accumulation error in the p-value.
- `chi2_valid = k >= 5` flags the Yates-corrected statistic as untrustworthy at small
  discordant counts, and it is retained but not reported as primary. The docstring
  explicitly notes the $c=0$ case "is routinely quoted in the IaC-scanner literature
  but is not trustworthy" — a pointed and correct observation.
- `mid-p` variant computed and stored but not headlined.

### 2.1 The Agresti–Coull tension (genuine, and a reviewer will spot it)

The paper cites `agresti1998approximate` — Agresti & Coull, *"Approximate Is Better
than 'Exact' for Interval Estimation of Binomial Proportions"* — **in support of using
Clopper–Pearson**. That paper's thesis is the opposite: that the "exact" interval is
needlessly conservative and the Wilson/adjusted-Wald interval has better actual
coverage.

Citing it as authority for CP, without engaging its argument, is the kind of thing a
statistically literate reviewer flags with relish. `stats.py` already implements
`wilson()`.

> **Required:** add one or two sentences justifying CP on the grounds that actually
> apply — guaranteed nominal coverage, and the fact that at $n = 26$ with proportions
> near 1 the conservatism is the safe direction for a claim about detection. Better
> still, report Wilson intervals alongside CP in a supplementary table and note they
> are narrower. Do not cite Agresti & Coull as if it endorsed the choice.

### 2.2 Precision intervals are conditional, and this is not stated

Recall's denominator (26 vulnerable cases) is fixed by design, so a binomial interval
is appropriate. **Precision's denominator is TP + FP, which is a random quantity** —
it depends on how many findings the tool emitted. Applying Clopper–Pearson to
precision treats a random denominator as fixed, which makes the interval conditional
on the observed number of positive predictions rather than marginal.

This is standard practice and not wrong, but it is a known subtlety and the paper is
otherwise scrupulous about exactly this class of caveat.

> **Minor:** one sentence in §6.1 noting precision intervals are conditional on the
> realised prediction count.

### 2.3 No overclaiming found

I looked specifically for the pattern the request flags ("100% detection"). The paper
handles it correctly. Checkov's precision is 100.00%, and §6.1 pre-empts the reading:

> "a perfect point estimate in particular carries a lower confidence bound
> substantially below unity, and reporting the point estimate alone would misstate
> what has been established"

Similarly, `NOT_ESTIMABLE` markers appear instead of zeros, `analyze.py` refuses to
emit tables for an empty corpus, and IaCSecBench L1's MCC of **−0.017** (worse than
chance) is reported without softening. The negative MCC in particular is the sort of
number most authors would quietly omit.

**On overclaiming the paper is exemplary.** If anything it under-claims: the
methodology contribution is real and is described more tentatively than it needs to be.

### 2.4 One statistical description to tighten

§6.1 says the chi-square approximation "is invalid when a discordant cell is small."
"Invalid" is too strong — it is *unreliable*; the approximation degrades rather than
becoming undefined. `stats.py`'s own docstring gets this right ("not trustworthy").

> **Minor:** align the prose with the code's wording.

---

## 3. Literature review

### 3.1 Two citations have wrong DOIs that resolve to the wrong papers

Checked against OpenAlex, 2026-08-04:

| Bib key | Paper as titled in `refs.bib` | Stated | Actual |
|---|---|---|---|
| `opdebeeck2022control` | "Control and Data Flow in Security Smell Detection for IaC: Is It Worth the Effort?" | MSR **2022**, DOI `10.1145/3524842.3527964` | MSR **2023**, DOI `10.1109/MSR59073.2023.00079` |
| `opdebeeck2021smelly` | "Smelly Variables in Ansible Infrastructure Code" | MSR **2021**, DOI `10.1109/MSR52588.2021.00019` | MSR **2022**, DOI `10.1145/3524842.3527964` |

The DOI currently attached to `opdebeeck2022control` **is** the smelly-variables
paper's DOI. The two entries have their identifiers crossed, and both years are wrong.
Since `opdebeeck2022control` is load-bearing — it is the citation justifying the
plan-level layer's entire rationale in §2.2 and §7 — a reviewer following the DOI
lands on a different paper.

> **Required:** correct both entries. This is the kind of error that makes a reviewer
> spot-check every other reference.

### 3.2 Verify one more, and prefer the peer-reviewed version

`verdet2024exploring` is given as *Empirical Software Engineering* 2024, DOI
`10.1007/s10664-024-10446-8`. OpenAlex records "Exploring Security Practices in
Infrastructure as Code: An Empirical Study" as arXiv 2023 (`10.48550/arxiv.2308.03952`),
and separately a 2025 EMSE paper by the same group, "Assessing the adoption of security
policies by developers in Terraform across different cloud providers"
(`10.1007/s10664-024-10610-0`). The DOI given is plausible but I could not confirm it.

> **Required:** verify the DOI resolves. **Recommended:** also cite the 2025 EMSE
> Terraform-specific paper — it is directly on point for §5.1's sampling-validity
> discussion (security-policy adoption differs by cloud provider, which bears on your
> single-provider limitation in §7.3).

### 3.3 Uncited direct prior work — the most serious literature gap

Three 2025–2026 papers benchmark IaC security scanners. None is cited. The first is
close enough that a reviewer who knows it will question the novelty claim outright:

| Work | Why it matters |
|---|---|
| **Roe, Gogate & Dashtipour (2026), "Multicloud Security Assessment: A Benchmark Study of Infrastructure as Code Scanners,"** DOI `10.62762/tisc.2026.777114` | **Closest existing work.** A benchmark study of IaC scanners across multicloud. Must be cited and differentiated. |
| **Gokhale, Jayaprakash & Singaravelu (2026), "Comparative Analysis of IaC Misconfiguration Detection Through Policy Driven Evaluation and Taint-Aware Static Reasoning,"** DOI `10.1007/978-3-032-27160-0_37` | Compares policy-driven against taint-aware detection for IaC — your §2.2 axis exactly. |
| **Kapetanidou, Nizamis & Votis (2025), "An evaluation of commonly used Kubernetes security scanning tools,"** DOI `10.1145/3721889.3721924` | Adjacent scanner-evaluation methodology; also **Krieger et al. (2026)**, "A Comparison of Kubernetes Compliance Standards and Configuration Scanners." |

All are recent and lightly cited, so it is *plausible* no reviewer raises them — but
that is a gamble, and the differentiation is easy to write: none of them contributes a
finding-normalization methodology, and on the evidence of their metadata none releases
a reusable labelled corpus. Your §1 claim to be addressing "the evaluation problem"
becomes stronger, not weaker, by naming them and saying what they left undone.

### 3.4 Missing methodological anchors

31 references is low for TSE (typical range 50–80). More importantly, the specific
papers that would *strengthen the methodology argument* are absent:

**Benchmark-methodology transfer — the strongest available support for your design:**

- **Li, Chen, Fan et al. (2023), "Comparison and Evaluation on SAST Tools for Java,"**
  ESEC/FSE, `10.1145/3611643.3616262`. Reports per-category precision/recall and
  explicitly separates *rule coverage* from *rule correctness*. This is the template
  your normalization methodology instantiates for IaC. Citing it locates your
  contribution in an established tradition rather than leaving it to look ad hoc.
- **Esposito, Falaschi & Falessi (2024), "An Extensive Comparison of SAST Tools,"**
  EASE, `10.1145/3661167.3661199`. Shows aggregate rankings invert under different
  error weightings — direct support for your §RQ2 argument.
- **Böhme, Szekeres & Metzman (2022), "On the reliability of coverage-based fuzzer
  benchmarking,"** ICSE, `10.1145/3510003.3510230`. **The** citation on why benchmark
  results fail to replicate. Your interval-width argument in §6.1 and your conclusion's
  claim that "benchmark size is a weaker indicator of evidential strength than
  admissibility and interval width" is *precisely* Böhme's thesis. Not citing it leaves
  your best methodological point unsupported.
- **Noirot Ferrand et al. (2026), "Longitudinal Analyses of SAST Tools: A CodeQL Case
  Study."** Tool performance is version-dependent — supports your version-manifest
  discipline in §5.6.

**IaC-specific, where your taxonomy needs positioning:**

- **War, Nikiema, Samhi et al. (2025), "Security smells in infrastructure as code: a
  taxonomy update beyond the seven sins,"** `10.48550/arxiv.2509.18761`. The
  seven-sins taxonomy you build on has been revised. Your canonical control set should
  acknowledge that the ground-truth vocabulary is unstable — which *helps* your
  admissibility argument.
- **Saavedra et al. (2023), "Polyglot Code Smell Detection for IaC with GLITCH,"** ASE,
  `10.1109/ase56229.2023.00162`. You cite only the 2022 ASE paper; the 2023 extension
  broadens coverage and is the version to compare against.
- **Qiu, Kon, Beckett et al. (2024), "Unearthing Semantic Checks for Cloud IaC
  Programs,"** SOSP, `10.1145/3694715.3695974`. Semantic rather than syntactic checking
  of IaC — directly relevant to your plan-level layer's rationale.
- **Minna, Blaise, Tuma et al. (2025), "Automated Analysis of Security Policy Violations
  in Helm Charts,"** IEEE TDSC, `10.1109/tdsc.2025.3628213`.
- **Foalem, Da Silva, Khomh et al. (2026), "An empirical study of Policy-as-Code adoption
  in open-source software projects,"** JSS, `10.1016/j.jss.2026.113028`. For §2.3.

**False positives and actionability — you assert Layer 1 over-detects but cite nobody:**

- **Vassallo et al. (2019), "How developers engage with static analysis tools in
  different contexts,"** EMSE, `10.1007/s10664-019-09750-5`.
- **Tahaei, Vaniea, Beznosov et al. (2021), "Security Notifications in Static Analysis
  Tools,"** CHI, `10.1145/3411764.3445616`.
- **Ge, Fang, Li et al. (2023), "Machine Learning for Actionable Warning
  Identification: A Comprehensive Survey."**

> **Required:** Böhme 2022 and Li 2023 at minimum. They support claims you are already
> making and currently making unaided.
> **Required:** cite and differentiate Roe et al. 2026.

### 3.5 Genuineness

All 31 existing references are real papers with correct titles and venues. Nothing
appears fabricated. Beyond the two Opdebeeck DOI errors, spot-checks of
`clopper1934use` (`10.1093/biomet/26.4.404`), `mcnemar1947note` (`10.1007/BF02295996`),
`matthews1975comparison` (`10.1016/0005-2795(75)90109-9`), `habib2018howmany`
(`10.1145/3238147.3238213`), `arcuri2014hitchhiker` (`10.1002/stvr.1486`), and
`dietterich1998approximate` (`10.1162/089976698300017197`) all resolve correctly.

---

## 4. IEEE formatting review

### 4.1 REQUIRED — the three figures contradict the manuscript

This is the most damaging single defect in the submission. Every figure encodes data
from an earlier draft:

| Figure asserts | Manuscript reports |
|---|---|
| "Benchmark Catalog (**N = 345**)"; "345 Labelled Scenarios"; "**176 Vulnerable / 169 Secure**" | **N = 48**; 26 vulnerable, 22 compliant (`tab:admissibility`) |
| "scenarios/ (**345** Self-Contained HCL Cases)" | 48 configurations present on disk |
| Evaluated engines: **Terrascan (v1.18.1)**, OPA (v0.62.0), tfsec (v1.28.1), Checkov (v3.2.0) | Checkov, tfsec, **Trivy**, OPA, IaCSecBench L1. **Terrascan explicitly excluded**, "no successful Terrascan execution was ever recorded" (§5.7) |
| Layer latencies "Avg: 0.4s / 21.8s / 5.9s", "Total Pipeline Overhead: ~28.1s" | L1 = **0.2 ms**, OPA = **18.1 ms** (`tab:latency`) |
| Tool versions as above | `run_manifest.json`: Checkov **3.3.8**, tfsec **v1.28.14**, Trivy **0.73.0**, OPA **1.19.0** |

Every version number in the figures is wrong; the corpus size is off by 7×; one figure
advertises a tool the paper spends a paragraph excluding; and Trivy — one of the three
evaluated scanners — appears in no figure.

A reviewer who compares Fig. 2 against Table II concludes the authors are not in
control of their own artefacts, and will then distrust the tables. §5.6's argument that
"a hand-copied version string is the first thing to drift" is undercut by figures that
hard-code four drifted version strings.

> **Required:** regenerate all three figures from current data before submission. The
> latency and corpus figures should ideally be generated by `analyze.py` alongside the
> tables, for the same reason the tables are generated.

### 4.2 REQUIRED — `\input` reaches outside the manuscript directory

`\resulttable` expands to `\input{../results/tables/#1.tex}`. IEEE submission systems
and arXiv require a self-contained, typically flat source bundle; `../results/` will
not exist in the upload and the build will fail with six missing-file errors.

> **Required:** add a `make dist` target that copies `results/tables/*.tex` and
> `paper/figures/*` into a staging directory, rewrites `\resulttable` to a local path,
> and produces the submission tarball. Keep the current layout for local work.

### 4.3 Minor formatting items

- **`\markboth` carries placeholders** — "Vol.~XX, No.~X, 2026". Expected pre-
  acceptance, but check the target journal's template; some want it removed.
- **`siunitx` is deliberately absent** and numeric columns rely on fixed decimal places
  plus `r` alignment. This is sound and documented in the preamble comment. Tables IV,
  VI, VII were corrected on 2026-08-04; **Tables III (`performance`) and V
  (`strictness`) still use `c` for numeric columns** and will show ragged decimal
  points. Same one-word fix per emitter.
- **`tab:performance` is a `table*`** with 10 columns — correct choice.
- **Cross-references now resolve**: `fig:pipeline`, `fig:normalization`, `fig:artifact`
  each have exactly one `\ref` (added 2026-08-04; before that all three floats were
  unreferenced, which IEEE flags).
- **`artifact_structure.png` is a 10:1 strip.** Even spanning both columns it renders
  0.69in tall with ~3pt labels — below IEEE's legibility threshold. See
  `figures/README.md`. Recommend redrawing vertically or replacing with a `verbatim`
  directory tree, which is the conventional treatment for a package layout anyway.
- **All three figures are RGBA.** pdfTeX handles alpha, but IEEE PDF eXpress sometimes
  flags transparency. Flatten onto opaque white.
- **`pipeline_architecture.png` renders at 231 dpi** at column width — under IEEE's
  300 dpi preference (600 for line art).
- **Length**: ~6,600 words of body text ≈ 7.8 two-column pages, plus 7 tables and 3
  figures → roughly 12–14 pages. Within TSE's regular-paper allowance; check the
  overlength page charge threshold.
- **AI-use disclosure** is present in the Acknowledgment and correctly scoped to
  copy-editing. Good — and increasingly expected. Verify the target journal's required
  wording and placement, which some now specify exactly.

---

## 5. Language polishing

### 5.1 REQUIRED — 24 sentences were broken by em-dash deletion

Comparing the working tree against `HEAD`: **all 24 em-dashes in the prose were
deleted, and in every case the surrounding sentence was left unrestructured.** The
result is 24 ungrammatical or unparseable sentences, including the abstract's central
methodological sentence.

The intent (avoiding em-dashes) is legitimate. The execution removed the delimiters
without replacing them, so parentheticals now run into their host clauses. This is
worse than the original in every instance. **The fix is to restructure with commas,
parentheses, or a sentence break — not to restore the dashes.**

Representative repairs:

| # | Broken (current) | Repair |
|---|---|---|
| 1 | "we evaluate three third-party scanners spanning two independent rule sets, since one is the maintained successor of another and inherits its rules against the pipeline's own layers and their union" | "we evaluate three third-party scanners, spanning two independent rule sets (one is the maintained successor of another and inherits its rules), against the pipeline's own layers and their union" |
| 2 | "The property that makes IaC attractive deterministic, repeatable application of a declared state also amplifies its failure modes" | "The property that makes IaC attractive, namely deterministic and repeatable application of a declared state, also amplifies its failure modes" |
| 3 | "would credit the corpus with four controls API-gateway authorization and three Kubernetes workload controls against which nothing was ever run" | "would credit the corpus with four controls (API-gateway authorization, and three Kubernetes workload controls) against which nothing was ever run" |
| 4 | "why the resulting invariant every plan-level identifier must exist in the policy source is now enforced by a test" | "why the resulting invariant, that every plan-level identifier must exist in the policy source, is now enforced by a test" |
| 5 | "a wrong identifier is inert nothing emits it, so it never matches and the only possible effect" | "a wrong identifier is inert (nothing emits it, so it never matches), and the only possible effect" |
| 6 | "with every comment line removed the generator writes the expected label and its rationale into each file header along with the annotation files and the case identifier" | "with every comment line removed, since the generator writes the expected label and its rationale into each file header, along with the annotation files and the case identifier" |
| 7 | "The generator's rationale reveals the intent encryption *other than* a customer-managed key so the label encoded a requirement" | "The generator's rationale reveals the intent, namely encryption *other than* a customer-managed key, so the label encoded a requirement" |
| 8 | "the set must span distinct analysis paradigms syntax-tree analysis, lexical scanning, and policy evaluation" | "the set must span distinct analysis paradigms: syntax-tree analysis, lexical scanning, and policy evaluation" |
| 9 | "different spellings tfsec reports `AVD-AWS-0086`, Trivy reports `AWS-0086` and we exploit exactly that correspondence" | "different spellings (tfsec reports `AVD-AWS-0086`, Trivy reports `AWS-0086`), and we exploit exactly that correspondence" |
| 10 | "Trivy emits its counterpart `AWS-0057` on neither not on these two cases, and nowhere in the corpus" | "Trivy emits its counterpart `AWS-0057` on neither: not on these two cases, and nowhere in the corpus" |
| 11 | "beyond the Terraform binary already needed to plan the configuration a qualitative difference in toolchain surface, not a quantitative claim" | "beyond the Terraform binary already needed to plan the configuration. This is a qualitative difference in toolchain surface, not a quantitative claim" |
| 12 | "the specifications were written from so the two raters share provenance and agreement is biased upward" | "the specifications were written from, so the two raters share provenance and agreement is biased upward" |
| 13 | "genuinely indeterminate at plan time the attribute is set, but nothing in the plan establishes what to and is reported as neither compliant nor violating" | "genuinely indeterminate at plan time (the attribute is set, but nothing in the plan establishes what to), and is reported as neither compliant nor violating" |
| 14 | "No claim is made about organisational factors policy ownership, escalation workflow, or developer friction because this study measures tool output" | "No claim is made about organisational factors such as policy ownership, escalation workflow, or developer friction, because this study measures tool output" |
| 15 | "This is the expected consequence of the corpus size not evidence of equivalence" | "This is the expected consequence of the corpus size, not evidence of equivalence" |
| 16 | "an unbounded ratio is a degenerate cell, not a large effect" | (reads acceptably; verify against `HEAD` for the intended emphasis) |

Item 13 is the worst of them: "nothing in the plan establishes what to" is a sentence
fragment even after repair, because the original relied on the dash to carry an
ellipsis ("what to [set it to]"). Rewrite as: "the attribute is set, but the plan does
not record the value it is set to."

Two further sentence fragments, independent of the dash issue:

- §7.1: "A control whose stated text was weaker than the requirement its label
  encoded, where the stricter reading matched the reference policy set." — no main
  verb. Attach to the previous sentence with a colon.
- §5.3 (`sec:coverage`): "Two controls lost their only rule to that correction and
  became detectable by no tool." — grammatical, but "lost their only rule to that
  correction" is ambiguous about agency.

### 5.2 Style observations

The prose is dense but of high quality — precise, unhedged, and free of the
throat-clearing that fills most tool papers. Do not flatten it in revision. Three
patterns to adjust:

- **Sentence length.** Several sentences run past 55 words while carrying two
  independent claims. §5.3's paragraph on the taxonomy audit is the clearest case.
- **"We report X because Y" is used ~11 times.** The construction is good once or
  twice; at eleven it becomes a tic and starts to read defensively, as if anticipating
  attack. Convert most to direct statements.
- **Repetition of the construct-validity caveat.** The single-investigator threat is
  stated in the abstract, §1, §5.4, §7.1, and §7.3. Three of the five are enough:
  keep §1 (brief), §5.4 (mechanism), §7.1 (full treatment).

---

## 6. Originality assessment

### 6.1 Does it read as AI-generated?

**Mostly no, and less so than most current submissions.** The passages that carry
specific, verifiable engineering detail could not plausibly be generated without
having done the work:

- the three-way Terraform plan serialisation distinction (literal / not-yet-known /
  null) and how a presence test *inverts* rather than weakens a control (§7.2)
- the shared-directory defect where four external cases returned byte-identical
  findings scored against four different controls (§6.5)
- the tfsec `AVD-AWS-0086` → Trivy `AWS-0086` identifier crosswalk, and that 12 of 13
  unmapped tfsec identifiers have exact Trivy counterparts (§6.1.1)
- the SSE-S3 / CIS 2.1.1 labelling disagreement and the decision to correct the
  control text rather than the label (§5.4)

These are the paper's strongest passages precisely because they are unfakeable.

### 6.2 Passages that do read as machine-assembled

Three patterns to revise:

1. **The Threat Model section (§4) is boilerplate.** A STRIDE table mapping six
   categories to generic mitigations, followed by "The threat model is stated to
   delimit scope; the pipeline was not subjected to adversarial testing, and no claim
   of resistance to the modelled adversaries is made." The section therefore
   establishes nothing and admits as much. It reads as a section included because
   security papers have one. **Recommend cutting it to a short paragraph inside the
   architecture section**, or removing it entirely — it costs a page and a reviewer
   will ask what it does.
2. **Parallel triads.** "First, *normalization before comparison*. Second,
   *admissibility is mechanically enforced*. Third, *measurement is separated from
   assumption*." Three italicised maxims in three sentences of identical shape. The
   content is fine; the symmetry is machine-flavoured. Vary the construction.
3. **Aphoristic closers.** Several paragraphs end on an epigram: "Case isolation has
   to be enforced, never assumed." / "Where the two options differ, we take the one
   that cannot flatter the reference." / "a manifest entry without a configuration is a
   citation, not a case." Individually good — the second is excellent — but there are
   roughly eight and the rhythm becomes recognisable. Keep the best three.

### 6.3 What would make it read more like a published IEEE paper

Published TSE papers front-load the result. This paper front-loads *method* and
distributes results across five RQ subsections, so the reader reaches §6 without
knowing what was found. Add two or three sentences of concrete findings to the
abstract — Checkov 88.46% [69.85, 97.55], no significant pairwise differences after
correction, and the matching criterion moving L1's recall from 3.85% to 92.31%. That
last figure is the paper's most striking number and appears only in a table.

---

## 7. Research quality assessment

### 7.1 Novelty: real but narrow

**What is genuinely novel:**

- **The three-level matching criterion** (control / resource / any), applied uniformly
  and reported for every tool. Habib & Pradel showed match definitions dominate
  results; this operationalises that for IaC and quantifies it. The L1 spread —
  **3.85% at control level, 92.31% at any level** — is a 24× swing from criterion
  choice alone, and is the most compelling evidence in the paper.
- **Mechanically enforced admissibility**, with the admissible count reported instead
  of the catalogue count. Directly attacks the field's habit of headline corpus sizes.
- **The unmapped-findings discipline**: counting and reporting rule identifiers the
  taxonomy does not cover, on the argument that discarding them biases toward whichever
  tool the taxonomy was authored around. 321 unmapped findings are reported, with 9
  identified as landing on cases the emitting tool missed. I have not seen this
  reported elsewhere.
- **Honesty engineering as an artefact property**: a harness that refuses to emit
  results for an empty corpus, statistics that return not-estimable rather than zero,
  and retention of pre-correction results so a disclosed fix can be audited.

**What is not novel:** the pipeline architecture (composing OPA, `terraform test`, and
pre-commit scanning is standard practice), and comparing IaC scanners as such —
GLITCH did a version of it in 2022, and Roe et al. (2026), Gokhale et al. (2026), and
Kapetanidou et al. (2025) all now do it.

### 7.2 Is IaCSecBench a sufficient contribution?

**As a benchmark: no.** 48 admissible cases, 4 of them external, with no significant
pairwise differences. Compared with the SAST benchmarks it implicitly competes against
— Juliet, the OWASP Benchmark, or the corpora in Li et al. 2023 — it is two to three
orders of magnitude short.

**As a methodology and reference harness: yes, marginally,** and more so at EASE/MSR
than at TSE. The normalization scheme, matching-strictness treatment, and admissibility
procedure are transferable, correct, and released as working code. The finding that
criterion choice moves recall further than inter-tool differences do is a real
contribution to how this subfield should report results.

**The mismatch between those two answers is the paper's core problem, and the title
currently claims the weaker one first.**

### 7.3 Against existing IaC benchmarking work

| Work | Overlap | Your differentiation |
|---|---|---|
| GLITCH (2022/2023) | Detector + labelled oracle + tool comparison | You contribute no detector; you contribute the comparison *methodology*. Cite the 2023 extension too. |
| Roe et al. (2026) multicloud IaC scanner benchmark | **Direct** — benchmarks IaC scanners | You add normalization, matching strictness, and mechanical admissibility. Needs explicit differentiation in §2.2. |
| Gokhale et al. (2026) | Policy-driven vs taint-aware IaC detection | Their axis is analysis technique; yours is measurement validity. Complementary. |
| Kapetanidou (2025), Krieger (2026) | Kubernetes scanner comparison | Different platform; same methodological gap. Useful as evidence the gap is general. |
| Li et al. (2023) SAST for Java | Methodological template | You are the IaC instantiation. Say so — it strengthens rather than diminishes the claim. |

---

## 8. Final pre-submission report

### Required before submission (blocking)

1. **Regenerate the three figures.** They assert N = 345, name Terrascan, omit Trivy,
   and carry four wrong version strings. (§4.1)
2. **Repair the 24 dash-broken sentences,** including the abstract. (§5.1)
3. **Fix a submission-breaking build path**: `\input{../results/tables/...}` will not
   resolve in a flat submission bundle. Add `make dist`. (§4.2)
4. **Correct the two Opdebeeck citations** — crossed DOIs, both years wrong. (§3.1)
5. **Cite and differentiate Roe et al. (2026)**; add Böhme (2022) and Li et al.
   (2023). (§3.3, §3.4)
6. **Resolve the corpus framing**: enlarge the corpus substantially, or drop
   "Benchmark" from the title and reframe as methodology + harness. (§1.1)
7. **Stop citing Agresti & Coull as support for Clopper–Pearson;** justify CP on
   coverage grounds instead. (§2.1)

### Major revisions (strongly recommended)

8. One **independent human relabelling pass** over all 48 cases. (§1.2)
9. **Report the full pairwise comparison matrix**, not just against your own layer. (§1.6)
10. **State that two of three layers are evaluated,** in abstract and contributions. (§1.4)
11. **Pick one justification for excluding Terrascan.** (§1.5)
12. **Cut or compress the Threat Model section** — it establishes nothing by its own
    admission and costs a page. (§6.2)
13. **Foreground the reference-loses-the-comparison result** in contributions and
    conclusion. (§1.3)
14. **Add concrete findings to the abstract,** especially the 3.85% → 92.31%
    criterion swing. (§6.3)

### Minor revisions

15. Fix `c` → `r` numeric alignment in Tables III and V. (§4.3)
16. Redraw or replace `artifact_structure` (10:1, ~3pt labels). (§4.3)
17. Flatten figure alpha channels; re-export `pipeline_architecture` above 300 dpi. (§4.3)
18. Note that precision intervals are conditional on the realised prediction count. (§2.2)
19. Soften "invalid" → "unreliable" for the chi-square approximation. (§2.4)
20. Reduce "we report X because Y" (11 occurrences) and trim the construct-validity
    caveat from five statements to three. (§5.2)
21. Add the missing false-positive/actionability citations (Vassallo, Tahaei, Ge). (§3.4)
22. Verify `verdet2024exploring`'s DOI; add the 2025 EMSE Terraform paper. (§3.2)
23. Fix two sentence fragments in §7.1 and §5.3. (§5.1)

### Venue recommendation

Submitting to TSE as-is wastes a review cycle. Two viable paths:

**Path A — reframe and submit soon (recommended).** Complete Required 1–5 and 7, drop
"Benchmark" from the title, complete Major 8, 10, 11, 13, 14, and submit to **EASE**
or **MSR** as a methodology-and-artifact paper. The work is a good fit for both, and
the artefact quality is above the norm at either. Estimated acceptance 55–65%.

**Path B — build the benchmark and target TSE.** Enlarge the admissible corpus to
several hundred cases with multi-provider coverage, obtain independent human labelling,
and re-run. Then the title's claim is true and the statistics have power. Six to twelve
months. Estimated acceptance 35–45%.

**What is already strong and should not be diluted in revision:** the statistical
implementation, the disclosure discipline (the inverted-policy correction in §7.2 and
the shared-directory defect in §6.5 are model examples of reporting one's own errors),
the refusal to fabricate the withdrawn RQ3 comparison, and the fact that the reference
pipeline loses and is reported losing. Those choices are why this paper deserves a
serious venue once the corpus and the artefacts are brought up to the level of the
reasoning.
