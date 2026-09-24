# Jarvis's overnight Crafter sandbox

The new game is **Crafter**, a free, open-source survival environment designed for AI agents: https://github.com/danijar/crafter

Watch and pause/stop locally: http://127.0.0.1:18924

Started September 23 around 11:40 PM. Stops September 24 around **7:40 AM Eastern**. The PC must remain awake for the game to advance. An hourly check is scheduled in this task and will retire after the morning report.

Verified in the actual game: movement through 93 positions, gathering wood and stone, drinking, placing a table, crafting a wood pickaxe, and defeating a zombie. Those are smoke-test results, not promised overnight outcomes.

Jarvis's configured local language model chooses among exploration, gathering, crafting and survival goals. A constrained game controller carries out movement and interactions; it saves reward-based goal-selection statistics between episodes. Observations are restricted to the nearby world. Episode summaries go through a package-only connection into Jarvis's existing Judge-gated memory. A smoke-test summary was accepted as NOTED.

The simulation runs on CPU at below-normal priority. Model planning is infrequent and skipped when Jarvis reports an active request or recent voice activity. The controller continues if model planning is unavailable. Nothing spends cloud credits, publishes content, or modifies the protected core. Minecraft and its world remain separate.

This is game-specific practice and persisted experience, not language-model retraining or proof of general improvement. Results: `status.json`, `latest.png`, `episodes.jsonl`, `last-jarvis-decision.json`, and `memory-receipt.json`. A morning report will be saved after completion.
