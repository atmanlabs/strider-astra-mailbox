# JARVIS scaffold and training handoff

Prepared for Strider's final review before an ATMAN public patch. These are scrubbed copies of the September 24, 2026 live source, not modifications to the running installation.

- `scaffold/`: the six requested scaffold modules, semantic_practice.py, training_receipts.py, and their shared curriculum.
- `games/meaning-match/`: live word-game driver, browser review UI, probes/tests, retired standalone prototype, and redacted before/after reports.
- `games/situation-gym/`: native Windows app source, simulator, tests, installer, integration patch scripts, specification, review contract, and redacted example runs.
- `games/crafter/`: earlier custom sandbox controller and outcome reports, included for completeness. Install the upstream Crafter dependency separately.
- `training-recall/reports/`: evidence and limitations of the recent recall repair.
- `REVIEW.md`: exclusions and flagged items that need final verification.
- `MANIFEST.json`: hashes of exported source/report files.
- `SCAN.json`: first-pass scan and Python syntax validation results.

No credential, private PSC store, private identity/profile/calendar file, physical-core file, binary, model, or environment is included. Generic scaffold interfaces and placeholder deployment paths remain for review. This package is not ready to run without configuring dependencies and paths. Do not execute historical deployment scripts blindly.

Read REVIEW.md before preparing the public patch. Reported local probe passes do not certify a clean public build or general intelligence improvement.
