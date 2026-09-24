# Training recall repair — September 24, 2026

The word-game reports existed, but the live calibrated activity lookup searched only recent action receipts. It could not see the training reports. After adding the reports as read-only evidence, another failure became visible: generated prose sometimes failed its existing grounding check, causing a generic fallback despite relevant evidence.

Changed only the evidence adapter and its two integration points: epistemic_dialogue.py reads validated completed training reports alongside lookup evidence; semantic_practice.py can fall back to exact selected plain-language passages from that report if generation fails. New training_receipts.py validates the expected completed practice and follow-up records before supplying a bounded summary. No model weights, PSC contents, permissions, protected Judge, voice, or protected core were changed. Conversation classifier changes were tested and then fully reverted; its original hash matches.

## Live verification

Repeated Strider's exact substantive question through the production owner-authenticated chat path (not a message sent as Strider). Before: “I don't know from the logs I can check.” After: JARVIS described paraphrase practice, answers grounded in retrieved notes, personal-disclosure acknowledgment, and the memory-count control. He explicitly said the record does not establish lasting improvement or feelings. A second question, “What did you practice in Meaning Match today?”, retrieved the same evidence successfully. Full outputs: live-checks.json.

Controls: ordinary greeting and personal-disclosure acknowledgment remained appropriate in intermediate-checks.json. Protected file hashes and the Judge function hash all matched the baseline. Unsupported fallback text and uncertain evidence were rejected by direct checks.

## Limits and next step

This repairs access to the recorded word-game activity; it is not a claim of new intelligence or a newly imprinted autobiographical memory. The generic greeting in Strider's first message remains unchanged deliberately. Direct Strider-origin retesting after this repair is still pending. One broader intelligence-improvement probe produced vague “numbers look solid” wording, despite qualifying that no general intelligence was measured. That existing broad response-quality limitation remains; this narrow change does not certify every answer.

Proceed with the situation game for further measured practice. Keep its evidence and process scores; do not infer improvement merely from winning or storing a lesson. No new game run was started by this repair.

Backups are retained in work/training-recall. Rollback restores epistemic_dialogue.py.before and semantic_practice.py.before and reloads only the relay. The added adapter can remain unused. Existing reports must remain available at their documented local paths.
