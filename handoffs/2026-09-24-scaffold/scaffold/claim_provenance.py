"""Validate explicit factual claims against supplied evidence, without certifying model assertions."""
import re

LABELS={'remembered','verified','inferred','speculative','unknown'}

def validate_claims(claims, memories, observations='', inference_context='', allow_speculative=False):
    if not isinstance(claims,list):return []
    memory_text='\n'.join(str(m.get('memory','')) for m in memories)
    output=[]
    for item in claims[:30]:
        if not isinstance(item,dict):continue
        text=str(item.get('text','')).strip()[:1800]
        if not text:continue
        provenance=item.get('provenance','unknown')
        evidence=str(item.get('evidence','')).strip()
        if provenance not in LABELS:provenance='unknown'
        corpus=memory_text if provenance=='remembered' else observations
        if provenance in ('remembered','verified') and (len(evidence)<8 or evidence.casefold() not in corpus.casefold()):
            provenance='unknown'
            text="I don't have evidence to establish that claim."
        if provenance=='inferred' and (len(evidence)<8 or evidence.casefold() not in (memory_text+'\n'+observations+'\n'+inference_context).casefold()):
            provenance='unknown'
            text="I don't have supporting evidence for that inference."
        if provenance=='speculative' and not allow_speculative:
            provenance='unknown'
            text="That is unknown from the available evidence."
        if provenance in ('inferred','speculative') and re.search(r'\d|[“”"]',text) and (not evidence or evidence.casefold() not in (memory_text+'\n'+observations).casefold()):
            provenance='unknown'
            text="The specific figure or quotation is unknown; I don't have supporting evidence."
        output.append(dict(text=text,provenance=provenance,evidence=evidence if provenance!='unknown' else ''))
    return output


def apply_response_evidence(action, claims, memories, observations='', raw_text='',
                            allow_speculative=False, *, intent='uncertain', auditor=None,
                            activity_observations=''):
    """Selectively remove unsupported assertions on all output tracks.
    The independent prose audit also covers empty formal claim lists.
    """
    if action.get('type') != 'respond':
        return
    from conversation_policy import units
    originals = [c for c in claims[:30] if isinstance(c,dict) and str(c.get('text','')).strip()] if isinstance(claims,list) else []
    checked = validate_claims(originals, memories, observations,
                              inference_context=raw_text, allow_speculative=allow_speculative)
    valid = [dict(c, valid=c['provenance'] != 'unknown') for c in checked]
    removed = []
    tracks = {k: str(action[k]) for k in ('content','show','say') if action.get(k) is not None}
    filtered, cache = {}, {}
    failed = False
    for key, text in tracks.items():
        if text in cache:
            filtered[key] = cache[text]
            continue
        parts = units(text)
        kept = []
        admission = False
        next_step = False
        removed_before = len(removed)
        try:
            if parts:
                if auditor is None:
                    raise ValueError('No prose audit available')
                verdicts = auditor(parts, valid, intent)
                if len(verdicts) != len(parts) or [v.get('index') for v in verdicts] != list(range(len(parts))):
                    raise ValueError('Incomplete audit')
                for part, verdict in zip(parts, verdicts):
                    kind = verdict.get('kind')
                    idx = verdict.get('claim_index', -1)
                    evidence = valid[idx] if type(idx) is int and 0 <= idx < len(valid) else None
                    if kind not in ('conversation', 'admission'):
                        residue = part
                        for original, result in zip(originals, checked):
                            bad = str(original.get('text','')).strip()
                            if result['provenance'] == 'unknown' and result['text'] != bad[:1800] and bad:
                                residue = re.sub(re.escape(bad), '', residue, flags=re.I)
                        if residue != part:
                            removed.append(part.strip())
                            if residue.strip():
                                residual = {'type': 'respond', 'content': residue.strip()}
                                apply_response_evidence(residual, [], memories, observations, raw_text,
                                    allow_speculative, intent=intent, auditor=auditor,
                                    activity_observations=activity_observations)
                                review = residual.get('evidence_review', {})
                                if not review.get('audit_failed') and not review.get('removed_claims'):
                                    kept.append(residual['content'])
                            continue
                    keep = kind in ('conversation','admission','general_fact')
                    if kind == 'supported_fact':
                        keep = bool(evidence and evidence['valid'])
                    # Exact source-backed assertions do not depend on the model
                    # correctly selecting an array index. Activity still wins.
                    if kind != 'activity' and not verdict.get('real_world_activity'):
                        for claim in valid:
                            corpus = '\\n'.join(str(m.get('memory','')) for m in memories) if claim['provenance'] == 'remembered' else observations
                            if (claim['provenance'] in ('verified','remembered')
                                and claim['valid'] and part.strip().casefold() == claim['text'].casefold()
                                and claim['text'].casefold() in corpus.casefold()):
                                keep = True
                                break
                    if kind == 'activity':
                        # Only fresh tool evidence establishes activity; not a user's
                        # assertion, inferred/remembered claim or capability aggregate.
                        keep = bool(evidence and evidence['provenance'] == 'verified'
                            and len(evidence['evidence']) >= 8
                            and evidence['evidence'].casefold() in activity_observations.casefold())
                    if keep:
                        kept.append(part)
                        admission = admission or kind == 'admission'
                        next_step = next_step or verdict.get('offers_next_step') is True
                    else:
                        removed.append(part.strip())
            result = ''.join(kept).strip()
            if result and (admission or action.get('dialogue_act') in ('unknown','uncertain','partial','inability')) and not next_step:
                result += " Can you fill me in, or should we check together?"
            elif result and len(removed) > removed_before and not admission:
                result += " I don't know the missing part yet. Want me to check?"
            if result and action.get('dialogue_act') == 'guess':
                result = "My guess: " + result
        except Exception:
            failed = True
            result = ''
        if not result:
            action['dialogue_act'] = 'unknown'
            result = ("Hey, I'm here. What's on your mind?" if intent == 'social' else
                "I don't know that yet. Want me to check, or can you fill me in?")
        cache[text] = result
        filtered[key] = result
    action.update(filtered)
    action.setdefault('content', "I don't know that yet. Want me to check, or can you fill me in?")
    action.setdefault('show', action['content'])
    action.setdefault('say', action['content'])
    action['claims'] = [c for c in checked if c['provenance'] != 'unknown' and c['text'] in action['content']]
    action['evidence_review'] = {'intent': intent, 'removed_claims': len(removed), 'audit_failed': failed}
