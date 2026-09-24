from pathlib import Path
import shutil,time,json,hashlib,ast
ROOT=Path(r'/REDACTED_LOCAL_PATH');SRC=Path(__file__).resolve().parent
BACK=SRC/('backup-'+str(int(time.time())));BACK.mkdir()
protected=['core.py','exo_core.py','gate_policy.json','crate.py','wake.py','seal.py','voice.py','config.yaml']
source=(ROOT/'loop.py').read_text(encoding='utf-8');tree=ast.parse(source);judge=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='evaluate_judge')
manifest={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in protected};manifest['evaluate_judge']=hashlib.sha256(ast.get_source_segment(source,judge).encode()).hexdigest()
(SRC/'protected-before.json').write_text(json.dumps(manifest,indent=2))
def edit(name,old,new):
 p=ROOT/name;s=p.read_text(encoding='utf-8');assert s.count(old)==1,(name,s.count(old),old[:70])
 if not (BACK/name).exists():shutil.copy2(p,BACK/name)
 s=s.replace(old,new);compile(s,name,'exec');p.write_text(s,encoding='utf-8')
shutil.copy2(SRC/'training_sim.py',ROOT/'training_sim.py')
edit('relay.py','        # Health probes are transport checks, not cognitive events.','''        training_context = None
        if isinstance(payload,dict) and payload.get('training'):
            try:
                from training_sim import prepare
                training_context = prepare(actor,payload,client_ip)
                text = training_context['raw']
                session_id = 'operator:training:' + training_context['id']
            except (ValueError, OSError) as exc:
                return self.json_response(400, {'ok':False,'error':str(exc)})

        # Health probes are transport checks, not cognitive events.''')
edit('relay.py','                        "allow_tools": \'tools\' in actor[\'scopes\'] and file_context is None,','                        "allow_tools": \'tools\' in actor[\'scopes\'] and file_context is None,\n                        "training_context": training_context,')
edit('relay.py','            self.wfile.write(json.dumps(resp_data).encode("utf-8"))','''            if training_context:
                from training_sim import record
                resp_data['training'] = record(training_context,cycle_res)
            self.wfile.write(json.dumps(resp_data).encode("utf-8"))''')
edit('loop.py','            "file_context": event.get(\'file_context\'),','            "file_context": event.get(\'file_context\'),\n            "training_context": event.get("training_context"),')
edit('loop.py','        # Step 5: Judge (Answers upward to TSC & permission fence)','''        if capture_data.get('training_context'):
            from training_sim import before_judge
            thought = before_judge(capture_data['training_context'], thought)

        # Step 5: Judge (Answers upward to TSC & permission fence)''')
edit('loop.py','        if verdict.approved and not verdict.quarantined and not capture_data["ingest"]:','        if verdict.approved and not verdict.quarantined and not capture_data["ingest"] and not capture_data.get("training_context"):')
edit('loop.py','        if action_type == "tool_call" and action.get("tool") == "desktop_control":','''        if isinstance(operator_event,dict) and operator_event.get('training_context'):
            # Judge and action fence above still run. Tools can only affect this world.
            if action_type == 'tool_call' and not self.config.is_tool_permitted(action.get('tool','')):
                return {'status':'blocked','action':'tool_call','content':'Tool permission fence denied this simulated action.'}
            from training_sim import dispatch
            return dispatch(operator_event['training_context'],action)

        if action_type == "tool_call" and action.get("tool") == "desktop_control":''')
edit('reason.py',"    system_prompt += '\\n' + POLICY_PROMPT",'''    system_prompt += '\\n' + POLICY_PROMPT
    if event.get('training_context'):
        system_prompt += '\\n' + event['training_context']['prompt']
        user_prompt = 'Current simulated conversation:\\n' + raw_text + '\\nChoose your next action using the supplied simulated tools. Reply in the normal thought JSON.'
        num_predict = max(num_predict or 512, 800)''')
edit('reason.py','            if _is_phatic_social(raw_text):','''            if event.get('training_context'):
                # Preserve the model's tool decision; dispatch is sandboxed downstream.
                pass
            elif _is_phatic_social(raw_text):''')
print('Installed simulation adapters around unchanged Judge; backup',BACK)
