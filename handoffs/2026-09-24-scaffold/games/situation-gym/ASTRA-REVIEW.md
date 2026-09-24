# Astra review contract — JARVIS Situation Gym

Installed app: `/REDACTED_LOCAL_PATH`

Data root: `/REDACTED_LOCAL_PATH`

Daily review: **9:00 PM America/New_York**, Codex automation `astra-daily-jarvis-scenario-review`. The native app works independently of Codex; the Astra review needs the Codex host available. No cloud model/API key is needed by the game. JARVIS's local relay and local model must be running.

## Run files

Each `runs\<run-id>\` contains:

- `world.json`: persisted simulated state, hidden fixture details, discovered facts and progress. World fixtures are not real facts about Operator.
- `trace.jsonl`: append-only ordered events. `start`, `conversation`, `tool`, and `cycle` events record actual model decisions and execution. Cycle events contain input, parsed thought/intent/action, real Judge approval/reason, dispatched result, actual live cycle ID and imprint flag. This is the observable execution trace; it is not hidden model reasoning and does not export the protected core or entire PSC.
- `report.json` and `report.md`: current/final process score, world outcome, lesson, and real Judge/PSC receipt. Do not trust a win flag without checking the trace.
- `client-error.json`, if present: transport or app failure. Also inspect the root `last-error.json` and incomplete runs, not only successful reports.

`profile.json` contains Operator's explicitly entered context and optional read-only ICS calendar references. Initial default appointment, service names, prices, and errands are labeled fictional. The PC/phone Jarvis use case is based on his request. Never infer a real appointment from a scenario.

## Required daily work

1. Read `reviews\last-reviewed.json` when present. Discover new and changed runs, including incomplete runs; compare trace hashes, not just directory names.
2. Inspect full traces. Identify misread intent/paraphrases, clarification failures, lost constraints, invented fields, repeated ineffective tools, missing status checks after timeouts, stale reservations after NPC changes, fabricated success, unnecessary provenance/JSON in human dialogue, and Judge/PSC failures.
3. Reproduce concrete failures with bounded local tests in a temporary workspace. Never replay a tool chain against real services. The gym uses local fixture search, not external internet search, and its reservations are simulated.
4. Propose exact fixes and test cases. Keep proposed changes in review files/patches; do not deploy them. Do not change voice, protected core, Judge rules, permission fences, or credentials without Operator's say. No purchases, publishing, external messages or real bookings.
5. Save one dated report and `review-receipt.json` under `reviews\YYYY-MM-DD\`. Include run IDs, evidence locations, severity, reproducible symptoms, proposed fixes, and limitations. Update `last-reviewed.json` only after the report is durable. Give Operator one concise daily findings summary. Stay quiet if there are no new runs.

## Scoring and transfer

Score observable process, not self-reported success: clarification, calendar inspection, active directory search, source checks, status-checked recovery, handling changed requirements, exactly one valid reservation, verification, a self-improvement proposal, and concise conversational language. Invalid actions lose points. Review the natural-language quality manually: the automatic naturalness check is only a surface heuristic.

The live path is `/chat -> MindLoop.run_cycle -> reason/llm_reason -> evaluate_judge -> simulated dispatch -> real memory update`. Simulation turns suppress ordinary fact/biography ingestion. During review JARVIS authors a lesson from the actual trace; it is labeled `SIMULATION LESSON` and submitted to the unchanged Judge and live AuthenticatedPSC. Confirm the receipt and persisted candidate. Storing a lesson is not proof that future behavior improved; measure held-out scenarios and real conversation probes separately.

## Debug locations

Live integration: `/REDACTED_LOCAL_PATH`, plus narrow hooks in `relay.py`, `loop.py`, and `reason.py`.

Source/build/tests/backups: `/REDACTED_LOCAL_PATH`.

Protected files: `core.py`, `exo_core.py`, `gate_policy.json`, `crate.py`, `wake.py`, `seal.py`, voice code/settings, and the `evaluate_judge` function. Never edit `psc.json` directly. Existing Judge-gated append-only storage remains authoritative.
