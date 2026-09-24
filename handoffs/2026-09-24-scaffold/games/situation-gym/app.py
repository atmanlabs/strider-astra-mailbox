"""JARVIS Situation Gym — native Windows desktop app and headless run driver."""
import json,os,sys,time,threading,queue,urllib.request,urllib.error,uuid
from pathlib import Path
ROOT=Path.home()/'Documents'/'jarvis-training';RUNS=ROOT/'runs';ROOT.mkdir(parents=True,exist_ok=True);RUNS.mkdir(exist_ok=True)
CREDENTIAL=Path.home()/'Documents'/'PRIVATE_DATA_REDACTED'/'phone-credential.json'
SCENARIOS={'PC & phone equipment errand':'pc_errand','Repair drop-off around an appointment':'calendar_conflict'}
def api(body):
 token=json.loads(CREDENTIAL.read_text(encoding='utf-8'))['token']
 req=urllib.request.Request('http://127.0.0.1:18790/chat',data=json.dumps({'text':'Scenario gym turn','source':'phone_app',**body}).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+token})
 with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
def run(scenario,seed,notify,stop):
 ident=None;last=None
 try:
  notify('Connecting to the local JARVIS relay…')
  for attempt in range(30):
   try:
    with urllib.request.urlopen('http://127.0.0.1:18790/health',timeout=3) as response:
     if json.load(response).get('status')=='online':break
   except OSError:pass
   if stop.wait(2):return None
  else:raise RuntimeError('JARVIS chat relay is offline. Start JARVIS, then try again.')
  for step in range(22):
   if stop.is_set():
    if ident:
     try:api({'training':{'command':'stop','id':ident}})
     except Exception:pass
    notify('Stopped before the next turn. The trace is preserved.');return ident
   request={'command':'start','scenario':scenario,'seed':seed} if ident is None else {'command':'step','id':ident}
   result=api({'training':request});last=result.get('training')
   if not last:raise RuntimeError('Live relay did not return a training trace. No fake run is substituted.')
   ident=last['id'];notify(f'Round {last["turn"]} · score {last["score"]["total"]}/100\nJARVIS: {result.get("reply","")}\nWorld: {last["world"]["npc"]}',last)
   if last['score']['win'] and last['world']['proposal'] and last['score']['criteria']['reviewed_status']:break
   time.sleep(.5)
  if stop.is_set():notify('Stopped; no automatic review.');return ident
  notify('JARVIS is reviewing his own recorded trace. The real Judge will decide whether to store his lesson.')
  result=api({'training':{'command':'review','id':ident}});last=result['training']
  receipt=last.get('memory_receipt') or {}
  title='Complete' if receipt.get('imprinted') else 'Run finished — lesson storage needs attention'
  notify(f'{title} · process score {last["score"]["total"]}/100 · win: {last["score"]["win"]}\nLesson: {result.get("reply","")}\nReal PSC imprint: {receipt.get("imprinted",False)}',last)
  return ident
 except Exception as error:
  failure={'run_id':ident,'error':str(error),'time':time.time(),'no_synthetic_fallback':True}
  (ROOT/'last-error.json').write_text(json.dumps(failure,indent=2))
  failed_folder=RUNS/(ident or ('client-error-'+uuid.uuid4().hex));failed_folder.mkdir(exist_ok=True)
  (failed_folder/'client-error.json').write_text(json.dumps(failure,indent=2))
  notify('Run needs attention: '+str(error));return ident

def gui(smoke=False):
 import tkinter as tk
 from tkinter import ttk,messagebox,filedialog
 window=tk.Tk();window.title('JARVIS Situation Gym');window.geometry('1080x780');window.minsize(850,620);window.configure(bg='#111a2b')
 style=ttk.Style();style.theme_use('clam');style.configure('TFrame',background='#111a2b');style.configure('TLabel',background='#111a2b',foreground='#edf3ff');style.configure('TButton',padding=9);style.configure('TNotebook',background='#111a2b');style.configure('TNotebook.Tab',padding=[14,8])
 heading=ttk.Frame(window,padding=20);heading.pack(fill='x');ttk.Label(heading,text='JARVIS  /  SITUATION GYM',font=('Segoe UI',22,'bold')).pack(anchor='w');ttk.Label(heading,text='Real reasoning. Simulated consequences. Evidence you can inspect.',font=('Segoe UI',11)).pack(anchor='w',pady=(5,0))
 tabs=ttk.Notebook(window);tabs.pack(fill='both',expand=True,padx=20,pady=8)
 gym=ttk.Frame(tabs,padding=16);profiletab=ttk.Frame(tabs,padding=16);history=ttk.Frame(tabs,padding=16)
 tabs.add(gym,text='Play a situation');tabs.add(profiletab,text='Operator’s context');tabs.add(history,text='Runs & Astra reviews')
 row=ttk.Frame(gym);row.pack(fill='x');choice=tk.StringVar(value=list(SCENARIOS)[0]);ttk.Combobox(row,textvariable=choice,values=list(SCENARIOS),state='readonly',width=43).pack(side='left');ttk.Label(row,text='  Variation seed').pack(side='left');seed=tk.StringVar(value='73');ttk.Entry(row,textvariable=seed,width=8).pack(side='left')
 status=tk.StringVar(value='Ready. JARVIS must already be running on this PC.');ttk.Label(gym,textvariable=status,wraplength=950).pack(anchor='w',pady=12)
 transcript=tk.Text(gym,wrap='word',bg='#19263c',fg='#edf3ff',insertbackground='white',font=('Segoe UI',11),relief='flat',padx=16,pady=12);transcript.pack(fill='both',expand=True)
 events=queue.Queue();stop=threading.Event();worker=None;last_id=None
 def notify(text,data=None):events.put((text,data))
 def start_run():
  nonlocal worker
  if worker and worker.is_alive():return
  try:value=int(seed.get())
  except ValueError:messagebox.showerror('Seed','Use a whole number.');return
  stop.clear();transcript.delete('1.0','end');status.set('Running through JARVIS’s live chat pipeline…');startbutton.configure(state='disabled')
  worker=threading.Thread(target=run,args=(SCENARIOS[choice.get()],value,notify,stop),daemon=True);worker.start()
 def poll():
  nonlocal last_id
  while not events.empty():
   text,data=events.get();transcript.insert('end',text+'\n\n');transcript.see('end')
   if data:last_id=data['id'];status.set(f'Run {last_id[:8]} · {data["phase"]} · score {data["score"]["total"]}/100')
  if worker and not worker.is_alive():startbutton.configure(state='normal')
  window.after(250,poll)
 buttons=ttk.Frame(gym);buttons.pack(fill='x',pady=(12,0));startbutton=ttk.Button(buttons,text='Start a run',command=start_run);startbutton.pack(side='left');ttk.Button(buttons,text='Stop after this turn',command=stop.set).pack(side='left',padx=8);ttk.Button(buttons,text='Open this run',command=lambda:os.startfile(str(RUNS/last_id if last_id else RUNS))).pack(side='right')
 ttk.Label(profiletab,text='Real context is optional. Times, service names and prices in the starting scenarios are fictional.\nNothing is booked on your real calendar. Save only details you want used as scenario context.',wraplength=950).pack(anchor='w',pady=(0,15))
 ttk.Label(profiletab,text='Typical errands, preferences and constraints').pack(anchor='w');profiletext=tk.Text(profiletab,height=10,font=('Segoe UI',11),wrap='word');profiletext.pack(fill='x',pady=8)
 try:profile=json.loads((ROOT/'profile.json').read_text(encoding='utf-8'))
 except (OSError,ValueError):profile={'notes':'Confirmed context: Operator uses JARVIS on his PC and phone and wants better assistant behavior. No real appointments or routine errands supplied yet.','source':'conversation; schedule unconfirmed'}
 profiletext.insert('1.0',profile.get('notes',''))
 def save_profile():
  profile['notes']=profiletext.get('1.0','end').strip()[:5000];profile['source']='Operator edited in Situation Gym';(ROOT/'profile.json').write_text(json.dumps(profile,indent=2),encoding='utf-8');messagebox.showinfo('Saved','Context saved for future scenarios. No real calendar was changed.')
 def import_calendar():
  path=filedialog.askopenfilename(title='Read a calendar export',filetypes=[('Calendar export','*.ics')])
  if not path:return
  text=Path(path).read_text(encoding='utf-8-sig');events=[]
  for block in text.split('BEGIN:VEVENT')[1:]:
   item={}
   for line in block.split('END:VEVENT')[0].splitlines():
    if ':' in line:
     key,value=line.split(':',1)
     if key.split(';')[0] in ('SUMMARY','DTSTART','DTEND'):item[key.split(';')[0]]=value
   if item:events.append(item)
  profile['calendar_reference']=events[:50];profiletext.insert('end','\nCalendar reference (read-only):\n'+json.dumps(events[:12],indent=2));save_profile()
 ttk.Button(profiletab,text='Save context',command=save_profile).pack(anchor='w',pady=8);ttk.Button(profiletab,text='Import calendar reference (.ics)',command=import_calendar).pack(anchor='w')
 ttk.Label(history,text='Every run saves report.md, report.json, world.json and an append-only trace.jsonl.\nThe trace records actual input, intent, proposed actions, Judge verdicts, tool outcomes and memory receipt.\nAstra’s daily review is separate from this desktop app and reads these files.',wraplength=950).pack(anchor='w',pady=12)
 ttk.Button(history,text='Open all runs',command=lambda:os.startfile(str(RUNS))).pack(anchor='w',pady=6)
 reviews=ROOT/'reviews';reviews.mkdir(exist_ok=True);ttk.Button(history,text='Open Astra reviews',command=lambda:os.startfile(str(reviews))).pack(anchor='w',pady=6)
 ttk.Label(history,text=str(RUNS),wraplength=900).pack(anchor='w',pady=20)
 def close():
  if worker and worker.is_alive():
   if not messagebox.askyesno('Stop run?','Stop after the current answer and close?'):return
   stop.set();status.set('Finishing the current turn before closing…')
   def wait_close():
    if worker.is_alive():window.after(300,wait_close)
    else:window.destroy()
   wait_close()
  else:window.destroy()
 window.protocol('WM_DELETE_WINDOW',close);poll()
 if smoke:
  def check_ui():
   window.update_idletasks()
   (ROOT/'ui-smoke.json').write_text(json.dumps({'title':window.title(),'tabs':len(tabs.tabs()),'width':window.winfo_width(),'height':window.winfo_height(),'start_button':startbutton.cget('text'),'frozen':bool(getattr(sys,'frozen',False))},indent=2))
   window.destroy()
  window.after(500,check_ui)
 window.mainloop()
if __name__=='__main__':
 if '--demo' in sys.argv:
  ident=run('pc_errand',73,lambda text,data=None:print(text,flush=True),threading.Event());print('RUN_ID='+str(ident),flush=True)
 else:gui('--ui-smoke' in sys.argv)
