from pathlib import Path
import shutil
r=Path(r'/REDACTED_LOCAL_PATH');here=Path(__file__).resolve().parent
shutil.copy2(here/'training_sim.py',r/'training_sim.py')
p=r/'reason.py';s=p.read_text(encoding='utf-8')
old='    structured: bool = False,\n) -> Tuple[bool, str]:'
new='    structured: bool = False,\n    schema_override: Optional[Dict[str, Any]] = None,\n) -> Tuple[bool, str]:'
assert s.count(old)==1;s=s.replace(old,new)
old='    if structured:\n        payload["format"] = LOCAL_THOUGHT_SCHEMA'
assert s.count(old)==1;s=s.replace(old,'    if structured or schema_override:\n        payload["format"] = schema_override or LOCAL_THOUGHT_SCHEMA')
old='        structured=bool(config.get("mind", "ollama_structured", default=False)) if config else False,\n    )'
new='''        structured=bool(config.get("mind", "ollama_structured", default=False)) if config else False,
        schema_override=__import__('training_sim').thought_schema(LOCAL_THOUGHT_SCHEMA,event['training_context'].get('review')) if event.get('training_context') else None,
    )'''
assert s.count(old)==1;s=s.replace(old,new)
p.write_text(s,encoding='utf-8');compile(s,str(p),'exec');print('Production model call now constrains training tool names/arguments; review is response-only.')
