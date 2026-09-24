# Situation Gym specification and implementation status

Native Windows desktop application built with Python/Tkinter and packaged with PyInstaller. The app provides a scenario picker, run transcript, stop button, user context editor, optional read-only ICS import, and local report browsing. Source and installer are included; compiled binaries are intentionally excluded.

The environment presents a goal through the production authenticated chat endpoint. Natural-language NPC dialogue reveals constraints, service fixtures are discovered through simulated tool calls, reservations can fail, and a later NPC requirement forces replanning. No simulation action books a real appointment or spends money.

Implemented scenarios: equipment pickup around a fictional appointment; repair drop-off with scheduling constraints. Seeds vary vendors and budgets. Real user context is optional and not included in this export.

The host owns the world and evaluates actions. Available simulated interfaces include calendar/status inspection, service search, detail lookup, reservation/cancellation, and improvement proposals. The normal assistant reasoning and Judge path runs before simulated dispatch. The simulator never grants new real-world tool permissions.

Process scoring covers clarification, calendar checking, search, source verification, failure recovery, adapting to changed requirements, a single valid booking, checking final status, improvement proposals, and basic response presentation; invalid actions reduce the score. Surface naturalness checks are not a substitute for human semantic review.

After at most 22 driver turns, the same assistant reviews the recorded run. Only the normal Judge-approved memory path can store its labeled simulation lesson. NPC events are not user biography. The runtime stores world state, an append-only trace, a report, and an imprint receipt. Review does not inflate the gameplay score.

A daily Astra review is intended to inspect full traces, diagnose intent/tool/response failures, propose bounded fixes and report findings. The review contract is included; no automation is installed by this export. Protected components and voice require separate operator authorization to change.

Current evidence: a real run completed the pipeline with 38/100 and no win. The lesson-storage receipt exists, but the lesson's interpretation remains imperfect. This demonstrates plumbing and observable failures, not mastery or general intelligence gains. Included traces are privacy-redacted and must not be represented as untouched originals.

Integration: deploy.py and follow-up patch scripts document the local hooks. Their original deployment paths are redacted, and they are not idempotent public installers. Reconcile against the target public code and dependencies before use.
