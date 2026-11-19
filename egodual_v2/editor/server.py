#!/usr/bin/env python3
"""Local EgoDual editor. Original annotations are always read-only."""
import argparse, copy, datetime, hashlib, json, math, os, re, threading, tempfile
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from progress_dashboard import collect as collect_progress
ROOT=Path(__file__).resolve().parent.parent
PROXIES=ROOT.parent/'proxies'
LOCK=threading.RLock()
ID=re.compile(r'^[0-9a-f]{16}$')
FINE_FIELDS={'summary','verb','object','tool','target','hands','in_hand_at_end','type','ambiguous','boundary_note','confidence','notes'}
def ident(v):
 if not isinstance(v,str) or not ID.fullmatch(v): raise ValueError('Invalid video id')
 return v
def read(p, default=None): return json.loads(p.read_text()) if p.exists() else default
def atomic(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(dir=p.parent,prefix='.'+p.name)
 try:
  with os.fdopen(fd,'w') as f: json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp): os.unlink(tmp)
def journal():
 p=ROOT/'human/edits.jsonl'
 return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
def append(p,event):
 p.parent.mkdir(parents=True,exist_ok=True)
 raw=(json.dumps(event,ensure_ascii=False)+'\n').encode()
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
 try:
  if os.write(fd,raw)!=len(raw): raise OSError('Short journal write')
  os.fsync(fd)
 finally: os.close(fd)
def recalc(d):
 for i,s in enumerate(d['fine']):
  h=d['fine'][i-1].get('in_hand_at_end',{}) if i else {}
  held=h.get('left',[])+h.get('right',[])
  s['transition_in']=None if i==0 else 'NONE' if s['type']=='idle' else 'STRONG' if any(x and x in held for x in (s.get('object'),s.get('tool'))) else 'WEAK'
 for c in d['coarse']: c['transition_in']=d['fine'][c['fine_index_range'][0]]['transition_in']
 return d
def tokens(path):
 if not isinstance(path,str) or not re.fullmatch(r'[a-z_]+(?:\[\d+\])?(?:\.[a-z_]+)*',path): raise ValueError('Invalid field path')
 return [int(x) if x.isdigit() else x for x in re.findall(r'[a-z_]+|\d+',path)]
def get(d,path):
 for k in tokens(path): d=d[k]
 return copy.deepcopy(d)
def put(d,path,val):
 ks=tokens(path); q=d
 for k in ks[:-1]: q=q[k]
 q[ks[-1]]=copy.deepcopy(val)
def allowed(path):
 k=tokens(path)
 if k[0]=='fine': return len(k)>=3 and isinstance(k[1],int) and k[2] in FINE_FIELDS and (len(k)==3 or k[2]=='in_hand_at_end' and len(k)==4 and k[3] in ('left','right'))
 if k[0]=='coarse': return len(k)==3 and isinstance(k[1],int) and k[2] in ('instruction','description')
 return path in ('object_inventory','notes','goal.title','goal.description','goal.final_state','coarse_boundaries')
def partition(d,starts):
 if not isinstance(starts,list) or any(type(x)!=int for x in starts) or starts!=sorted(set(starts)) or not starts or starts[0]!=0 or starts[-1]>=len(d['fine']): raise ValueError('Invalid coarse boundaries')
 old={c['fine_index_range'][0]:c for c in d['coarse']}; result=[]
 for j,a in enumerate(starts):
  b=(starts[j+1] if j+1<len(starts) else len(d['fine']))-1
  c=copy.deepcopy(old.get(a,{'instruction':'','description':''})); c.update(start=d['fine'][a]['start'],end=d['fine'][b]['end'],fine_index_range=[a,b]); result.append(c)
 d['coarse']=result
def validate(d,base):
 if len(d['fine'])!=len(base['fine']): raise ValueError('Step count is immutable')
 inv=d['object_inventory']
 if not isinstance(inv,list) or any(not isinstance(x,str) or not x.strip() for x in inv) or len(set(inv))!=len(inv): raise ValueError('Invalid inventory')
 for s,b in zip(d['fine'],base['fine']):
  if s['start']!=b['start'] or s['end']!=b['end']: raise ValueError('Step times are immutable')
  if s['type'] not in ('action','idle') or s['hands'] not in ('left','right','both','unclear') or type(s['ambiguous'])!=bool: raise ValueError('Invalid step fields')
  h=s['in_hand_at_end']
  if set(h)!=set(('left','right')) or any(not isinstance(h[k],list) for k in h): raise ValueError('Invalid hands')
  if any(x is not None and x not in inv for x in [s.get('object'),s.get('tool'),s.get('target')]+h['left']+h['right']): raise ValueError('Unknown object')
  if s.get('confidence') not in ('high','medium','low'): raise ValueError('Invalid confidence')
  if s.get('summary') is not None and not isinstance(s['summary'],str): raise ValueError('Invalid summary')
 prev=0
 for c in d['coarse']:
  a,b=c['fine_index_range']
  if a!=prev or b<a or b>=len(d['fine']) or c['start']!=d['fine'][a]['start'] or c['end']!=d['fine'][b]['end']: raise ValueError('Partition must cover steps continuously')
  prev=b+1
 if prev!=len(d['fine']): raise ValueError('Incomplete partition')
def state(v,persist=True):
 base=read(ROOT/'annotations'/f'{ident(v)}.json')
 if base is None: raise FileNotFoundError(v)
 d=copy.deepcopy(base)
 for e in journal():
  if e['video_id']!=v: continue
  for p,val in e.get('changes',{}).items(): put(d,p,val)
 recalc(d)
 if persist and read(ROOT/'human/merged'/f'{v}.json')!=d: atomic(ROOT/'human/merged'/f'{v}.json',d)
 return d

def edit(v,req):
 with LOCK:
  d=state(v,False); before=copy.deepcopy(d); changes=req.get('changes',{})
  if not isinstance(changes,dict): raise ValueError('Invalid changes')
  for p,val in changes.items():
   if not allowed(p): raise ValueError('Immutable or unsupported field: '+p)
   if p=='coarse_boundaries':
    previous=copy.deepcopy(d['coarse']); partition(d,val)
    if req.get('move_boundary'):
     old,new=req['move_boundary']; source=next((c for c in previous if c['fine_index_range'][0]==old),None)
     dest=next((c for c in d['coarse'] if c['fine_index_range'][0]==new),None)
     if source is None or dest is None: raise ValueError('Invalid boundary move')
     for k in ('instruction','description'): dest[k]=source[k]
   else: put(d,p,val)
  if req.get('rename'):
   old,new=req['rename']
   if old not in d['object_inventory'] or not isinstance(new,str) or not new.strip() or new in d['object_inventory']: raise ValueError('Invalid object rename')
   d['object_inventory']=[new if x==old else x for x in d['object_inventory']]
   for s in d['fine']:
    for k in ('object','tool','target'):
     if s.get(k)==old: s[k]=new
    for k in ('left','right'): s['in_hand_at_end'][k]=[new if x==old else x for x in s['in_hand_at_end'][k]]
   # Text references follow the same atomic rename; structured fields above remain authoritative.
   def rename_text(x):
    if isinstance(x,str) and x==new: return x
    if isinstance(x,str): return re.sub(r'(?<![A-Za-z0-9_])'+re.escape(old)+r'(?![A-Za-z0-9_])',new,x,flags=re.IGNORECASE)
    if isinstance(x,list): return [rename_text(y) for y in x]
    if isinstance(x,dict): return {k:(y if k=='old_summary' else rename_text(y)) for k,y in x.items()}
    return x
   d=rename_text(d)
  recalc(d); validate(d,read(ROOT/'annotations'/f'{v}.json'))
  # One journal line commits a whole transaction (including rename/partition).
  changed={k:d[k] for k in d if d[k]!=before.get(k)}
  prior={k:before.get(k) for k in changed}
  event={'ts':datetime.datetime.now(datetime.timezone.utc).isoformat(),'video_id':v,'mode':req.get('mode','edit'),'item_id':req.get('item_id'),'path':next(iter(changes)) if len(changes)==1 else '__transaction__','before':prior,'after':changed,'changes':changed,'decision':req.get('decision'),'note':req.get('note',''),'error_fields':req.get('error_fields',[])}
  if event['mode']=='queue' and event['decision'] is not None and (event['decision'] not in ('confirm','reject','unsure','accept_agent','accept_verifier','custom')): raise ValueError('Invalid queue decision')
  if 'match_corrections' in req: event['match_corrections']=req['match_corrections']
  append(ROOT/'human/edits.jsonl',event)
  if str(event['item_id']).startswith('R:'): append(ROOT/'human/random_audit.jsonl',event)
  if read(ROOT/'human/merged'/f'{v}.json')!=d: atomic(ROOT/'human/merged'/f'{v}.json',d)
  return d

def undo(v):
 with LOCK:
  entries=[e for e in journal() if e['video_id']==v]
  undone={e.get('undo_ts') for e in entries if e.get('undo_ts')}
  last=next((e for e in reversed(entries) if not e.get('undo_ts') and e['ts'] not in undone),None)
  if not last: return state(v)
  event={'ts':datetime.datetime.now(datetime.timezone.utc).isoformat(),'video_id':v,'mode':last['mode'],'item_id':last['item_id'],'path':'__undo__','before':last['after'],'after':last['before'],'changes':last['before'],'decision':None,'note':'undo','undo_ts':last['ts']}
  append(ROOT/'human/edits.jsonl',event)
  if str(last['item_id']).startswith('R:'): append(ROOT/'human/random_audit.jsonl',event)
  return state(v)

def stable_sample(items,rate):
 return sorted(items,key=lambda x:hashlib.sha256(('EgoDual-2026-11-06:'+x['id']).encode()).hexdigest())[:math.ceil(len(items)*rate)]
def queues():
 out={k:[] for k in 'TSDPR'}; candidates=[]; pred_candidates=[]
 logs=journal(); undone={e.get('undo_ts') for e in logs if e.get('undo_ts')}; done={e.get('item_id') for e in logs if e.get('decision') and e['ts'] not in undone}
 for f in sorted((ROOT/'annotations').glob('*.json')):
  v=ident(f.stem); d=state(v,False); fine=d['fine']; coarse=d['coarse']; ver=read(ROOT/'verify'/f.name,{}) or {}; part=read(ROOT/'partition_b'/f.name,{}) or {}; pred=read(ROOT/'predictability'/f.name,{}) or {}
  blocked=set(); changed=set()
  for s in ver.get('steps',[]):
   i=s['fine_index']
   if s.get('transition_may_change'): changed.update([i,i+1])
   for field,result in s.get('fields',{}).items():
    if result.get('verdict') in ('incorrect','unsure'):
     out['D'].append(dict(id=f'D:{v}:{i}:{field}',video_id=v,index=i,start=fine[i]['start'],end=fine[i]['end'],field=field,agent=fine[i].get(field),verification=result)); blocked.add(i)
  for i,s in enumerate(fine):
   if i and (s['transition_in']=='STRONG' or i in changed):
    levels=['step']+(['subtask'] if any(c['fine_index_range'][0]==i for c in coarse) else [])
    for level in levels: out['T'].append(dict(id=f'T:{v}:{i}:{level}',video_id=v,index=i,start=max(0,s['start']-2),end=min(d['duration'],s['start']+2),previous=fine[i-1],next=s,level=level))
    blocked.update([i-1,i])
  pco=part.get('coarse',part.get('subtasks',[])); pb=[c['fine_index_range'][0] for c in pco][1:]
  for j,c in enumerate(coarse[1:],1):
   i=c['fine_index_range'][0]; out['S'].append(dict(id=f'S:{v}:{i}',video_id=v,index=i,coarse_index=j,start=max(0,c['start']-3),end=min(d['duration'],c['start']+3),context=fine[max(0,i-2):i+2],previous=coarse[j-1],next=c,partition_b=pb,partition_available=bool(part),partition_match=i in pb))
  # Also include independent-only boundaries.
  for i in sorted(set(pb)-{c['fine_index_range'][0] for c in coarse}):
   if 0<i<len(fine): out['S'].append(dict(id=f'S:{v}:independent:{i}',video_id=v,index=i,start=max(0,fine[i]['start']-3),end=min(d['duration'],fine[i]['start']+3),context=fine[max(0,i-2):i+2],partition_b=pb,partition_only=True))
  for p in pred.get('subtasks',[]):
   j=p['index']
   if j<len(coarse): pred_candidates.append(dict(id=f'P:{v}:{j}',video_id=v,index=coarse[j]['fine_index_range'][0],start=coarse[j]['start'],end=coarse[j]['end'],prediction=p,based_on=pred.get('based_on'),current_boundaries=[c['start'] for c in coarse],current_instructions=[c['instruction'] for c in coarse],current_mtime=(ROOT/'human/merged'/f.name if (ROOT/'human/merged'/f.name).exists() else f).stat().st_mtime))
  for i,s in enumerate(fine):
   if i not in blocked and not s.get('beyond_video_end'): candidates.append(dict(id=f'R:{v}:{i}',video_id=v,index=i,start=s['start'],end=s['end'],step=s))
 out['P']=stable_sample(pred_candidates,.2); out['R']=stable_sample(candidates,.1)
 for items in out.values():
  for x in items: x['done']=x['id'] in done
 return out

class Handler(BaseHTTPRequestHandler):
 def respond(self,obj,status=200):
  raw=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(raw)
 def do_GET(self):
  try:
   u=urlparse(self.path); q=parse_qs(u.query)
   if u.path=='/':
    raw=Path(__file__).with_name('index.html').read_bytes(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
   elif u.path=='/progress':
    raw=Path(__file__).with_name('progress.html').read_bytes(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
   elif u.path=='/api/progress': self.respond(collect_progress(ROOT))
   elif u.path=='/api/progress/report':
    name=q.get('name',[''])[0]
    allowed_reports={'bundle_preparation':'predictability/preparation_report.md','bundle_validation':'predictability/bundle_validation.json','annotation_validation':'validation_after_goal_completion.json','three_level_protocol':'predictability/three_level_protocol.md','text_predictability_result':'predictability_text/report.md','text_predictability_validation':'predictability_text/validation_after_merge.json'}
    if name not in allowed_reports: raise ValueError('Unknown report')
    p=ROOT/allowed_reports[name]; raw=p.read_bytes()
    self.send_response(200); self.send_header('Content-Type',('application/json' if p.suffix=='.json' else 'text/plain')+'; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
   elif u.path=='/api/videos': self.respond([{'video_id':p.stem,'gold':(ROOT/'gold'/p.name).exists()} for p in sorted((ROOT/'annotations').glob('*.json')) if ID.fullmatch(p.stem)])
   elif u.path=='/api/state':
    with LOCK: self.respond(state(ident(q['id'][0])))
   elif u.path=='/api/queues':
    with LOCK: self.respond(queues())
   elif u.path.startswith('/video/'):
    name=u.path[len('/video/'):]
    if not re.fullmatch(r'[0-9a-f]{16}\.mp4',name): raise ValueError('Invalid video filename')
    p=PROXIES/name; size=p.stat().st_size; start=0; end=size-1; rng=self.headers.get('Range'); status=200
    if rng:
     m=re.fullmatch(r'bytes=(\d*)-(\d*)',rng)
     if not m or not any(m.groups()): self.respond({'error':'Invalid range'},416); return
     a,b=m.groups()
     if not a: start=max(0,size-int(b))
     else: start=int(a); end=min(size-1,int(b)) if b else size-1
     if start>=size or end<start: self.send_response(416); self.send_header('Content-Range',f'bytes */{size}'); self.end_headers(); return
     status=206
    self.send_response(status); self.send_header('Content-Type','video/mp4'); self.send_header('Accept-Ranges','bytes'); self.send_header('Content-Length',str(end-start+1))
    if status==206: self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
    self.end_headers()
    with p.open('rb') as f:
     f.seek(start); remain=end-start+1
     while remain:
      raw=f.read(min(1024*1024,remain))
      if not raw: break
      self.wfile.write(raw); remain-=len(raw)
   else: self.respond({'error':'Not found'},404)
  except (BrokenPipeError,ConnectionResetError): pass
  except FileNotFoundError: self.respond({'error':'Not found'},404)
  except (ValueError,KeyError,IndexError,TypeError) as e: self.respond({'error':str(e)},400)
 def do_POST(self):
  try:
   if self.headers.get('Origin') and self.headers['Origin']!=f'http://{self.headers.get("Host")}': raise ValueError('Cross-origin request rejected')
   n=int(self.headers.get('Content-Length','0'))
   if n>2_000_000: raise ValueError('Request too large')
   req=json.loads(self.rfile.read(n)); v=ident(req['video_id']); path=urlparse(self.path).path
   if path=='/api/edit': self.respond(edit(v,req))
   elif path=='/api/undo': self.respond(undo(v))
   elif path=='/api/gold':
    if req.get('confirm') is not True: raise ValueError('Gold confirmation required')
    with LOCK:
     d=state(v); validate(d,read(ROOT/'annotations'/f'{v}.json')); atomic(ROOT/'gold'/f'{v}.json',d); self.respond({'ok':True})
   else: self.respond({'error':'Not found'},404)
  except FileNotFoundError: self.respond({'error':'Not found'},404)
  except (ValueError,KeyError,IndexError,TypeError) as e: self.respond({'error':str(e)},400)
if __name__=='__main__':
 parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8766); parser.add_argument('--root',type=Path); args=parser.parse_args()
 if args.root: ROOT=args.root.resolve()
 import errno
 while True:
  try:
   server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler); break
  except OSError as e:
   if e.errno!=errno.EADDRINUSE: raise
   args.port+=1
 print(f'Listening on http://127.0.0.1:{server.server_port}',flush=True); server.serve_forever()
