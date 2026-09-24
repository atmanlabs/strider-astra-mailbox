import json,sys,time,urllib.request
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'outputs'/'word-game'
PROBES=[
 'What do your notes say about playing Crafter?',
 'Tell me what you remember from the Crafter sandbox.',
 'Explain what you learned in Crafter in plain everyday words.',
 'I want you to understand me when I tell you about myself.',
 'Being understood matters to me when I share something personal.'
]
token=json.loads(Path(r'/REDACTED_LOCAL_PATH').read_text())['token']
label=sys.argv[1];rows=[]
for attempt in range(30):
 try:
  with urllib.request.urlopen('http://127.0.0.1:18790/health',timeout=3) as r:
   if json.load(r).get('status')=='online':break
 except OSError:pass
 time.sleep(2)
else:raise RuntimeError('Chat relay did not become ready')
if label=='practice':
 PROBES=['What happened during your Crafter practice?', 'Walk me through your notes from the Crafter game.', 'In simple language, what do the Crafter records tell you?', 'I care about being understood when I share personal things.', 'It matters to me that you listen when I tell you about myself.', 'How many memories are you holding right now?']
for i,prompt in enumerate(PROBES):
 if Path(__file__).with_name('stop').exists():break
 body={'text':prompt,'source':'phone_app','session_id':f'semantic-evaluation-{label}-{i}'}
 req=urllib.request.Request('http://127.0.0.1:18790/chat',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+token})
 start=time.time()
 try:
  with urllib.request.urlopen(req,timeout=180) as r: result=json.load(r)
 except Exception as e:result={'error':str(e)}
 rows.append({'prompt':prompt,'elapsed':round(time.time()-start,2),'result':result})
 (OUT/(label+'.json')).write_text(json.dumps(rows,indent=2),encoding='utf-8')
 print(json.dumps({'probe':i+1,'reply':result.get('reply'),'action':result.get('action'),'error':result.get('error')}),flush=True)
