import sys,json,time,urllib.request
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parent))
from app import api
for _ in range(30):
 try:
  with urllib.request.urlopen('http://127.0.0.1:18790/health',timeout=3) as r:
   if json.load(r).get('status')=='online':break
 except OSError:pass
 time.sleep(2)
result=api({'training':{'id':sys.argv[1],'command':'review'}})
print(json.dumps({'reply':result.get('reply'),'training':result.get('training')},indent=2))
