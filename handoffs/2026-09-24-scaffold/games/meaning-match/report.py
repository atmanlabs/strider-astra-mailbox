import json,re,datetime
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'outputs'/'word-game'
before=json.loads((OUT/'before.json').read_text());after=json.loads((OUT/'after.json').read_text());practice=json.loads((OUT/'practice.json').read_text())
assert len(before)==len(after)==5 and len(practice)==6
assert [r['prompt'] for r in before]==[r['prompt'] for r in after]
leak=re.compile(r'supplied provenance|sender=|package=|[{}]|\[remembered',re.I)
checks=[]
for i,row in enumerate(after):
 r=row['result'];reply=r.get('reply','');tool=r.get('tool_result',{})
 route=(tool.get('tool')=='memory_query' and (tool.get('result') or {}).get('dialogue_act') in ('known','partial')) if i<3 else r.get('action')=='respond'
 checks.append(bool(r.get('ok') and route and reply and not leak.search(reply) and not re.search(r'\d+ persistent memories',reply) and "couldn't turn them" not in reply and "don't remember" not in reply))
summary=['Internal provenance and raw game JSON.','Internal provenance and raw game JSON.','Memory count instead of a game answer.','Memory count instead of acknowledgment.','Long acknowledgment with an unsupported claim about prior conversations.']
lines=['# Meaning Match: real-chat before and after','',f'Completed {datetime.datetime.now().astimezone().isoformat()}.','',
 '**Measured result:** '+str(sum(checks))+'/5 final probes met the tested routing, plain-language and acknowledgment criteria. The baseline had 0/5 fully satisfactory replies: two metadata dumps, two wrong memory-count responses, and one unsupported personal-history assertion. These are task-specific acceptance judgments, not a standardized intelligence score.','',
 'All five prompts were identical before and after. Every turn went through the production authenticated phone-app `/chat` endpoint and its normal MindLoop, reasoning, Judge and dispatcher. Different session IDs reduced within-session carryover; the real shared memory and ongoing Crafter records were not frozen.','',
 '| Probe | Before | After |','|---|---|---|']
for i,(b,a) in enumerate(zip(before,after)):
 lines.append('| '+b['prompt'].replace('|','\\|')+' | '+summary[i]+' | '+a['result'].get('reply','ERROR').replace('|','\\|').replace('\n',' ')+' |')
lines+=['','## Exact captured replies','']
for i,(b,a) in enumerate(zip(before,after),1):
 lines += [f'### {i}. {b["prompt"]}','','Before:','', '> '+b['result'].get('reply','ERROR').replace('\n','\n> '),'','After:','', '> '+a['result'].get('reply','ERROR').replace('\n','\n> '),'']
lines += ['## What is wired into ordinary chat','',
 '- The shared Meaning Match curriculum is read by the production intent classifier, disclosure handler and grounded memory-answer writer.',
 '- Personal disclosures receive a short acknowledgment based on the current message. They do not route to a memory count.',
 '- Named subjects outrank generic request words during recall. Storage wrappers are decoded before selection; original stored records remain intact.',
 '- Structured Crafter achievements become plain statements from their actual fields. They do not acquire invented chronology or causal learning. General prose notes use synthesis plus an evidence check; unsafe synthesis falls back without raw data.',
 '- Evidence and provenance stay available in diagnostic tool data, while the operator-facing reply stays conversational. The game itself sends practice through the live `/chat` path.',
 '', '## Validation and limits','',
 '- Eleven focused regression tests passed for wrapper decoding, positive/zero achievements, metadata-safe failure, unsupported summaries, failed reads, partial/conflicting knowledge, false personal history, invented chronology, legacy records, honest learning reviews and preserving recall mode across both live entry points.',
 '- Voice code/settings and six protected files match their saved pre-change hashes. No protected core or stored memories were directly edited. Normal chat appends its usual records.',
 '- A genuine memory-count control still returns a count: '+practice[5]['result'].get('reply','ERROR'),
 '- Development attempts exposed missing retrieval, overcautious fallbacks, wrong attribution and invented sequence. Those attempts were retained as intermediate records, not counted as final successes.',
 '- This is a curriculum, retrieval and response-generation improvement. No model weights were trained; five rehearsed probes do not demonstrate general language mastery or broad intelligence improvement.',
 '- Some replies remain repetitive, and broad questions may receive cautious partial answers. The live path still depends on the local model and available memory.',
 '', 'Raw captures: [before](before.json), [after](after.json), [practice](practice.json). Protected-file validation: [validation](validation.json).','']
(OUT/'before-after.md').write_text('\n'.join(lines),encoding='utf-8')
(OUT/'score.json').write_text(json.dumps({'checks':checks,'passed':sum(checks),'total':5,'criteria':'routing + no metadata/count deflection; naturalness and factual fidelity manually reviewed'},indent=2))
print(json.dumps({'passed':sum(checks),'total':5,'after':[r['result'].get('reply') for r in after]},indent=2))
