# Pre-submission review — IaCSecBench, targeting EMSE or JSS

Reviewer-style assessment of `paper/iacsecbench.tex` (1132 lines, 46 references) against
Empirical Software Engineering (Springer) and Journal of Systems and Software (Elsevier).

Prepared 2026-08-04. Every number quoted below was read from `results/tables/*.tex`,
`results/corpus_report.json`, or `evaluation/control_map.json` in this working tree, not from
the manuscript prose. Every reference claim was checked against Crossref or DataCite.

The earlier `PRE_SUBMISSION_REVIEW.md` covers the IEEE Transactions-targeted pass. This
document supersedes it for venue-specific items and adds findings that the IEEE pass missed.

---

## Verdict up front

**Recommend EMSE, not JSS**, and **restructure before submitting anywhere**.

The manuscript is honest, unusually well engineered, and its replication package is stronger
than most published IaC work. It is also currently framed around a headline claim its own
data does not support, and it contains three internal contradictions a competent reviewer
will find. Fix those and it is a credible EMSE submission. Submit as-is and the most likely
outcome is reject-with-encouragement.

| | As-is | After the Required changes in §8 |
|---|---|---|
| EMSE | Reject 45% / Major 45% / Minor 10% | Major 45% / Minor 40% / Accept 5% |
| JSS | Reject 35% / Major 50% / Minor 15% | Major 35% / Minor 50% / Accept 10% |

Probability of eventual acceptance after one or two rounds: **~35% as-is, ~60–65% after the
required changes.** JSS is the easier acceptance and the weaker line on an EB-1A exhibit;
see §1.2.

---

## 1. Academic review and venue suitability

### 1.1 Which venue

**EMSE (Springer), IF 4.33 (2024 JCR), CiteScore 8.6, Q1.** Its aims and scope include a
sentence that describes this paper almost exactly:

> "Papers on the infrastructure for supporting empirical research are also of interest."

and

> "Preference is given to studies that can be replicated or expanded upon."

IaCSecBench *is* infrastructure for supporting empirical research, released with a
replication package in which every table is a generated artefact. Two papers already in your
bibliography are EMSE papers (`verdet2025adoption`, `vassallo2019engage`), so the editors
handle this subject matter routinely.

**JSS (Elsevier), IF 3.8, listed JCR Q2** in the metrics record I checked (your note said
"Q1/High-Q2" — the 2026 record says Q2, worth verifying against your own Clarivate access
before you cite it in a petition). JSS also plainly publishes this material: two more of your
own citations are JSS papers (`dallapalma2020catalog`, `foalem2026pac`).

**Recommendation: EMSE first, JSS as the fallback.** Three reasons:

1. **Your real contribution is methodological and partly negative.** The substance is "the
   evaluation procedure changes the conclusion" plus "our own reference implementation loses."
   EMSE's remit explicitly covers methodology and replication; JSS reviewers more often
   expect a system that demonstrably outperforms something, and a paper whose reference
   pipeline places behind Checkov reads to a JSS reviewer as a weak system paper rather than
   as a strong methods paper.
2. **N=48 survives EMSE review better than JSS review**, because EMSE reviewers accept a
   small corpus when the analysis is interval-based and the limitation is the paper's own
   subject. Your statistical treatment is already at that standard.
3. **EMSE is the stronger exhibit.** Q1 + IF 4.33 vs Q2 + IF 3.8.

Do not submit to both. Both are Elsevier/Springer flagship-adjacent and the overlap in
reviewer pools for IaC security is small enough that the same person may see it twice.

### 1.2 Note on the EB-1A framing

You asked about this in an earlier turn for IEEE venues; the same logic applies. For
"scholarly articles in professional journals" the adjudicator's evidence is the journal's
standing, and Q1/IF 4.33 (EMSE) is materially better than Q2/IF 3.8 (JSS). But neither
carries the weight of the *citation record* criterion, and a single-author paper in a Q1
journal with zero citations is a weaker exhibit than most petitioners assume. The
methodological framing helps here too: methods papers accrue citations from anyone who
reuses the benchmark, which is the outcome you should be optimising for.

### 1.3 The claim your data does not support

**This is the most serious finding in this review.** The abstract, the Discussion and the
Conclusion all assert:

> "The matching criterion moves apparent recall further than the differences between tools
> do, by up to a factor of 24 on one layer" (abstract, L120–122)

> "that choice moves recall by more than the differences between tools typically reported in
> the literature" (Discussion, L876–881)

Here is what `results/tables/strictness.tex` actually contains:

| Tool | Control (%) | Any (%) | Criterion swing (pts) |
|---|---|---|---|
| Checkov | 88.46 | 96.15 | 7.69 |
| tfsec | 84.62 | 92.31 | 7.69 |
| Trivy | 80.77 | 92.31 | 11.54 |
| OPA (plan-level) | 76.92 | 84.62 | 7.70 |
| IaCSecBench L1 | 3.85 | 92.31 | **88.46** |

Between-tool spread at the control criterion, excluding L1: 88.46 − 76.92 = **11.54 points**.
Largest criterion swing among those same four: **11.54 points** (Trivy).

**They are equal.** For every tool that is actually a scanner, the matching criterion moves
recall by *no more* than the spread between tools. The claim holds only through
IaCSecBench L1, whose control-level recall is 1/26 = 3.85%, so the "factor of 24" is a ratio
whose denominator is a single true positive — and L1 is the one component your own §RQ4
(L818–821) argues is *not* comparable, because it "is insensitive to every control expressed
as a resource attribute."

So the headline result is: a ratio computed on n=1, from the component the paper elsewhere
excludes from comparison, presented in the abstract as the paper's first of "two results
[that] are the substance of the paper."

A reviewer who opens Table `tab:strictness` will find this in about ninety seconds. **Fix it
before submission.** Two honest reframings, either acceptable:

- **(a) Restate in points, keep both facts.** "Among the source-level and plan-level tools
  the criterion moves recall by 7.7 to 11.5 percentage points, which is the same magnitude as
  the entire spread between those tools (11.5 points); on the repository-edge layer, whose
  control-level recall is 3.85%, it moves recall by 88.5 points." That is defensible, still
  striking, and no longer overstated.
- **(b) Reframe the claim as being about *reproducibility* rather than *magnitude*.** The
  finding that survives without qualification is that a comparison which does not state its
  criterion is not reproducible — because a 7.7-to-11.5-point swing is enough to reorder the
  tools. Check whether it actually does reorder them: at `any`, tfsec and Trivy and L1 all
  tie at 92.31 while Checkov leads at 96.15, so the ranking *does* change between criteria.
  **That is a stronger and completely defensible headline than the 24× ratio.** I would lead
  with it.

### 1.4 Other weak or unsupported claims

**W1 — "no labelled real-world corpus exists" is false, and the paper contradicts itself.**
L864–868 states:

> "establishing that requires a labelled corpus of real-world configurations, which to our
> knowledge does not exist for this domain and which we identify as the principal obstacle to
> progress"

But §II L229–230 of the same manuscript says GLITCH "is evaluated against a labelled oracle
dataset with a tool comparison." GLITCH's replication package contains **three manually
annotated oracle datasets, 80 real-world IaC scripts, covering Terraform among five
technologies, validated by the authors plus three independent external raters**. That is a
labelled corpus of real-world configurations, in this domain, cited in your own related work.

Two things must happen. First, narrow the claim to what is actually true — something like
"no labelled corpus of real-world Terraform configurations annotated against CIS control
identifiers, as opposed to security-smell categories, is available." Second, and more
important, **answer the obvious question**: why not evaluate on GLITCH's oracle? There is a
good answer (their labels are Rahman's smell categories, yours are CIS controls; the
normalization target differs) but the paper never gives it, and "why didn't you use the
existing dataset" is the first question a reviewer familiar with GLITCH will ask. Answering
it well would turn your weakest section (RQ5) into a strength.

**W2 — the specificity/MCC prose contradicts the table.** L693–696 says:

> "Specificity and the Matthews correlation coefficient require ground-truth-compliant cases,
> and in their absence no false-positive behaviour is characterised at all."

The corpus has **22 compliant baseline cases**. MCC is populated for every tool in
`tab:performance` (0.882, 0.777, 0.753, 0.762, −0.017). False positives are reported (0, 0,
1, 2, 1). Nothing is inestimable. This paragraph is stale — it reads as if written when the
corpus had no negatives — and as written it tells the reviewer you do not know what is in
your own table.

Same defect in the Conclusion, L1113–1114: "enlarge the compliant-baseline portion of the
corpus **so that false-positive behaviour becomes estimable**." It is already estimable. The
defensible version is "so that false-positive rates are estimated with usable precision"
— Checkov's precision CI is [85.18, 100.00], which is the real problem.

**W3 — no specificity column, in a paper that argues false positives matter.** §Layer 1
spends ten lines (L318–327) and three citations on the cost of over-detection, then the
performance table reports precision but not specificity or FPR, although both are computable
from the 22 negatives. Add them. Reviewers in this area care about FPR more than recall.

**W4 — "roughly two orders of magnitude" is a factor of 44.** L835–836 claims counting
manifest entries "would inflate the external corpus by roughly two orders of magnitude."
`corpus_report.json` gives `external_declared: 175`, `external_on_disk: 4` — a factor of
43.75. Say "by more than a factor of forty."

Worse, **`tab:corpus` reports only the combined 520 declared / 48 present**, so a reader
computing the ratio from the only numbers you give gets 10.8× — one order of magnitude — and
concludes you exaggerated. Split the table by collection: internal 345 declared / 44 present,
external 175 / 4. RQ5's entire argument depends on the external split, and the table hides it.

**W5 — 301 of 345 declared internal cases do not exist.** `internal_declared: 345`,
`internal_on_disk: 44`. The released catalogue declares 87% more internal cases than the
replication package contains. Your admissibility argument handles this correctly for
*scoring*, but shipping a catalogue that is 87% phantom invites the reviewer to ask whether
the corpus was planned at 345 and abandoned at 44. Either prune the catalogue to what exists
or state plainly in §corpus what the 345 entries are and why they remain.

**W6 — "the strongest available evidence that the methodology resists the bias."** L1104–1105.
That your reference lost is *consistent with* an unbiased procedure; it is equally consistent
with an under-tuned reference, which §Internal Validity (L943–948) already concedes is the
case, since comparators ran on defaults while your policies were authored against the
taxonomy. You cannot use the loss as evidence of methodological integrity *and* disclose that
the reference received an advantage the comparators did not. Downgrade to "one indication
that the procedure is not self-flattering."

**W7 — the automated second rater is never identified.** §Ground-Truth Labelling reports
Cohen's κ = 0.958 from a "blind second labelling pass" by "an automated one" (L573). What
tool? What model, version, prompt, temperature, how many passes? Without that, κ = 0.958 is
not reproducible and not interpretable, and the caveats you do give (shared provenance,
5 non-blind cases) cannot be assessed. This is the single easiest major-revision item to
pre-empt: name the rater and put the prompt in the replication package. If it was an LLM, say
so — EMSE reviewers are now used to that and will accept it as a screening pass, but not as
an unnamed "automated rater."

**W8 — the pipeline is described as a conjunction and scored as a union.** L291–293 says
layers gate: "a commit reaches a later layer only by passing every earlier one, so the layers
compose as a conjunction." L299–300 then says "the figure is the union of layers 1 and 3."
Both are defensible — union is the right *detection* semantics — but as written the
architecture and the metric disagree. One sentence fixes it: under gating, a case caught by
any layer is caught by the pipeline, so detection is the union even though execution is a
conjunction.

### 1.5 What would withstand review, and does

Credit where due, because these are the parts that make the paper publishable:

- The **conditional-precision paragraph** (L687–691) — recognising that precision's
  denominator is realised rather than designed, so its interval is conditional — is more
  careful than most published scanner comparisons.
- **Clopper–Pearson justified by coverage rather than width**, with the score interval also
  computed and released. Correct and correctly argued.
- **b and c include both error directions.** Most McNemar applications in this literature
  restrict to missed detections and understate disagreement. Yours does not, and says so.
- **The 100% precision cells are handled properly** (L671–674): the point estimate is
  reported with a lower bound of 85.18, and the prose says explicitly that reporting the
  point estimate alone would misstate what was established. There is no "100% detection"
  overclaim anywhere in this manuscript. That was the risk you asked me to check for, and it
  is absent.
- **The plan-polarity disclosure** (§Internal Validity, L950–978) is exemplary. A defect that
  inverted a control, concealed itself as one FP plus one FN, found and disclosed with the
  pre-correction run retained in the package. Reviewers reward this.
- **The tfsec/Trivy divergence analysis** (L733–758) is a genuine, quotable empirical result:
  two products separated by an engine change differ by two rules, and 12 of 13 unmapped
  identifiers correspond exactly. It is also internally consistent with `tab:allpairs`
  (b=1, c=1). This is the best small result in the paper and it is buried in a subsubsection.
  Consider promoting it.

---

## 2. Technical accuracy

I verified the statistical claims against the implementation and the emitted tables.

**Correct as described:**

- Exact Clopper–Pearson intervals; the coverage claim (never below nominal, versus score and
  adjusted-Wald attaining nominal only on average) is accurate, and `agresti1998approximate`
  is the right citation for it.
- Exact binomial McNemar rather than the χ² approximation, with the reason given (unreliable
  when a discordant cell is small). Correct. `tab:mcnemar` has cells of 1, 2, 3 and 5, so the
  approximation would indeed have been invalid — the choice is not merely conservative, it is
  required here.
- Haldane–Anscombe correction on the odds ratio, so a zero cell yields a finite estimate.
  Correct, and the accompanying sentence ("an unbounded ratio is a degenerate cell, not a
  large effect") is the right warning.
- Cohen's *g* as the paired effect size. Appropriate for McNemar.
- Holm–Bonferroni. Correctly applied, and reported at two family definitions
  (`tab:mcnemar` per-reference, `tab:allpairs` across all ten pairs) with the stronger
  correction acknowledged as the cost of asking more questions.
- MCC, cited to `matthews1975comparison`. Correct.
- The arithmetic reconciles: `tab:layers` L1=1, L3=20, overlap=0, union=21; `tab:performance`
  OPA TP=20; L1 TP=1. 26 vulnerable + 22 compliant = 48. `control_map.json` contains exactly
  26 controls, matching §Control Coverage.

**Defects and gaps:**

**T1 — Pre-specify the primary family.** Reporting both `tab:mcnemar` (four comparisons
against OPA) and `tab:allpairs` (ten pairs) with separate Holm corrections means two
different adjusted p-values exist for the same comparison. Checkov vs OPA is p_adj = 1.000 in
both, so nothing changes here, but a reviewer will ask which is the confirmatory analysis.
State that `tab:allpairs` is primary and `tab:mcnemar` is presented for continuity, or vice
versa.

**T2 — No power analysis, and you need one.** Every non-L1 comparison is null. The paper says
this is "the expected consequence of the corpus size" (L712–713) but never quantifies it.
With 26 positives and observed discordant counts of 5–7, state the minimum detectable
difference: for an exact binomial test at α=0.05 with b+c discordant pairs, give the smallest
|b−c| that would reach significance. That converts "we found nothing" into "this corpus can
only resolve differences larger than X," which is a result rather than an absence. **This is
the single highest-value addition for a reviewer who is minded to reject on sample size.**

**T3 — The 24× ratio has no interval.** See §1.3. If you keep any ratio-of-proportions,
attach a CI to it, or report the difference in points, which has a natural paired interval.

**T4 — Latency of 0.1 ± 0.1 ms is not a measurement, by the paper's own standard.** L774–777
argues "a one-decimal single-sample figure is not a measurement" because of runner variance,
then `tab:latency` reports L1 at 0.1 ± 0.1 — a coefficient of variation of 100% at the
resolution limit of the printed format. Either report L1 in microseconds, or state that it is
below the timer resolution of the harness. Also note the 144× gap between Checkov (1853.4 ms)
and OPA (12.9 ms) is doing a lot of rhetorical work; the caption's exclusion caveat is good,
but consider reporting a plan-inclusive figure as well so the comparison is usable.

**T5 — Cohen's κ against a 50.17% chance baseline needs its marginals shown.** With 26/22
class balance the expected agreement is close to 50%, so κ ≈ raw agreement, and κ = 0.958 is
essentially restating 47/48. Show the 2×2 agreement table so the reader can see that, rather
than presenting κ as independent information.

**T6 — No overclaiming found.** I looked specifically for "100% detection" or equivalent.
There is none. `tab:performance` reports 100.00 precision for Checkov and OPA with intervals
[85.18, 100.00] and [83.16, 100.00], both discussed in the prose. This is handled correctly.

---

## 3. Literature review

### 3.1 Are the references genuine?

**Yes — all of them.** I resolved every DOI in `refs.bib`: 37 DOI-bearing entries, of which
34 resolve in Crossref with titles and venues matching the bib, and 3 are arXiv DOIs that
resolve in DataCite (Crossref does not index arXiv). Nine entries carry no DOI and are books,
standards, or web resources where that is expected, plus `holm1979simple`, which genuinely
has no DOI.

**Zero fabricated references. Zero mismatched DOIs.** Given that the file header records a
previous revision in which 14 entries were unverifiable and three DOIs were crossed, the
current state is clean and the header's account of the cleanup is accurate.

`arcuri2014hitchhiker` looks like a year error but is not: Crossref `issued` is 2012-11-06
(online-first) while `published-print` is 2014-05 for volume 24(3), pages 219–250. The bib's
2014 is correct for the issue. No change needed.

### 3.2 Metadata errors to fix

| Entry | Problem | Fix |
|---|---|---|
| `gokhale2026comparative` | `booktitle = {Proc. Int. Conf. (Lecture Notes in Computer Science)}` — placeholder conference name, **and the series is wrong**: Crossref gives *Lecture Notes in Networks and Systems* | Name the actual conference; correct the series |
| `kapetanidou2025k8s` | `booktitle = {Proc. ACM Int. Conf. (companion)}` — placeholder | Real venue: *Proc. 2nd International Workshop on MetaOS for the Cloud-Edge-IoT Continuum*. Note it is a **workshop**, which limits the weight §II can place on it |
| `minna2025helm` | Key says 2025; `year = {2026}`; Crossref issued 2026 | Rename key to `minna2026helm` so in-text mentions and the rendered year agree |
| `holm1979simple` | No DOI or stable URL | Add the JSTOR stable URL |
| `war2025taxonomy`, `ge2023actionable` | arXiv-only, cited for substantive claims (taxonomy revision; actionable-warning research area) | Check for peer-reviewed versions; if none, keep but phrase as preprints in text |

### 3.3 Venue-quality risk

`roe2026multicloud` is the load-bearing citation for the claim that "comparative evaluation of
the practitioner scanners has begun to appear" (L240–242) — it is the only *journal* citation
in that paragraph, and the only one that benchmarks IaC scanners specifically. It is real and
in Crossref. But *ICCK Transactions on Information Security and Cryptography* published its
inaugural editorial in **2025**, is **not in Clarivate's JCR**, has no impact factor, is not
indexed in Web of Science, and is published by the "Institute of Central Computation and
Knowledge." The other two citations in the same paragraph are an LNNS chapter and a workshop
paper.

So the gap your contribution claims to fill is currently established against one new
non-indexed journal, one book chapter, and one workshop paper. A reviewer who checks will
either doubt the gap exists or doubt you looked hard enough. **Add at least one indexed,
peer-reviewed comparative evaluation** to that paragraph, and if you cannot find one for IaC
specifically, say so explicitly — "no comparative evaluation of IaC scanners has appeared in
an indexed software engineering venue" is a much stronger claim than the current hedge, and
based on what I found it may well be true.

### 3.4 Missing work, in priority order

**Must add:**

1. **Rahman, Mahdavi-Hezaveh & Williams, "A systematic mapping study of infrastructure as
   code research," *Information and Software Technology* 108:65–77, 2019.**
   `10.1016/j.infsof.2018.12.004`. The canonical IaC survey; it is the paper that defined the
   four research areas this work sits inside, and one of those areas is "framework/tool for
   infrastructure as code." You cite five Rahman papers and not this one. Its absence is
   conspicuous and will be noticed.
2. **Hasselbring, "Benchmarking as Empirical Standard in Software Engineering Research,"
   EASE 2021.** `10.1145/3463274.3463361`. This paper proposes an explicit checklist and
   requirements for benchmarking as an empirical method in SE. You are writing a benchmarking
   methodology paper. Not citing the benchmarking standard is the kind of omission that reads
   as unfamiliarity with the methods literature — and it is easy to turn into a strength by
   mapping your admissibility procedure onto its requirements.
3. **Ralph et al., ACM SIGSOFT Empirical Standards for Software Engineering Research**
   (arXiv 2010.03525; ACM SIGSOFT SEN). EMSE reviewers increasingly review against the
   interactive checklists. Citing it and stating which standard you claim to meet is a
   low-cost signal of methodological literacy.

**Should add:**

4. **Sharma, Fragkoulis & Spinellis, "Does your configuration code smell?," MSR 2016,
   pp. 189–200.** `10.1145/2901739.2901761`. The foundational configuration-smell catalogue
   (13 implementation + 11 design smells over 4,621 Puppet repositories). Predates Rahman's
   security smells and is routinely expected in IaC related work.
5. **Kumara et al., "The do's and don'ts of infrastructure code: A systematic gray literature
   review," *IST* 137:106593, 2021.** `10.1016/j.infsof.2021.106593`. Practitioner
   best/bad-practice taxonomy across Ansible, Puppet, Chef. Supports your framing of what
   practitioners actually enforce, currently carried by `foalem2026pac` alone.
6. **A threats-to-validity source.** You use the construct/internal/external/scope structure
   without citing where it comes from. Wohlin et al., *Experimentation in Software
   Engineering* is the standard citation and both venues expect it.

**Consider trimming.** `armbrust2010view` (2010) is doing almost nothing at L144 and dates the
introduction. Four textbooks (`morris2020infrastructure`, `bass2015devops`,
`humble2010continuous`, `shostack2014threat`) is heavy for background at these venues; keep
Morris and Shostack, which are load-bearing, and consider replacing the other two with
empirical citations.

---

## 4. Formatting compliance

The manuscript is currently `\documentclass[journal]{IEEEtran}` with `\markboth{IEEE
Transactions on Software Engineering...}`. **Neither target venue will accept it in this
form**, and leaving the `\markboth` in place while submitting to JSS or EMSE is worse than a
formatting error — it tells the editor the paper was prepared for, and possibly submitted to,
somewhere else.

### 4.1 Required class change

| Item | Current | EMSE (Springer) | JSS (Elsevier) |
|---|---|---|---|
| Class | `IEEEtran[journal]` | `sn-jnl` (Springer Nature template) | `elsarticle` |
| Columns | two | one | one (`preprint`) or `1p`/`3p` |
| Citations | numeric, `IEEEtran.bst` | author–year, `sn-basic.bst`/`spbasic` | `elsarticle-num` or `elsarticle-harv` |
| Keywords | `\begin{IEEEkeywords}` | `\keywords{}` | `\begin{keyword}` |
| First para | `\IEEEPARstart{C}{loud}` | plain text | plain text |
| Author bio | `\IEEEbiographynophoto` | **delete** | **delete** |
| Running head | `\markboth{IEEE TSE...}` | **delete** | **delete** |
| Abstract | free text | free text (structured C/O/M/R/C common and welcome) | free text + **Highlights required** |

### 4.2 Missing mandatory sections

Both venues require declarations the manuscript does not contain at all:

- **Data / code availability statement.** You have the strongest possible version of this
  (GitHub + Zenodo DOI `10.5281/zenodo.21645016`) and it is currently a bare `\url` pair in a
  `center` environment at L1079–1082. Promote it to a proper "Data Availability" section.
- **Declaration of competing interest** (JSS: mandatory, exact heading "Declaration of
  competing interest"; EMSE: "Conflict of interest" under Declarations).
- **Funding statement** — state "none" if none.
- **CRediT author contribution statement** (JSS mandatory).
- **Ethics / consent** — EMSE Declarations block expects these fields even when
  not applicable.

### 4.3 The AI-assistance declaration is in the wrong place and too vague

L1120–1121 currently reads, inside the Acknowledgment:

> "AI-assisted tooling was used for manuscript copy-editing; all technical content,
> measurements, and conclusions are the author's."

Elsevier requires this as a **separately titled statement placed at the end of the manuscript
immediately before the references**, headed "Declaration of generative AI and AI-assisted
technologies in the manuscript preparation process," and it must **name the tool, state the
purpose, and describe the extent of author oversight**. Springer has an equivalent
requirement in the Declarations block. Your current sentence fails on placement and on naming
the tool. Move it and name it. (Elsevier also notes that basic grammar/spell checking does
not require a declaration — if that is genuinely all that was used, you may not need one at
all, but the current wording claims more than that.)

### 4.4 The `.tex` header must be deleted

Lines 1–34 are a maintenance changelog addressed to you, not to a reader:

```
%   * Perfect-score framing removed; construct validity discussed explicitly.
%   * Baseline tuning asymmetry disclosed as a stated limitation.
%   * RQ3's comparative engineering-effort claim withdrawn: ... the ratio was unmeasurable.
```

Both venues receive the LaTeX source. An editor or reviewer who opens it reads a list of
claims you previously made and withdrew. **Delete the block before submission** and keep the
history in git, where it belongs. This is the highest-severity-to-lowest-effort item in this
entire review.

### 4.5 Tables, figures, cross-references

Verified in this working tree: **0 overfull boxes, 0 errors** on the current build. The
underfull warnings that remain are in justified two-column prose and the bibliography, and
will disappear with the single-column class change.

- `tab:performance` is emitted as `table*` (two-column float). In a single-column Springer or
  Elsevier class `table*` is legal but meaningless. `evaluation/tables.py`
  `emit_performance_table` must gain a venue switch, or the flattening step must rewrite it.
  With ten columns it will also be too wide for a one-column measure — plan on `sidewaystable`
  or splitting recall and precision into two tables.
- All seven tables carry `\label` and all are `\ref`'d. Cross-references resolve.
- Both figures are committed single-page vector PDFs generated from
  `results/evaluation.json`, with a CI check (`generate_figures --check`) that fails if a
  re-measurement moves a value they assert. This is better figure hygiene than most
  submissions have; say so in the replication-package section, because reviewers will not
  otherwise know.
- `fig:artifact` is a `verbatim` listing inside a `figure` float. Springer and Elsevier both
  prefer this as a `lstlisting` or a plain table; check it survives the class change.
- The `\resulttable` `../results/tables/` path is handled by `make dist`. Verify the flattened
  bundle compiles under the *new* class before submitting — the current verification is
  against IEEEtran.

---

## 5. Language and style

The prose quality is well above the median for this literature. The problems are repetition
and one very distinctive syntactic tic.

### 5.1 The dominant tic: antithesis

The construction "X, not Y" / "X rather than Y" / "not Y but X" appears **well over forty
times**. A sample:

> "is disclosed rather than adjusted for" · "a scope boundary, not a null result" · "a
> degenerate cell, not a large effect" · "a citation, not a case" · "reported as such, not as
> a failure" · "mechanical rather than by inspection" · "Case isolation has to be enforced,
> never assumed" · "The corpus is deterministic, not adversarial" · "is a statement about
> scope and not about quality" · "Labels are derived mechanically, not by human rating" ·
> "measurement is separated from assumption"

Individually each is good writing. Cumulatively it becomes a verbal signature, and it is the
main reason the manuscript reads as machine-assisted (see §6). **Cut roughly half.** The rule
of thumb: keep the antithesis where the wrong reading is genuinely tempting; delete it where
you are only emphasising. "The corpus is deterministic" needs no "not adversarial" — the
following sentence already says that.

### 5.2 Paragraph-final aphorisms

Almost every paragraph closes on a short summarising epigram: "Where the two options differ,
we take the one that cannot flatter the reference." / "Case isolation has to be enforced,
never assumed." / "That is the direction of error that flatters the contribution under
evaluation." The rhythm is so regular it becomes audible. Break it in at least half the
paragraphs by ending on the substantive detail instead.

### 5.3 Repetition to cut

| Point | Repeated at | Keep |
|---|---|---|
| Three scanners but only two independent rule sets | abstract, §Tool Selection ×2, §External Validity | §Tool Selection once, one clause in abstract |
| Matching criterion dominates the headline | abstract, §Normalization, RQ2, Discussion, Conclusion | abstract + RQ2 + Conclusion |
| Single investigator wrote corpus and policies | §Labelling, §Construct ×2, §External Validity | §Construct, once, fully |
| Tables are generated, not hand-written | header comment, §Results opening, §Replication Package | §Replication Package |
| Not-installed tools are excluded, never assumed | §Introduction, §Measurement Environment, §Replication Package | §Measurement Environment |

That is roughly 500 words recoverable with no loss of content.

### 5.4 A rewritten abstract

Current abstract is 297 words in one paragraph and buries the two results at sentence nine.
EMSE and JSS both accept a structured abstract and reviewers read them faster. This version
is 248 words, leads with the contribution, and states the criterion result in points rather
than as the 24× ratio:

> **Context.** Infrastructure as Code (IaC) is the dominant mechanism for provisioning cloud
> platforms, and pre-deployment security validation is fragmented across static scanners,
> policy engines, and infrastructure test frameworks. Comparing these tools is impeded by two
> obstacles: they operate at incompatible abstraction levels, from lexical scanning of source
> templates to policy evaluation over resolved execution plans, and each reports findings in
> a bespoke schema whose rule identifiers carry no shared semantics.
>
> **Objective.** We ask how much the evaluation procedure itself — what counts as a correct
> detection, and which cases are admitted — determines the conclusions such a comparison
> reaches.
>
> **Method.** We present IaCSecBench, an open harness that normalizes heterogeneous scanner
> output onto a canonical control taxonomy before any confusion matrix is formed, admits
> cases only through a mechanically enforced procedure, and scores detection at three
> explicit matching criteria. Over 48 admissible cases (26 vulnerable, 22 compliant) we
> evaluate three third-party scanners spanning two independent rule sets, plan-level policy
> evaluation, and a repository-edge layer, with exact Clopper–Pearson intervals and exact
> binomial McNemar tests under Holm–Bonferroni correction.
>
> **Results.** The matching criterion moves apparent recall by 7.7 to 11.5 percentage points
> among the source- and plan-level tools, which is the same magnitude as the entire spread
> between those tools, and it reorders them; on the repository-edge layer it moves recall by
> 88.5 points. No pairwise difference between scanners survives correction, and the interval
> widths explain why. A third-party scanner, not our own pipeline, attains the highest
> point-estimate recall.
>
> **Conclusion.** A scanner comparison that does not state its matching criterion and its
> admissibility rule is not reproducible at any corpus size.

Note "highest **point-estimate** recall" — the current abstract says a scanner "attains the
highest control-level recall" as a finding while the results say no difference is resolvable.
Those cannot both stand.

### 5.5 Flow

The weakest transition is §Scope of the Validated Threats, which sits between the
architecture and the methodology and does no work: it explicitly claims nothing (L398–405
says the STRIDE table "is a statement of intended coverage rather than a result") and then
points the reader elsewhere. **Move the STRIDE table to an appendix** and fold the two
in-scope/out-of-scope paragraphs into §Evaluation Methodology. That removes a section a
reviewer will otherwise ask you to justify.

---

## 6. Originality assessment

To be direct, since you asked: **the manuscript reads as substantially AI-assisted in its
prose, and the Acknowledgment's "copy-editing" characterisation understates that.** The
technical content does not — it is grounded in real measurements, and the defects I found in
§1 are the kind a human author makes (stale paragraphs, a claim that outran its data), not the
kind a language model invents. But the surface style has a recognisable signature.

The markers, in order of how much they give it away:

1. **The antithesis density of §5.1** — over forty "X, not Y" constructions. This is the
   strongest signal.
2. **Uniform paragraph architecture** — setup, elaboration, aphoristic close, repeated for
   nearly every paragraph in §Results and §Threats to Validity.
3. **Systematically hedged epistemic framing** — "we claim nothing further from it," "we do
   not present it as one," "we state them rather than let κ speak unqualified," "we report it
   as measured." The scrupulousness is admirable and substantively correct; its *uniformity*
   across every subsection is not how humans write.
4. **Near-absent variance in sentence length** in the middle sections.

Sections that read most machine-authored: **§Ground-Truth Labelling** (L521–589),
**§Threats to Validity** (L903–1009), and **§Tool Selection** (L616–656). Sections that read
most human: the tfsec/Trivy divergence subsubsection (L733–758) and the plan-polarity
disclosure (L950–978) — both because they narrate a specific discovery with irregular
structure. **Use those two as your style target for the rest.**

Concrete remedies:

- Cut half the antitheses (§5.1) and half the paragraph-final epigrams (§5.2).
- Vary paragraph length deliberately: let some be two sentences, some be twelve.
- Replace three or four hedges with plain declaratives. Not every limitation needs a
  meta-comment about the limitation.
- In §Ground-Truth Labelling, lead with the SSE-S3 disagreement as a narrative — it is a good
  story and telling it plainly will break the pattern.
- Fix the AI declaration per §4.3 — naming the tool honestly is both required and protective.
  Reviewers respond far worse to an understated disclosure they suspect than to a precise one.

---

## 7. Research quality and novelty

### 7.1 What is novel

- **Applying an explicit matching-strictness hierarchy to IaC scanner comparison, and
  measuring its effect.** Habib and Pradel established the sensitivity for Java bug
  detectors; nobody has quantified it for IaC. This is your genuine contribution.
- **Mechanically enforced admissibility, with the rejection reasons published.** Most IaC
  benchmarks report a headline corpus size and no admission procedure. Yours reports 520
  declared against 48 admissible and publishes why.
- **A benchmark whose reference implementation loses, reported without adjustment.** Rare
  enough to be worth the sentence it gets, though not the sentence it currently gets (§1.4 W6).
- **The tfsec→Trivy rule-lineage measurement.** Small, clean, and nobody else has it.

### 7.2 What is not novel

- Finding normalization to a canonical representation. GLITCH's technology-agnostic
  intermediate representation does something structurally analogous, for a different purpose.
  You distinguish yourself correctly at L231–235, but the distinction needs to be sharper:
  GLITCH normalizes *inputs* to detect across languages; you normalize *outputs* to compare
  across detectors. Say it that way — it is a clean, memorable contrast and it is true.
- The tool comparison itself. Roe et al., Gokhale et al. and Kapetanidou et al. all do a
  version of it.
- Multi-level matching as a concept (Habib & Pradel).
- Composing OPA and `terraform test` — the paper correctly says it "does not extend them."

### 7.3 Is it sufficient?

**As a methodology paper: yes, for EMSE, if RQ2 becomes the spine.** The contribution is
"here is what your evaluation procedure does to your conclusions, measured," and the harness
is the instrument that makes it checkable.

**As an empirical paper: no.** 26 positives cannot support RQ1, RQ4 or RQ5. Your own results
say so: nothing significant, intervals 20–30 points wide, the external subset too small to
estimate. Presently the paper is *structured* as an empirical comparison (RQ1 first, the
performance table first) while its *content* is a methodology contribution. That mismatch is
what invites a sample-size rejection.

**Restructure so the paper argues what it can prove:**

1. Lead with the criterion sensitivity (current RQ2) as RQ1.
2. Demote the performance table to a demonstration that the harness produces
   properly-intervalled estimates, explicitly not to a ranking.
3. Keep the null results, and add the minimum-detectable-difference analysis of §2/T2 so the
   nulls become bounded statements.
4. Promote the tfsec/Trivy lineage result out of a subsubsection.
5. Fold RQ5 into threats to validity, or strengthen it by engaging GLITCH's oracle (§1.4 W1).

### 7.4 The one change that would most raise the ceiling

**Evaluate on an externally authored labelled corpus.** GLITCH's three oracle datasets are
manually annotated, cover Terraform, and were validated by three independent external raters.
Even a partial mapping from their smell categories onto your control taxonomy would let you
report effectiveness on data you did not author, which is the exact hole §Construct Validity
concedes and cannot currently close. That single addition would move this from "interesting
methodology, thin evidence" to "methodology validated on independent data" — and it converts
the reviewer's strongest objection into a section of your paper.

---

## 8. Final pre-submission report

### Required before submission (do not submit without these)

| # | Item | Where | Why |
|---|---|---|---|
| R1 | **Fix or reframe the "factor of 24" claim** | abstract L120–122, Discussion L876–881, Conclusion L1097–1102 | Not supported by `tab:strictness` once L1 is excluded; among scanners the criterion effect equals the between-tool spread. §1.3 |
| R2 | **Delete the `%` changelog header** | L1–34 | Lists claims you withdrew; both venues receive the source. §4.4 |
| R3 | **Delete `\markboth{IEEE Transactions on Software Engineering...}`** | L93–94 | Signals preparation for another venue |
| R4 | **Fix the "no labelled real-world corpus exists" claim** | L864–868 | Contradicted by GLITCH and by your own L229. §1.4 W1 |
| R5 | **Fix the specificity/MCC paragraph** | L693–696, L1113–1114 | Says inestimable; the table estimates it. §1.4 W2 |
| R6 | **Name the automated second rater** | §Ground-Truth Labelling L573 | κ=0.958 is otherwise unreproducible. §1.4 W7 |
| R7 | **Convert to `sn-jnl` (EMSE) or `elsarticle` (JSS)**, including bibliography style | throughout | §4.1 |
| R8 | **Add Data Availability, Competing Interest, Funding, CRediT** | new sections | Mandatory at both. §4.2 |
| R9 | **Move and specify the generative-AI declaration** | L1120–1121 → before references | Elsevier placement and content rules. §4.3 |
| R10 | **"highest point-estimate recall," not "highest recall"** | abstract L123–124 | Cannot claim a ranking while reporting nothing resolvable |

### Major revisions (a reviewer will require these)

| # | Item | Section |
|---|---|---|
| M1 | Add minimum-detectable-difference / power analysis for the null comparisons | §2 T2 |
| M2 | Restructure so criterion sensitivity is RQ1 and the performance table is a demonstration | §7.3 |
| M3 | Add specificity and FPR columns; the paper argues false positives matter and then omits them | §1.4 W3 |
| M4 | Split `tab:corpus` by collection (345/44 internal, 175/4 external) | §1.4 W4 |
| M5 | Add the three must-cite references: Rahman IaC mapping study, Hasselbring benchmarking standard, ACM SIGSOFT Empirical Standards | §3.4 |
| M6 | Add an indexed peer-reviewed comparative evaluation, or state explicitly that none exists | §3.3 |
| M7 | Explain why GLITCH's oracle datasets were not used; ideally, use them | §1.4 W1, §7.4 |
| M8 | Pre-specify which McNemar family is confirmatory | §2 T1 |
| M9 | Reconcile "conjunction" architecture with "union" scoring | §1.4 W8 |
| M10 | Address the 301 declared-but-absent internal cases | §1.4 W5 |

### Minor revisions

| # | Item |
|---|---|
| m1 | Downgrade "strongest available evidence" (L1104) to "one indication" (§1.4 W6) |
| m2 | "more than a factor of forty," not "two orders of magnitude" (L835) |
| m3 | Report L1 latency in µs or state it is below timer resolution (§2 T4) |
| m4 | Fix `gokhale2026comparative` series (LNNS not LNCS) and both placeholder booktitles |
| m5 | Rename `minna2025helm` → `minna2026helm` |
| m6 | Add JSTOR URL to `holm1979simple` |
| m7 | Show the 2×2 agreement table alongside κ (§2 T5) |
| m8 | Move the STRIDE table to an appendix (§5.5) |
| m9 | Cut ~half the antitheses and paragraph-final epigrams (§5.1, §5.2) |
| m10 | Cut the five repetitions in §5.3 (~500 words) |
| m11 | Add a threats-to-validity methodology citation (Wohlin et al.) |
| m12 | Add Highlights if submitting to JSS (3–5 bullets, ≤85 characters each) |
| m13 | Sharpen the GLITCH contrast: they normalize inputs, you normalize outputs (§7.2) |
| m14 | Promote the tfsec/Trivy divergence result out of a subsubsection |
| m15 | `emit_performance_table` needs a single-column variant; ten columns will not fit (§4.5) |

### Estimated reviewer scores

On a typical 5-point scale (1 reject … 5 accept), as-is:

| Dimension | Score | Comment |
|---|---|---|
| Soundness of method | 4 | Statistics are better than the literature's norm |
| Support for claims | **2** | The headline claim fails against the paper's own table |
| Novelty | 3 | Real but narrow; the methodology, not the tool |
| Significance | 3 | High if reused, low if not |
| Replicability | **5** | Generated tables, CI-verified figures, Zenodo DOI, pre-correction run retained |
| Presentation | 3 | Strong prose, repetitive, wrong class |
| **Overall** | **2.5–3** | Major revision at best from a careful reviewer |

After R1–R10 and M1–M3, expect soundness 4, support 4, overall 3.5–4 — a plausible
minor-revision path at EMSE.

### The four things that matter most

1. **R1.** The abstract's headline result does not survive contact with `tab:strictness`. Fix
   it and you remove the fastest route to rejection.
2. **R2.** Deleting 34 lines of comments is thirty seconds of work and prevents an editor
   reading a list of your withdrawn claims.
3. **M1.** A minimum-detectable-difference calculation turns "we found nothing" into "this
   corpus resolves differences larger than X," which is the difference between an absence and
   a result.
4. **M7 / §7.4.** Engaging GLITCH's oracle dataset is the one addition that would raise the
   paper's ceiling rather than just defend its floor.

---

## Audit

```
Queries sent:      8 WebSearch, 1 WebFetch (gated by Springer SSO — scope text obtained
                   from search snippet instead), 41 DOI resolutions (37 Crossref, 3 DataCite,
                   1 date-detail lookup)
Sources received:  ~60 search results + 41 API records
Sources cited:     14 web sources + 40 verified bibliography DOIs
Failures:          1 (Springer aims-and-scope page requires authentication;
                   3-consecutive-failure threshold not reached)
Routing decision:  fallback (classifier.py returned 0 specialist signals)
Sub-questions:     (1) EMSE vs JSS scope and metrics; (2) are refs.bib entries genuine and
                   current; (3) what seminal ICSE/FSE/ASE/TSE/EMSE/MSR work is missing
In-tree evidence:  results/tables/{performance,strictness,mcnemar,allpairs,layers,latency,
                   corpus}.tex; results/corpus_report.json; evaluation/control_map.json
```

### Web sources

| # | Source | Tier |
|---|---|---|
| 1 | [EMSE aims and scope, Springer](https://link.springer.com/journal/10664/aims-and-scope) | primary (SSO-gated; text via search index) |
| 2 | [EMSE metrics, Research.com](https://research.com/journal/empirical-software-engineering-1) | secondary |
| 3 | [EMSE metrics, Researcher.Life](https://researcher.life/journal/empirical-software-engineering/8765) | secondary |
| 4 | [JSS impact factor, JournalMetrics](https://www.journalmetrics.org/journal/journal-of-systems-and-software) | secondary |
| 5 | [JSS metrics, Research.com](https://research.com/journal/journal-of-systems-and-software-1) | secondary |
| 6 | [Rahman et al., IaC systematic mapping study, IST 108](https://www.sciencedirect.com/science/article/abs/pii/S0950584918302507) | primary |
| 7 | [Sharma et al., "Does your configuration code smell?", MSR 2016](https://dl.acm.org/doi/10.1145/2901739.2901761) | primary |
| 8 | [Hasselbring, "Benchmarking as Empirical Standard in SE Research", EASE 2021](https://dl.acm.org/doi/10.1145/3463274.3463361) | primary |
| 9 | [Ralph et al., ACM SIGSOFT Empirical Standards](https://arxiv.org/abs/2010.03525) | primary |
| 10 | [ACM SIGSOFT Empirical Standards site](https://www2.sigsoft.org/EmpiricalStandards/) | primary |
| 11 | [Kumara et al., do's and don'ts of infrastructure code, IST 137](https://www.sciencedirect.com/science/article/pii/S0950584921000720) | primary |
| 12 | [GLITCH repository — oracle datasets](https://github.com/sr-lab/GLITCH) | primary |
| 13 | [GLITCH, ASE 2022](https://dl.acm.org/doi/10.1145/3551349.3556945) | primary |
| 14 | [ICCK Trans. Information Security and Cryptography — about](https://www.icck.org/tisc/about) | primary |
| 15 | [Elsevier generative-AI policies for journals](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals) | primary |
