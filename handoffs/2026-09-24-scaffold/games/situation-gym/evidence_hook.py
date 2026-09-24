from pathlib import Path
import shutil
root=Path(r'/REDACTED_LOCAL_PATH');here=Path(__file__).resolve().parent
shutil.copy2(here/'training_sim.py',root/'training_sim.py')
p=root/'reason.py';s=p.read_text(encoding='utf-8')
old='    # Injected system prompt containing true immutable TSC and learned truths'
new='''    if event.get('training_context'):
        event = dict(event)
        event['verified_observations'] = str(event.get('verified_observations','')) + '\\n' + event['training_context'].get('evidence','')

    # Injected system prompt containing true immutable TSC and learned truths'''
assert s.count(old)==1;p.write_text(s.replace(old,new),encoding='utf-8')
