# cChardet v3 roadmap

Status: proposed implementation plan; product direction accepted by the maintainer.
Baseline inspected: 2026-09-20, cChardet `bc41189` (2.3.0), bundled
PyYoshi/uchardet `7993e0a`. Implementation milestones below are not completed
by publishing this document. Dates are not delivery promises.

Reading guide:

- [Direction and scope](#product-direction-and-scope)
- [Current evidence](#evidence-at-the-starting-point) and [repository ownership](#repository-boundaries-and-delivery-process)
- [Phase dependencies and release boundaries](#dependencies-priorities-and-release-boundaries)
- [Native foundation](#phase-1-make-native-changes-safe-and-explainable)
- [Corpus and models](#phase-2-reproducible-corpus-and-model-infrastructure)
- [Failure analysis](#phase-3-failure-analysis-and-improvement-selection)
- [Detector improvements](#phases-46-intentional-detector-improvements) and [later research](#phases-79-alternative-implementation-and-later-research)
- [Measurement gates](#measurement-contracts-and-acceptance-gates) and [migration decisions](#v3-contracts-and-migration-decisions)
- [First implementation batches](#first-implementation-batches) and [release gates](#release-gates-risks-and-progress-tracking)

## Product direction and scope

cChardet v3 targets real-world data ingestion: scraping, crawling, HTML and
document ingestion, RAG preprocessing, training-corpus preparation, ETL, and
parallel processing of many files. The core remains a fast, lightweight native
encoding detector, with particular attention to inputs of a few KiB to a few
hundred KiB, low allocation, incremental processing, and independent detectors
running concurrently under conventional and free-threaded CPython.

Download growth motivates investigation, but its causes are unverified.
AI adoption, downstream projects, and ephemeral installations remain hypotheses;
download counts are not evidence of a particular input distribution.

Full chardet compatibility is not the primary objective. Familiar APIs remain
valuable, but v3 may deliberately break Python API, C API/ABI, output, or default
policy compatibility when that enables a demonstrably better design. Compatibility
must not prevent useful progress. Each break needs a rationale, measurements,
an explicit contract, and migration guidance; a compatibility adapter is optional
and must not become permanent complexity in the native hot path.

This is a roadmap for the v3 series, not a requirement to complete every research
phase before 3.0. Rust, a new engine architecture, and SIMD are conditional later
work. The first release must deliver a useful, validated improvement beyond
infrastructure alone; its specific user-visible scope will follow failure analysis.

## Evidence at the starting point

These are repository observations, not a fresh execution of every existing test.

| Area | Existing evidence | Remaining work |
| --- | --- | --- |
| Python development | [uv configuration](../pyproject.toml), [Makefile](../Makefile), typing and tests | Preserve locked setup; separate engine tooling from wrapper tooling |
| CI and native safety | [Test workflow](../.github/workflows/test.yml): Linux ASan/UBSan and Python 3.11–3.14/3.14t on three OSes | Native compiler/configuration matrix, dedicated fuzzing and static analysis gates |
| Native build | [CMake configuration](../src/ext/uchardet/CMakeLists.txt): CMake 3.5 declaration, C++11, Debug injects ASan flags, global CPU/FP flags | Explicit portable options and target-scoped flags; audit actual minimum version and multi-config behavior |
| Native tests | [CTest registration](../src/ext/uchardet/test/CMakeLists.txt) excludes five known failing language/encoding cases | Report all cases and reasons; explicit expected-failure inventory, no silent exclusions |
| Conformance | [Random-byte wrapper test](../tests/test_robustness.py), [native output tool](../src/ext/uchardet/benchmark/uchardet-output.cpp) | Native structured comparison, lifecycle and completion traces, minimized failures |
| Performance | [Native benchmark](../src/ext/uchardet/benchmark/README.md), [Python benchmarks](../benchmarks/pyperf_compare.py), [threading benchmark](../benchmarks/pyperf_free_threading.py) | Versioned workloads, distributions, allocation/memory and scaling reports |
| Accuracy | [Evaluation script](../benchmarks/accuracy.py) reports exact/compatible/decode-equivalent and language metrics per corpus | Per-sample records, versioned metric semantics, split discipline and failure taxonomy |
| Data handling | [Test data policy](test-data-policy.md) | Corpus manifest, license inventory, deterministic generation and leakage checks |
| Model generation | [Generator guide](../src/ext/uchardet/script/README), [BuildLangModel.py](../src/ext/uchardet/script/BuildLangModel.py), language/charset definitions and generation logs | Audit provenance; separate network acquisition from offline generation; reproducible inputs and parameters |
| Packaging | [Wheel workflow](../.github/workflows/build.yaml), [wheel smoke test](../tools/wheel_smoke.py) | Retain installed-artifact coverage as native integration evolves |

The [published performance analysis](performance-analysis.md) records reductions
in native elapsed time of 54.5% for whole-file input and 51.6% for 64-byte chunks
on 158 bundled fixtures relative to the 2.2.0 baseline. These are workload-specific
measurements, not a universal speedup or a new v3 result. Re-establish baselines
before changing the engine. Existing output comparisons do not prove universal
chunk-boundary independence or cross-platform bitwise equality.

## Repository boundaries and delivery process

- This repository owns the cross-project roadmap, Python API/CLI, packaging,
  downstream integration, comparative Python benchmarks and release migration.
- The maintained PyYoshi/uchardet fork owns native build changes, native safety,
  fuzzing, introspection, C API, engine benchmarks and engine conformance.
  Its current integration branch is `cchardet`; retain the actual fork and pin
  submodule commits. Do not redirect `.gitmodules` to an incompatible upstream.
- Initially place corpus/model tools with their native consumers in the fork,
  using locked uv environments for Python tooling. Keep acquisition, generation
  and evaluation as separate modules. A separate data repository is an explicit
  future decision, not a prerequisite for progress.
- Land native changes in reviewable fork PRs, then update the cChardet submodule
  in a dependent integration PR that tests the exact native commit. Python and
  uchardet version numbers need not move in lockstep; native ABI versioning is
  a separate decision.
- Use Draft PRs. Validate locally and batch related commits before pushing.
  Cancel superseded CI runs; avoid repeated pushes solely to poll or retry CI.
  Heavy scheduled jobs and release-wheel builds are separate from quick PR gates.
- Keep small redistributable fixtures, schemas, recipes, decisions and compact
  reports in Git. Store large datasets and raw benchmark artifacts separately
  with hashes and retention locations. CI must not crawl live websites.

Proposed implementation locations (not existing commands or completed artifacts):

| Owner | Proposed artifact |
| --- | --- |
| cChardet | `docs/decisions/`, `docs/v3-migration.md`, versioned benchmark reports |
| uchardet | `CMakePresets.json`, `fuzz/`, conformance and trace tools under `test/` or `tools/` |
| uchardet | `corpus/` schemas/manifests/recipes and `modelgen/` offline generator |
| uchardet | Model inventory plus logical `legacy`/`generated` origins; physical relocation only when useful |

## Dependencies, priorities and release boundaries

| Phase | Priority | Depends on | Exit evidence | Release role |
| --- | --- | --- | --- | --- |
| 1. Native development foundation | P0 | Baseline inventory | Portable builds, safety gates, conformance and trace artifacts | Required for 3.0 |
| 2. Corpus and model infrastructure | P0/P1 | Phase 1 baseline; schema work can overlap | Audited corpus v1, isolated splits, one reproducible model experiment | Required foundation for 3.0; not all models must be replaced |
| 3. Failure analysis | P1/P2 | Phase 2 evaluation slice and Phase 1 traces | Reproducible failure report and ranked improvement backlog | Selects 3.0 user-visible scope |
| 4. Focused accuracy improvements | P2 | Phase 3 | Before/after reports, intentional output deltas, migration decisions | Candidate 3.0 scope |
| 5. Encoding/language expansion | P2 | Phases 2–3 | Independently validated model additions with cost measurements | Candidate 3.0 or later v3 |
| 6. Staged detection and evidence policy | P3 | Phases 3–5 evidence | Hint, truncation and early-stop policy experiments | Optional 3.0; otherwise later explicit contract review |
| 7. Experimental Rust engine | P4 | Stable model/conformance contracts from Phases 1–2 | Behavior-preserving parallel engine and comparative reports | Not a 3.0 blocker |
| 8. Next-generation models/engine | Research | Phases 2–3; Phase 7 if comparing implementations | Architecture proposal supported by measured limits | Later, compatibility reviewed again |
| 9. Advanced optimization | P5 | Profiled bottleneck and all regression gates | Portable fallback, runtime dispatch, measured net benefit | Conditional |

The main path is 1 → 2 → 3 → selected 4/5 → 3.0. Corpus schema and model
inventory can progress during Phase 1; detector behavior changes wait for the
evaluation foundation. Later phases are not an obligation to rewrite a working
engine. Do not force a breaking post-3.0 change into a minor version merely
because it appeared in this roadmap: defer it to a further major if required.

## Phase 1: make native changes safe and explainable

### Build, analysis and CI

Separate Debug/Release from sanitizer selection. Choose and document supported
CMake and compiler minima based on the actual build features and wheel targets;
do not raise the C++ standard merely for modernization. Add target-scoped warning,
sanitizer, benchmark and fuzz options, static/shared builds, install/export smoke
tests, and reproducible presets. Native tools must build without importing Python.
The setuptools extension build currently uses its own integration: verify it
alongside standalone CMake instead of assuming CMake changes cover wheels.

Audit platform and floating-point flags before changing them: candidate scores
may depend on arithmetic behavior. Separate toolchain cleanup from score changes.
Release binaries must not use `-march=native` or unconditional host-specific ISA.

| CI lane | Intended scope | Budget/policy |
| --- | --- | --- |
| Every relevant PR | GCC and Clang on Linux, MSVC on Windows, Apple Clang on macOS; representative Debug/Release and static/shared coverage | Cover dimensions without a full Cartesian product; target ≤15 minutes per native lane initially |
| Every native PR | ASan + UBSan on Linux; deterministic conformance; minimized fuzz regressions | Fail on findings; sanitizer overhead is excluded from performance comparisons |
| Every native PR | Clang Static Analyzer and focused clang-tidy checks | Baseline legacy findings with reason/owner; no new unexplained findings; improve invariants before suppressing |
| Every native PR | Short bounded libFuzzer smoke run | Initial budget 60 seconds per target; deterministic regressions always replayed |
| Scheduled/manual | Longer fuzz campaigns, broader compiler matrix, native ARM64 where available, controlled performance runs | Initial fuzz budget 30 minutes per target; record actual executions, coverage and seed corpus |
| Release candidate | Supported Python/wheel matrix, installed-wheel smoke, sdist rebuild | Conventional and free-threaded builds; approved support matrix recorded at release |

These are initial operational budgets, not current CI configuration or proof of
adequate fuzz coverage. Record timings and adjust them with evidence. Evaluate
MSan for initialized-memory coverage and TSan for independent-detector races when
instrumented dependencies/platforms are practical. Consider CodeQL after local
analysis is useful and its maintenance cost is understood.

### Native conformance and fuzzing

Extend the output tool into machine-readable conformance records. For each
fixture and deterministic generated input, exercise one-shot and 1-, 7-, 64-,
and 1,024-byte feeds, plus seeded random boundaries. Cover empty/very short input,
embedded NUL, malformed multibyte sequences, long repeated/adversarial input,
reset/reuse, repeated finalization, candidate access and completion behavior.
Use bounded fuzz inputs; large-input and allocation-failure tests need separate
resource budgets and fault-injection paths rather than multi-GiB PR fixtures.

Use two different comparisons:

1. **Build/implementation equivalence:** old versus new under the same feed
   schedule and environment. Compare candidate count/order, encoding, language,
   confidence, final encoding, errors and completion events.
2. **Chunk invariance:** identical logical bytes under different feed schedules.
   First record current differences. Decide whether each is a defect, a specified
   early-stop consequence, or an intentional v3 semantic change. Matching two
   builds does not establish chunk invariance.

Capture how many bytes the caller supplied, how many the engine actually examined
where observable, and the event at which `done` changes. A chunk-level stop cannot
be assumed to identify the exact byte that triggered it. Specify whether feeding
after completion is ignored, rejected or processed before comparing traces.

For same-toolchain behavior-preserving work, exact output is the initial gate.
The existing decimal output tool is a starting point; add raw floating-point
representation if claiming bitwise equality. Cross-toolchain differences require
analysis and an explicit numerical contract, not an unexplained epsilon.

Fuzz the public API and relevant internal model/state-machine entry points, with
one-shot/incremental differential properties. Failures become minimized fixtures
with seeds, build flags and reproducer commands under the test-data policy.
Exercise OOM cleanup/error reporting using injectable allocation failures; no
exception may unexpectedly cross a C ABI boundary. Define thread safety for
independent detectors and shared immutable model data; sharing a mutable detector
is a separate contract, not implied by releasing the GIL.

### Introspection and model archaeology

Add opt-in native traces for active/rejected probers, scores, language, state
transitions, early-stop reasons and ranking/tie decisions. Stable reason codes
and model/prober IDs support analysis; verbose event formats may remain developer
interfaces. Compile tracing out or disable it with measured negligible cost in
release builds. Do not record source text by default.

Inventory every model family, generator, input source, revision, license notice,
parameters, generated file and handwritten transformation. Begin with
`script/BuildLangModel.py`, its language/charset definitions and existing logs.
The guide documents automated single-byte model generation; do not assume the
same pipeline regenerates multibyte tables. Mark missing provenance as unknown
instead of inferring it. Deliver a reproducibility gap report before extraction.

Phase 1 is complete when a fresh checkout can build and run the documented
checks, all tracked safety findings and known test failures are visible, native
comparison runs are reproducible, representative failures have useful traces,
and the model inventory identifies what can and cannot currently be regenerated.

## Phase 2: reproducible corpus and model infrastructure

### Corpus dimensions and leakage prevention

Keep corpus **role** independent of corpus **layer**. Roles are training/model
generation, tuning, validation, and independent evaluation. Layers are:

| Layer | Purpose | Initial material and constraints |
| --- | --- | --- |
| A: character coverage | Codec mappings, state transitions and boundary cases | Versioned mapping inputs and generated structural cases; not natural-language accuracy evidence |
| B: controlled text | Language models, ranking, confidence and size curves | Audited multilingual Unicode sources, strictly re-encoded |
| C: independent evaluation | External generalization and comparison | Pinned chardet and charset-normalizer corpora plus other independently maintained sets |
| D: real-world documents | Malformation, declarations and actual ingestion | Local archive extraction and explicitly redistributable documents; no raw Common Crawl pages committed |

Split by original document/source group **before** deriving encodings, fragments,
HTML variants or sizes. Persist split seed, algorithm and assignments. Detect
exact and near duplicates, including overlap with legacy corpus/model sources
where possible. Unknown legacy training overlap prevents claiming a fully
independent result; report it. Once an evaluation failure is used to tune a
model, mark that exposure and use a fresh holdout for the next independent claim.

Source candidates, pending per-dataset review, are Leipzig for multilingual text,
Unicode data for mappings/boundaries, individually reviewed Gutenberg works for
long documents, and Common Crawl for local Web evaluation. Do not assume a
collection-wide license, redistribution right, or permission for generated models.
Keep acquisition adapters optional; failure to access a remote corpus must not
break normal builds or silently reduce an evaluation denominator.

For archive-derived samples, record snapshot, WARC location, offset/length,
content hash, extraction recipe, and label evidence. Declaration alone is not
ground truth. Separate verified labels, compatible possibilities and unresolved
cases; unresolved cases contribute robustness/coverage observations, not fabricated
accuracy scores. Archive availability and deletion requests can limit reproduction;
report missing samples explicitly.

### Manifest and generation contract

Implement versioned JSON/JSONL schemas with validators and small accepted/rejected
examples. The initial fields are:

| Record | Required information |
| --- | --- |
| Source | Stable ID, source URL/location, license identifier/text reference and review status, revision, original hash, language and labeling method |
| Sample | Schema/corpus version, sample and source-group IDs, role/layer, language, encoding and label certainty, encoder/version, source-text and byte hashes, byte/character lengths, transformation parameters, generation timestamp |
| Derivation | Parent ID, normalization policy, selected text range, target and actual size, split assignment, truncation/invalidity status, HTML template and declaration fields when applicable |
| Run | Manifest hash, tool/engine commits, environment, command, seed, excluded/missing counts and reasons, artifact hashes |

Preserve raw Unicode sources. Make normalization, newline conversion, case
handling and text selection explicit and versioned; do not silently normalize
away useful evidence. Encode with strict errors and verify round-trip decoding.
Report unrepresentable text as a rejected derivation, not `ignore`/`replace` output.
Codec aliases, variants such as CP932 versus Shift_JIS, and superset relationships
need a versioned registry tied to actual mapping behavior.

Generate target budgets of 16, 32, 64, 128, 256 and 512 B, then 1, 4, 16, 64 and
256 KiB. Clean samples stop at complete encoded boundaries and record actual size;
stateful encodings must finalize/reset correctly within the budget. Separate
explicitly truncated/adversarial samples may end mid-sequence. Never pad short
sources with repeated text to pretend they are representative larger documents.
Keep equal-content comparisons separate from equal-byte-budget comparisons.

Separate text clean/adversarial and HTML clean/declared/undeclared/mismatched/
malformed fixtures. Include HTTP versus meta conflicts, UTF-8 declarations over
CP932 bytes, absent declarations, XML declarations, and entity-heavy markup.
Record generated declarations independently of actual bytes. Add API responses,
CSV, e-mail, subtitles and document exports incrementally as audited workload
families; synthetic HTML is not a substitute for real Web validation.

### Model generation and provenance

Extract acquisition → normalization → language/encoding filtering → statistics
→ validation → emission into independently testable steps. Start with one
single-byte language/encoding family selected after the inventory. Use a tiny
redistributable corpus to test determinism, plus a separate realistic training
set to assess model quality. A toy deterministic model is not a production model.

Pin generator/runtime/dependency versions with uv, sort traversal and output,
fix random seeds, and isolate network access to acquisition. Run generation twice
in clean environments and compare canonical model content hashes. Store run time
outside canonical content or use a reproducible timestamp policy; provenance
metadata must not make otherwise identical models differ.

Each generated model records model/format versions, generator version/commit,
corpus revision/hash, source license references, language/encoding family,
parameters, origin category, generated-at policy and content hash. Legacy models
retain their actual notices and unknown fields. New generation does not erase
the provenance of reused tables or transformations.

Define a small language-neutral representation for the pilot model, including
table dimensions, order, numeric types, quantization and validation constraints.
Prefer build-time C++ emission initially; do not add runtime loading/allocation
without a demonstrated need. Validate dimensions, ranges and references before
emission. A later Rust emitter must consume the same canonical artifact. The
first schema need not represent every historical model; document unsupported
families and evolve the format with explicit versions.

Track engine, generator, corpus and model licensing independently. MPL-2.0 is a
candidate for a derived Rust implementation, not an approved blanket relicensing
of existing code or tables. License/provenance review is a gate before importing,
redistributing or changing notices; unresolved data may remain locally referenced.

Phase 2 exits with corpus v1 and tested split/manifest validators, deterministic
size/encoding/HTML generation, an audited provenance inventory, and a reproducible
pilot model with a C++ emitter. Do not require recreating unknown historical
training data or replacing all legacy models to pass this milestone.

## Phase 3: failure analysis and improvement selection

Run the pinned 2.3.0 reference and current engine against all available frozen
corpora. Preserve per-sample predictions, candidates, scores, label certainty,
source group, input size, model version and optional traces. Publish counts and
denominators per corpus, language, encoding family, size and workload; distinguish
missing data, unsupported codecs, abstentions, crashes and wrong predictions.

Use multiple labels with supporting evidence rather than force every failure
into one exclusive category:

| Classification | Evidence needed |
| --- | --- |
| `UNSUPPORTED_ENCODING`, `MODEL_MISSING` | Support/model inventory and missing codec or language coverage |
| `WRONG_ENCODING_FAMILY`, `RIGHT_FAMILY_WRONG_CODEC` | Versioned family/mapping definitions and observed candidates |
| `SUPERSET_AMBIGUITY`, `INSUFFICIENT_EVIDENCE` | Same bytes valid/equivalent under multiple codecs, or too little distinguishing evidence |
| `RANKING_FAILURE` | Plausible correct candidate loses, with trace evidence beyond candidate presence alone |
| `CONFIDENCE_CALIBRATION` | Repeated held-out mismatch between defined score interpretation and observed correctness |
| `STRUCTURAL_VALIDATION_FAILURE`, `LANGUAGE_MODEL_FAILURE` | Decoder/state-machine or model/prober evidence |
| `DECLARATION_CONFLICT` | Actual bytes and metadata/declaration evidence disagree |
| `UNRESOLVED` | Evidence insufficient; retain competing explanations |

Measure top-k candidate recall to separate candidate generation from ranking.
Confidence is initially a score, not a guaranteed probability. Define the event
being calibrated (exact codec, compatible decoding, or joint language/encoding),
plot reliability/abstention curves with bin counts, and evaluate calibrated
probabilities only on held-out data. Report sparse strata rather than drawing
strong conclusions from a few documents. Resample by source group when estimating
uncertainty so many derived variants do not masquerade as independent observations.

Rank work by observed occurrence and failure cost, achievable accuracy gain,
implementation effort, runtime/memory cost and provenance readiness. High cost
must lower priority, not increase it through a literal multiplication formula.
Frequency estimates from a convenience corpus are not global Web frequencies.
Publish the evidence and uncertainty behind each selected encoding family.

Phase 3 exits with a replayable report, manually checked representative failures,
a ranked backlog and a 3.0 scope decision. Re-run reviewed metric definitions
identically across competitors; the current use of `chardet.evaluation` is a
versioned dependency, not an immutable definition of correctness.

## Phases 4–6: intentional detector improvements

### Phase 4: focused corrections

Start with demonstrated structural/BOM problems, model selection, ranking and
confidence. For each change, link the failure class, fix the general byte/model
property, and provide positive, negative and ambiguous cases. Publish complete
before/after per-corpus results and candidate deltas, including regressions.
Do not tune directly to an external benchmark or accumulate ad hoc heuristics.
Changes to language confidence must distinguish language evidence from an
encoding label: ASCII does not imply English, and mixed-language input may
require unknown/multiple-language semantics rather than a false precise answer.

### Phase 5: targeted coverage

Candidate groups include Japanese, Simplified/Traditional Chinese, Korean,
Cyrillic, Central/Eastern European, Turkish, Greek, Hebrew, Arabic and Vietnamese.
This is an investigation list, not a claim that all these groups are absent.
Select actual language/codec gaps using Phase 3 evidence. Each model addition
needs provenance, disjoint training/tuning/evaluation, independent and real-world
validation, negative-family checks, initialization/allocation cost, model size,
throughput and candidate-stability measurements. Compare legacy and new models
through the same engine before attributing differences to an engine rewrite.

### Phase 6: staged evidence and content hints

Prototype cheap structural checks (BOM, ASCII, valid UTF-8, UTF-16/32 structure,
escape sequences) and optional XML/HTML/HTTP hints. Valid UTF-8 alone does not
prove intended encoding, especially for short ASCII-compatible input. Document
which signals are definitive under the chosen contract and which merely rank
candidates. Specify conflict, absent metadata, malformed markup and hint-invalid
input behavior; use bounded native parsing and measure its cost.

Evaluate a separate API or explicit content hint without silently imposing Web
semantics on generic detection. Keep the statistical decision logic native.
Compare evidence limits of 64 KiB, 200 KiB, 1 MiB and unlimited across workloads,
including inputs whose distinguishing evidence occurs late. Report bytes examined,
accuracy/confidence, latency, allocation and memory. The existing unlimited
default is a baseline, not a v3 constraint: change it if the evidence supports
the choice, with an explicit opt-out and migration documentation.

Early termination and candidate pruning require proofs or measured bounds for
discarded candidates and tests for later contradicting bytes. Use profiling and
failure analysis before architecture changes; avoid adding SIMD to compensate
for redundant work. Phases 4–6 exit per selected feature, not as one large merge.

## Phases 7–9: alternative implementation and later research

An experimental Rust engine starts only after shared model/conformance contracts
are useful. Its purpose is safer maintenance and contributor tooling as well as
performance evaluation. Keep C++ as the runnable reference and choose a bounded
vertical slice before expanding coverage. Initial ports preserve behavior and
reuse approved models; do not mix score/model improvements with porting.

Use typed encoding/language/candidate/state representations, detector-local
mutable state and explicit ownership. Normal detector logic should be safe Rust;
localize and document `unsafe` at FFI, dispatch or optimized kernels. Evaluate
`cargo test`, rustfmt, clippy, property tests, fuzzing, Miri and sanitizers according
to what they can actually check. A thin C ABI is an option, not a reason to copy
the C API into the internal Rust design. Specify buffer lifetimes, ownership,
panic/error translation and independent-detector thread safety at any FFI boundary.

Compare the same feed schedules, malformed inputs, lifecycle, completion events,
candidate order/language/confidence and model content. Require exact equality
where the arithmetic contract permits; investigate mismatches before allowing
documented numerical tolerances. Also compare native latency, throughput, memory,
allocation, parallel scaling, binary size, build/install cost and wheel coverage.
Rust syntax alone does not establish safety, independence or license eligibility.

Promote Rust, maintain both engines, or keep C++ primary only after an explicit
decision report. Broader independently generated models and new architectures
follow evidence of existing limits, with separate compatibility decisions.
SIMD/architecture-specific kernels come last: require a profiled bottleneck,
runtime feature dispatch, portable fallback, cross-architecture correctness and
net wins on the actual small/medium workloads. Reject optimizations whose dispatch,
allocation or maintenance costs exceed their measured benefit.

## Measurement contracts and acceptance gates

Use the native C API benchmark for engine tuning. Use installed release wheels
for cChardet/chardet/charset-normalizer comparisons; native engine timings and
Python API timings answer different questions and must be published separately.
Enable available competitor native accelerators and verify loaded module paths;
report pure-Python fallback as a separate configuration, never infer it from a
package name. Record versions, wheel hashes, interpreter/GIL mode, compiler flags,
CPU/OS, affinity and power policy where available, corpus hashes and commands.

Preload bytes outside timing, warm code/model paths consistently, alternate
baseline/candidate run order and retain distributions. Measure both fresh and
reused detectors; warming must not silently remove initialization cost from the
fresh case. Separate top-result and all-candidate queries, serial and threaded
runs, and one-shot versus incremental input. Keep end-to-end I/O measurements
separate. Record affinity as unavailable on unsupported systems rather than
claiming identical controls. Publish p50/p95 latency, throughput, allocation
counts/bytes, peak memory and model/binary footprint with instrument limitations.

Accuracy reports include exact codec, compatible/superset and decode-equivalent
metrics, language and joint accuracy, abstention, and unknown-label exclusions.
Use strict decoding and separately handle invalid/truncated inputs where
decode-equivalence is undefined. Preserve per-corpus and stratified counts; macro
and workload-weighted summaries may supplement but never replace them.

Maintain a release scorecard in addition to the accuracy/performance reports:

| Dimension | Evidence to retain |
| --- | --- |
| Coverage | Supported codec/language/script inventory, unsupported observed samples, coverage weighted only by a declared workload distribution |
| Robustness | Unique minimized fuzz defects, sanitizer findings, chunk/lifecycle mismatches, OOM handling results and campaign coverage/budget |
| Maintainability | Fresh-checkout setup steps/time, tested compiler/platform combinations, analyzer backlog, deterministic model-generation results and unresolved provenance |
| Alternative engines | FFI/unsafe inventory with reasons, build complexity, conformance differences and maintenance cost alongside speed/memory |

Do not interpret zero observed fuzz failures as proof of memory safety, or a
larger encoding count as evidence of better real-world accuracy.

Initial review thresholds, to be frozen with the Phase 1 benchmark protocol:

- Safety: no untriaged crash, sanitizer error, new analyzer finding or invalid
  output. Known findings remain explicit; an xfail is not a passing accuracy case.
- Mechanical/port changes: no unexplained candidate or lifecycle changes within
  the defined equivalence contract. Intentional changes use a separate review.
- Performance: investigate repeatable >5% native median latency or throughput
  degradation on any primary workload, or >10% p95/memory/allocation increase.
  Define throughput degradation as lower bytes/sec and latency degradation as
  higher elapsed time; do not interchange their percentages. Zero-allocation
  paths require absolute counts instead of percentages. Noise/underpowered runs
  are inconclusive and must be repeated on a controlled runner, not declared wins.
- Accuracy: enumerate every changed known-label outcome; no aggregate gain may
  hide an unexplained family/size regression. Expected ambiguous changes and
  statistically uncertain improvements must be labeled as such.
- An accuracy/performance tradeoff may be accepted through a documented decision
  with scope, measurements and mitigation. Thresholds trigger review, not a ban
  on valuable v3 changes or a license to regress just below the threshold.

## v3 contracts and migration decisions

Create decision records before implementing each affected public contract:

| Decision | Questions to resolve | Decision deadline |
| --- | --- | --- |
| Result and confidence | Mapping versus typed result, unknown/abstention, score semantics, language naming, candidate ties | Before a new public result API; freeze by beta |
| Streaming | `done`, feed-after-done, finalize/reset, partial multibyte state, chunk invariance and errors | Before conformance expectations become the v3 contract |
| Resource/evidence policy | Default `max_bytes`, caller-visible truncation, input copies/lifetimes, mutable buffers during GIL-free work, OOM | Before introducing limits or buffer changes |
| Hints and scope | Generic versus HTML/XML detection, metadata precedence, invalid/binary and mixed-encoding input behavior | Before a hint API or new fallback policy |
| Native boundary | Exported symbols, ABI version/SONAME where applicable, ownership, error codes, Cython coupling | Before native API changes and integration PR |
| Platforms | Python/compiler/CMake minima, architectures, free-threaded support and packaging burden | Before beta; do not drop a supported platform accidentally |
| Data/models | Format versioning, compatible readers, provenance and distribution rights | Before model publication |
| Engine choice | Rust trial exit criteria, dual-engine cost, default engine | Only after Phase 7 evidence |

For each break document old/new examples, affected consumers, conversion or
replacement API, version boundary, rationale, regression evidence and rollback.
Prefer an explicit migration over an ambiguous compatibility flag. Deprecation
in 2.x is useful when cheap, but is not mandatory before a justified v3 break.
No promise is made here to backport new features or maintain 2.x indefinitely;
define the maintenance window at beta. Freeze 2.3.0 as a benchmark reference,
not as a permanent constraint on results or an implicit probability specification.

## First implementation batches

Each row is a bounded PR-sized starting point; split further when native and
wrapper ownership requires dependent PRs. All are initially planned.

| ID | Owner | Work and deliverable | Acceptance/dependency |
| --- | --- | --- | --- |
| V3-01 | uchardet + cChardet | Baseline inventory: known failures, toolchains, model families, native/wrapper benchmark manifest and raw result hashes | Replays documented; no new performance claim without measurements |
| V3-02 | uchardet | Separate sanitizer options from Debug; build presets and supported-toolchain guide | GCC/Clang/MSVC configure/build/test; depends on V3-01 inventory |
| V3-03 | uchardet | Structured native output, comparison harness and completion/lifecycle cases | Same-schedule equivalence and chunk differences reported separately; V3-01 |
| V3-04 | uchardet | ASan/UBSan presets, bounded fuzz targets and regression seeds | Reproducible smoke campaign; minimized failure replay; V3-02/03 |
| V3-05 | uchardet | Analyzer/tidy baseline and invariant-focused fixes | No new findings; fixes isolated from detector tuning; V3-02/03 |
| V3-06 | uchardet | Opt-in prober/ranking trace tool | Explains representative failures; disabled cost measured; V3-03 |
| V3-07 | uchardet | Corpus manifest/split schemas, license inventory and validators | Reject missing rights metadata and cross-split derivations; may overlap V3-02 |
| V3-08 | uchardet | Offline strict re-encoding, boundary-safe size and HTML generation | Deterministic hashes, rejected-derivation counts, leakage tests; V3-07 |
| V3-09 | uchardet | Legacy generator/provenance report, then offline pilot model and C++ emission | Unknowns explicit; two clean generations match; V3-01/07/08 |
| V3-10 | cChardet + uchardet | Failure report, top-k analysis and ranked coverage/ranking backlog | Reviewed examples and untouched holdout; V3-03/06/08 |
| V3-11 | cChardet | 3.0 scope/contract decisions and initial migration guide | Select measurable user-visible work from V3-10; do not invent scope to satisfy a date |
| V3-12 | Both, separate PRs | Selected fixes/models, submodule integration and reports | Gates above, wheel/API tests and intentional delta review; V3-09/10/11 as applicable |

## Release gates, risks and progress tracking

**Alpha:** Phases 1–2 have a working vertical slice, selected user-facing
improvements run through the evaluation pipeline, and experimental/breaking APIs
are labeled. Publish what remains incomplete; alpha does not establish stability.

**Beta:** Phase 3 scope is agreed, selected features pass their gates, public
contracts and migration examples are frozen, corpus/model provenance is reviewed,
and the platform/support matrix and 2.x maintenance policy are documented. Expand
downstream smoke coverage with representative HTML/CSV/streaming/threaded use.

**Release candidate and 3.0:** reproduce the frozen evaluation and controlled
performance reports; resolve blocking safety and unexplained semantic regressions;
validate all supported wheels and sdist installations including type information,
CLI and free-threaded behavior. Link code/model/corpus revisions and artifacts.
Review release notes against the preceding stable release; do not republish 2.x
features as new. Follow [the release procedure](releasing.md), with prerelease
handling updated and tested before the first alpha. Full corpus replacement,
Rust, staged detection and SIMD are not blanket release blockers.

| Risk | Mitigation or decision trigger |
| --- | --- |
| Compatibility stalls needed design work | Use v3 breaks with migration records; reevaluate future major boundaries after 3.0 |
| No clear accuracy win after infrastructure | Publish negative findings, improve labels/traces and revisit scope; do not manufacture benchmark wins |
| Corpus bias/leakage or ambiguous labels | Source-group splits, exposure ledger, fresh holdouts, certainty-aware metrics |
| Lost/unlicensed corpus or unknown model origin | Quarantine redistribution, keep hashes/recipes and explicit unknowns; prioritize auditable replacement |
| New models increase latency or memory | Per-model cost reports, evaluate pruning only with evidence, reject unjustified cost |
| Platform/floating-point drift | Compiler matrix, fixed contracts and preserved mismatch artifacts |
| CI cost or Actions rate limits | Local validation, batched pushes, bounded PR lanes and scheduled heavy work |
| Rust port grows without product benefit | Bounded pilot and comparative decision gate; retain C++ reference |
| Documentation becomes stale | Update milestone evidence and decisions in the implementing PR |

Track each work item as planned, in progress, blocked, deferred or completed.
Completion requires links to merged implementation, reproducible commands,
artifact hashes and acceptance evidence. Record blockers and why a milestone is
deferred; do not silently redefine its scope. Revisit this roadmap after Phase 1,
after the first failure report, and at each release gate. Update release scope
and decisions in Git so contributors can distinguish accepted direction,
proposed thresholds, experimental options and demonstrated results.
