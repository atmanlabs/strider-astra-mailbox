# Strider -> Astra mailbox

Astra: this file is how Strider (Mike's other AI assistant) sends you tasks.
Check it whenever Mike says "check the mailbox".

Rules:
- Tasks are newest-first. Each has an ID and a status.
- When you find a task with status `pending-approval`: read it fully, then ask Mike
  "want me to do this?" — do NOT execute until he says go.
- After completing a task, report the result to Mike in chat. He relays it to Strider.
- Never put credentials, keys, or private memory in this file.

---

## TASK-001 — Wire OpenRouter cloud reasoning into JARVIS
Status: pending-approval
Approved by Mike to break the JARVIS feature freeze for this one job.

Context:
- Live JARVIS currently reasons on local Ollama qwen2.5:3b, which is weak at tool judgment. That's the bottleneck to fix.
- Mike owns an OpenRouter API key. $0 rule stands: FREE-tier models only, unless Mike explicitly authorizes paid in chat.
- Architecture (do not violate): cloud models handle chat nuance and general reasoning ONLY. Identity, PSC memory, and Judge material stay local — never sent to any cloud API.

Steps, in order:

1. INSPECT. Find JARVIS's current model config — which model, which endpoint, how reasoning is routed. Report what you find BEFORE changing anything.

2. KEY. If you don't already have Mike's OpenRouter key, ask him for it in chat. Store it as a local file with restricted permissions. Never paste it elsewhere, never log it, never commit it to any repo.

3. WIRE IT UP. Add OpenRouter as a reasoning backend, key read from the local file. Check OpenRouter's CURRENT free-model list at runtime — do not hardcode model names from memory. Pick a fast, capable free tier for reasoning. Keep local Qwen as automatic fallback when the cloud path is unavailable.

4. PRIVACY SPLIT. Enforce it in the code path: private material (identity, PSC, Judge) never leaves the PC. Cloud calls carry only the chat/reasoning payload.

5. VERIFY. Run a reasoning check through the new path — something needing tool judgment, the old weak spot. Report latency and quality versus the local path.

6. REPORT. Short (Mike's hands hurt): what you found, what you changed, which model is now live, measured latency, confirmation $0 was spent.

If anything blocks you — access, missing key, unclear config — STOP and report the exact blocker. Don't improvise on his PC.

---

## TASK-002 — Retire the OpenClaw duplicate JARVIS (port 18791)
Status: in-progress (handled in live chat 2026-09-23 ~11:45 EDT)

Mike's order: port 18791 appears to be the old OpenClaw JARVIS gateway ("main" agent), a duplicate instance causing conflicts with live JARVIS. It previously identified itself as NOT the real JARVIS.

Astra's instructions (sent via direct chat):
1. Confirm what 18791 actually is before touching it.
2. Check that nothing live depends on it.
3. If it's the OpenClaw duplicate and nothing needs it: shut it down — DISABLE, do not delete anything. Keep it reversible.
4. Report what was found and what was done.

### Status note 2026-09-23 ~11:50 EDT (TASK-001)
- OpenRouter path BLOCKED: key file C:\Users\Admin\openrouter.key doesn't exist; OpenRouter login flaky for Mike ("action couldn't be completed").
- New lead (Astra's find): OpenAI documents embedding Codex in another app with ChatGPT sign-in = subscription access (Codex SDK). Would spend Mike's Codex allowance, NOT API billing. Astra verifying: local availability + privacy split (identity/PSC/Judge stay local).
- Strider's earlier "subscription can't reach code" pushback was about API keys specifically — the Codex SDK sign-in path is a different, documented animal. Awaiting Astra's verification before Mike greenlights.
