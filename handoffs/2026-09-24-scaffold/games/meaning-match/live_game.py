"""All word-game rounds use the authenticated production /chat path."""
import json,subprocess,sys,threading,time,urllib.request
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parent;OUT=ROOT.parents[1]/'outputs'/'word-game'
STATE={'phase':'ready','pipeline':'phone_app → /chat → MindLoop → reason → shared semantic curriculum'}
def run():
 STATE['phase']='waiting for chat'
 for attempt in range(30):
  try:
   with urllib.request.urlopen('http://127.0.0.1:18790/health',timeout=3) as r:
    if json.load(r).get('status')=='online':break
  except OSError:pass
  time.sleep(2)
 else:STATE['phase']='needs_attention';return
 for phase in ('practice','after'):
  if (ROOT/'stop').exists():STATE['phase']='stopped';return
  STATE['phase']=phase
  process=subprocess.run([sys.executable,'-u',str(ROOT/'probes.py'),phase])
  if process.returncode:STATE['phase']='needs_attention';return
  if (ROOT/'stop').exists():STATE['phase']='stopped';return
 STATE['phase']='complete'
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path=='/state':
   data=dict(STATE)
   for phase in ('before','practice','after'):
    try:data[phase]=json.loads((OUT/(phase+'.json')).read_text(encoding='utf-8'))
    except (OSError,ValueError):data[phase]=[]
   body=json.dumps(data).encode();kind='application/json'
  elif self.path=='/':body=(ROOT/'live.html').read_bytes();kind='text/html; charset=utf-8'
  else:self.send_error(404);return
  self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(body)
 def do_POST(self):
  if self.path!='/stop' or self.headers.get('Origin')!='http://127.0.0.1:18925':self.send_error(403);return
  (ROOT/'stop').touch();self.send_response(204);self.end_headers()
if __name__=='__main__':
 server=ThreadingHTTPServer(('127.0.0.1',18925),Handler)
 if '--review-only' in sys.argv:STATE['phase']='review'
 else:threading.Thread(target=run,daemon=True).start()
 server.serve_forever()
