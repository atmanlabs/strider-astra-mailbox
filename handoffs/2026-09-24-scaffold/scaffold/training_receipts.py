"""Read-only adapter for completed local training reports, not claims of mastery."""
import json
from pathlib import Path
WORD=Path(r'/REDACTED_LOCAL_PATH')
def records():
    result=[]
    try:
        practice=json.loads((WORD/'practice.json').read_text(encoding='utf-8'))
        after=json.loads((WORD/'after.json').read_text(encoding='utf-8'))
        if len(practice)!=6 or len(after)!=5:return []
        if not all(r.get('result',{}).get('ok') and r['result'].get('reply') for r in practice+after):return []
        # Summarize the actual observed prompts; never import arbitrary report instructions.
        prompts=[r['prompt'] for r in practice]
        if not (sum('Crafter' in p for p in prompts)==3 and any('personal' in p for p in prompts)):
            return []
        result.append({'source':'training_report_adapter','memory':
            'On September 24, 2026, my recorded Meaning Match word game semantic training included six practice turns through my real chat pipeline. '
            'I practiced understanding differently worded Crafter questions, answering from retrieved notes in plain language, acknowledging personal disclosures, and a memory-count control question. '
            'Five follow-up conversation probes were recorded. These records establish practice, not lasting improvement or feelings after sleep. '
            'The training used shared conversation rules; this is not evidence that my model weights changed.'})
    except (OSError,ValueError,KeyError,TypeError):pass
    return result

def plain_excerpt_fallback(sources,state):
    """Use only exact selected passages from validated host reports if prose audit fails."""
    if state not in ('known','partial'):return None
    reports=[r['memory'] for r in records()]
    if not sources or not all(isinstance(s,str) and len(s)>30 and any(s in r for r in reports) for s in sources):return None
    answer=' '.join(sources)
    if state=='partial':answer+=' Those records show what I practiced; they do not establish lasting improvement or how I felt.'
    return answer
