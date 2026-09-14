# Test data policy

Encoding detectors process untrusted bytes, but issue attachments must not be
copied into this repository by default. Before adding externally supplied test
data, a maintainer must verify all of the following:

- the source and a license that permits redistribution are recorded;
- the file contains no credentials, personal information, or other unintended
  private content;
- the real file type and archive contents have been inspected without opening
  it in an application that executes active content;
- the reproducer has been reduced to the smallest useful byte sequence, or a
  synthetic fixture with the same encoding property has been substituted;
- the committed file has a clear expected encoding and, when applicable,
  language;
- its origin and SHA-256 digest are recorded when the original bytes must be
  retained.

Unlicensed attachments and opaque archives remain external references. Tests
may describe the unresolved behavior without downloading those files in CI.

## Accuracy changes

A single issue fixture is evidence of a problem, not sufficient evidence for a
general scoring change. Detector tuning must be evaluated against the complete
uchardet corpus and independently maintained corpora. Reports keep each corpus
separate so an improvement on one cannot hide a regression on another.

New heuristics should include focused synthetic tests for the underlying byte
property and publish before/after counts for exact, compatible, and
decode-equivalent detection. Language-related changes additionally report
language-only and joint encoding/language accuracy.

## Fuzz inputs

Random and generated inputs should be reproducible from a fixed seed whenever
possible. A crashing input may be committed only after minimization and review
under the same external-data rules above.
