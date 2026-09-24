"""Jarvis's isolated Crafter controller: local actions, measured outcomes, bounded overnight run."""
import collections, io, json, math, os, random, secrets, threading, time, urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import crafter
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parents[1]/'outputs'/'crafter'
OUT.mkdir(parents=True,exist_ok=True)
STATE=ROOT/'learning.json'
STOP=ROOT/'stop'
PAUSE=ROOT/'pause'
EXO=Path(r'/REDACTED_LOCAL_PATH')
PORT=18924
snapshot={};frame=b'';lock=threading.Lock()
GOALS=['explore','gather','craft','survive']
directions=[(-1,0,'move_left'),(1,0,'move_right'),(0,-1,'move_up'),(0,1,'move_down')]

def atomic(path,obj):
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,indent=2),encoding='utf-8');os.replace(tmp,path)

def http(url,data=None,token=None,timeout=8):
 req=urllib.request.Request(url,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json',**({'Authorization':'Bearer '+token} if token else {})})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)

def remember(summary,episode):
 try:
  token=(ROOT/'memory-token').read_text().strip()
  payload={'package_id':f'crafter-{RUN_ID}-{episode}','from':'jarvis-crafter','date':time.strftime('%Y-%m-%d'),'requested_action':'note',
   'claims':[{'content':'Crafter game experience only: '+summary,'provenance':'verified','evidence':str(OUT/'episodes.jsonl')}]}
  receipt=http('http://127.0.0.1:18790/packages',payload,token,20)
  atomic(OUT/'memory-receipt.json',receipt)
 except Exception as e:atomic(OUT/'memory-receipt.json',{'state':'pending','reason':str(e)[:200]})

class Controller:
 def __init__(self,seed=73):
  self.env=crafter.Env(seed=seed,size=(360,360),length=2400)
  self.learn=json.loads(STATE.read_text()) if STATE.exists() else {'episodes':0,'steps':0,'goals':{g:[0,0.] for g in GOALS},'unlocked':[],'moved':0,'changed_inventory':0}
  self.goal='gather';self.goal_steps=0;self.goal_reward=0;self.recommendation='gather';self.reason='Begin with resources and basic tools.'
  self.memory={};self.visited=collections.Counter();self.reset()
 def reset(self):
  self.env.reset();_,_,_,self.info=self.env.step(0);self.memory={};self.visited=collections.Counter();self.ep_steps=0;self.ep_reward=0;self.ep_start=time.time()
 def observe(self):
  x,y=map(int,self.info['player_pos'])
  for a in range(max(0,x-4),min(64,x+5)):
   for b in range(max(0,y-3),min(64,y+4)):
    terrain,obj=self.env._world[(a,b)]
    self.memory[(a,b)]=(terrain,type(obj).__name__ if obj else '')
  self.visited[(x,y)]+=1
  return (x,y)
 def route(self,pos,targets):
  queue=collections.deque([(pos,None)]);seen={pos}
  while queue:
   here,first=queue.popleft()
   for dx,dy,act in directions:
    nxt=(here[0]+dx,here[1]+dy)
    if nxt not in self.memory:continue
    terrain,obj=self.memory[nxt]
    if terrain in targets or obj.lower() in targets:
     if here==pos:
      if tuple(self.env._player.facing)==(dx,dy):return 'do'
      return act
     return first
    if nxt not in seen and terrain in ('grass','sand','path') and obj in ('','Player'):
     seen.add(nxt);queue.append((nxt,first or act))
  return None
 def explore(self,pos):
  opts=[]
  for dx,dy,act in directions:
   nxt=(pos[0]+dx,pos[1]+dy);terrain,obj=self.memory.get(nxt,('unknown',''))
   if terrain in ('grass','sand','path') and not obj:opts.append((self.visited[nxt]+random.random()*.8,act))
  return min(opts)[1] if opts else random.choice([x[2] for x in directions])
 def action(self):
  pos=self.observe();inv=self.info['inventory']
  if inv['energy']<2:return 'sleep'
  if inv['drink']<4:
   a=self.route(pos,{'water'})
   if a:return a
  if inv['food']<4:
   a=self.route(pos,{'cow','plant'})
   if a:return a
  for dx,dy,act in directions:
   obj=self.memory.get((pos[0]+dx,pos[1]+dy),('',''))[1]
   if obj in ('Zombie','Skeleton'):return 'do' if tuple(self.env._player.facing)==(dx,dy) else act
  nearby,_=self.env._world.nearby(pos,1)
  if self.goal!='explore' or self.ep_steps%4==0:
   if 'table' in nearby:
    for item in ('wood_pickaxe','wood_sword','stone_pickaxe','stone_sword','iron_pickaxe'):
     spec=crafter.constants.make[item]
     if not inv[item] and all(inv[k]>=v for k,v in spec['uses'].items()) and all(k in nearby for k in spec['nearby']):return 'make_'+item
   if inv['wood']>=3 and 'table' not in nearby and not inv['wood_pickaxe']:
    target=tuple(np.array(pos)+self.env._player.facing)
    if self.memory.get(target,('',None))[0] in ('grass','sand','path') and not self.memory[target][1]:return 'place_table'
   targets={'tree'} if inv['wood']<5 else ({'stone'} if inv['wood_pickaxe'] and inv['stone']<5 else {'coal','iron'} if inv['stone_pickaxe'] else {'tree'})
   a=self.route(pos,targets)
   if a:return a
  return self.explore(pos)
 def step(self):
  if self.goal_steps>=80:
   stat=self.learn['goals'][self.goal];stat[0]+=1;stat[1]+=(self.goal_reward-stat[1])/stat[0]
   if random.random()<.25:self.goal=random.choice(GOALS)
   else:self.goal=max(GOALS,key=lambda g:self.learn['goals'][g][1]+math.sqrt(2*math.log(2+sum(v[0] for v in self.learn['goals'].values()))/(1+self.learn['goals'][g][0]))+(.3 if g==self.recommendation else 0))
   self.goal_steps=0;self.goal_reward=0
  action=self.action();old=self.info;_,reward,done,self.info=self.env.step(self.env.action_names.index(action))
  moved=tuple(old['player_pos'])!=tuple(self.info['player_pos'])
  changed=any(old['inventory'][k]!=self.info['inventory'][k] for k in ('wood','stone','coal','iron','wood_pickaxe','wood_sword','stone_pickaxe'))
  self.learn['steps']+=1;self.learn['moved']+=int(moved);self.learn['changed_inventory']+=int(changed)
  self.ep_steps+=1;self.ep_reward+=reward;self.goal_steps+=1;self.goal_reward+=reward+.01*int(moved and self.visited[tuple(self.info['player_pos'])]==0)
  for name,value in self.info['achievements'].items():
   if value and name not in self.learn['unlocked']:self.learn['unlocked'].append(name)
  if self.ep_steps%20==0:atomic(STATE,self.learn)
  return action,done
 def finish(self):
  self.learn['episodes']+=1
  record={'episode':self.learn['episodes'],'steps':self.ep_steps,'reward':round(self.ep_reward,3),'achievements':{k:v for k,v in self.info['achievements'].items() if v},'ended':time.strftime('%Y-%m-%d %H:%M:%S')}
  with (OUT/'episodes.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
  atomic(STATE,self.learn)
  if self.learn['episodes']%3==1:threading.Thread(target=remember,args=(json.dumps(record),self.learn['episodes']),daemon=True).start()
  self.reset()

def planner(controller):
 while time.time()<END and not STOP.exists():
  try:
   health=http('http://127.0.0.1:18790/health')
   voice=EXO/'voice.activity'
   if not health.get('governor_active') and not (voice.exists() and time.time()-voice.stat().st_mtime<60):
    prompt='You are JARVIS choosing a goal in your private Crafter sandbox. Return JSON with goal (explore, gather, craft, survive) and one short reason. Only game decisions; no external actions. Current measured game state: '+json.dumps(snapshot)
    result=http('http://127.0.0.1:11434/api/generate',{'model':'qwen3.5:4b','prompt':prompt,'stream':False,'think':False,'format':'json','options':{'num_predict':100,'num_ctx':2048}},timeout=60)
    decision=json.loads(result['response'])
    if decision.get('goal') in GOALS:
     controller.recommendation=decision['goal'];controller.reason=str(decision.get('reason',''))[:300]
     atomic(OUT/'last-jarvis-decision.json',{'at':time.time(),**decision})
  except Exception as e:atomic(OUT/'planner-status.json',{'reason':str(e)[:200],'fallback':'Learned game controller continues; no completion claim'})
  for _ in range(300):
   if STOP.exists() or time.time()>=END:return
   time.sleep(1)

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path.startswith('/state'):data=json.dumps(snapshot).encode();kind='application/json'
  elif self.path.startswith('/frame'):data=frame;kind='image/png'
  elif self.path=='/':data=(ROOT/'index.html').read_bytes();kind='text/html'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
 def do_POST(self):
  if self.headers.get('Origin')!=f'http://127.0.0.1:{PORT}':self.send_error(403);return
  if self.path=='/pause':PAUSE.touch()
  elif self.path=='/resume':PAUSE.unlink(missing_ok=True)
  elif self.path=='/stop':STOP.touch()
  else:self.send_error(404);return
  self.send_response(204);self.end_headers()

RUN_ID=time.strftime('%Y%m%d-%H%M%S');END=time.time()+8*3600
def main():
 global snapshot,frame
 server=ThreadingHTTPServer(('127.0.0.1',PORT),Handler) # Single instance; loopback only.
 threading.Thread(target=server.serve_forever,daemon=True).start()
 c=Controller();threading.Thread(target=planner,args=(c,),daemon=True).start()
 last='starting'
 while time.time()<END and not STOP.exists():
  if not PAUSE.exists():
   last,done=c.step()
   if done:c.finish()
  snapshot={'running':True,'paused':PAUSE.exists(),'game':'Crafter','goal':c.goal,'jarvis_goal':c.recommendation,'jarvis_reason':c.reason,'action':last,'position':[int(x) for x in c.info['player_pos']],'inventory':c.info['inventory'],'episode':c.learn['episodes']+1,'episode_steps':c.ep_steps,'total_steps':c.learn['steps'],'verified_moves':c.learn['moved'],'inventory_changes':c.learn['changed_inventory'],'achievements':c.learn['unlocked'],'goal_learning':c.learn['goals'],'stops_at':time.strftime('%H:%M',time.localtime(END))}
  buf=io.BytesIO();Image.fromarray(c.env.render()).save(buf,format='PNG');frame=buf.getvalue()
  if c.ep_steps%10==0:
   atomic(OUT/'status.json',snapshot);(OUT/'latest.png').write_bytes(frame)
  time.sleep(.35)
 snapshot['running']=False;atomic(OUT/'status.json',snapshot);atomic(STATE,c.learn)
 remember('Overnight session finished. '+json.dumps(snapshot),str(c.learn['episodes'])+'-final')
 (OUT/'morning-report.md').write_text('# Jarvis — Crafter practice\n\n'+json.dumps(snapshot,indent=2)+'\n\nGame-specific controller statistics and memories; no claim of general intelligence improvement.\n',encoding='utf-8')
 server.shutdown()
if __name__=='__main__':main()
