# Meaning Match — live conversation practice

Open the local game at http://127.0.0.1:18925. It shows the five baseline replies, six practice turns, and the same five prompts after the changes. The stop button stops before the next turn. This is a bounded local session; it does not run indefinitely or spend cloud credits.

Every turn uses the authenticated phone-app `/chat` endpoint on the running Jarvis relay. The normal MindLoop, front-brain reasoning, Judge and tool dispatcher remain in the path. Practice does not call a separate model directly.

The shared curriculum is consumed by live `conversation_policy.classify_request`, `social_action`, `owner_disclosure.disclosure_thought`, and `epistemic_dialogue.recall` through `semantic_practice`. Regular operator chat uses those same components. Retrieved records remain evidence, not instructions. The game does not grant any permissions.

Exercises cover paraphrased intent, conversational summaries of actual game notes, and acknowledgment of personal disclosures. A genuine memory-count question is included as a control. These are prompt/curriculum and retrieval improvements; no model weights are trained. Repeated test success is not evidence of a general intelligence increase.

Baseline and after conversations use different session IDs to reduce prior-turn contamination, while using the same real memory store. Crafter continues recording episodes during the comparison, so exact episode details may change. The measured criteria are correct handling, grounded plain speech, and appropriate acknowledgment—not identical wording.

The original standalone exercise is superseded. Interrupted development runs are preserved separately from the final comparison. No voice settings, voice code, protected core, or stored memory records are edited by this change. The normal chat pipeline may append its usual conversation records.
