"""Real pilot copied into an isolated root; no production human edits."""
import copy, importlib.util, json, shutil, subprocess, sys, tempfile, pathlib, hashlib, time, urllib.request
HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('editor_server',HERE/'server.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=HERE.parent/'annotations/e531cded0108b6c3.json'; orig=source.read_bytes(); vid=source.stem
with tempfile.TemporaryDirectory(prefix='editor-selftest-',dir=HERE) as td:
 root=pathlib.Path(td);(root/'annotations').mkdir();shutil.copy2(source,root/'annotations'/source.name);m.ROOT=root; m.PROXIES=root/'proxies'; m.PROXIES.mkdir(); (m.PROXIES/(vid+'.mp4')).write_bytes(bytes(range(200)))
 base=m.state(vid,False); i=next(i for i in range(1,len(base['fine'])) if base['fine'][i].get('object') or base['fine'][i].get('tool')); obj=base['fine'][i].get('object') or base['fine'][i]['tool']
 d=m.edit(vid,{'changes':{f'fine[{i-1}].in_hand_at_end':{'left':[obj],'right':[]}}});assert d['fine'][i]['transition_in']=='STRONG'
 assert m.undo(vid)==m.recalc(copy.deepcopy(base))
 oldstarts=[c['fine_index_range'][0] for c in base['coarse']]; target=next(x for x in range(1,len(base['fine'])) if x not in oldstarts)
 changed=sorted([0,target]+oldstarts[2:]);d=m.edit(vid,{'changes':{'coarse_boundaries':changed}});m.validate(d,base);assert [c['fine_index_range'][0] for c in d['coarse']]==changed
 assert m.undo(vid)==m.recalc(copy.deepcopy(base))
 old=base['object_inventory'][0]; d=m.edit(vid,{'rename':[old,old+' renamed']});m.validate(d,base);assert old not in d['object_inventory'];assert m.undo(vid)==m.recalc(copy.deepcopy(base))
 try: m.edit(vid,{'changes':{'fine[0].transition_in':'STRONG'}});raise AssertionError('transition accepted')
 except ValueError: pass
 try: m.edit(vid,{'changes':{'fine[0].end':99}});raise AssertionError('retime accepted')
 except ValueError: pass
 q=m.queues();assert q['D']==q['P']==[]
 print('PASS: real pilot holds→transitions, partition move, rename, undo, immutable fields, absent verify/predictability')
 # Browser uses isolated journal, plus synthetic future-stage fixtures for all five queues.
 (root/'verify').mkdir();(root/'predictability').mkdir();(root/'partition_b').mkdir()
 (root/'verify'/source.name).write_text(json.dumps({'steps':[{'fine_index':0,'fields':{'summary':{'verdict':'incorrect','suggested':'test replacement','evidence':'isolated test fixture'}}}]}))
 (root/'predictability'/source.name).write_text(json.dumps({'based_on':{'boundaries':[c['start'] for c in base['coarse']]},'subtasks':[{'index':1,'actual':base['coarse'][1]['instruction'],'forecasts':{'f1':['test'],'f2':['test'],'f3':['test']},'top1_match':{'f1':True,'f2':False,'f3':True}}]}))
 # Exercise HTTP handlers without creating sockets (sandbox prohibits socket()).
 import io, email.message
 def get(path, range_header=None):
  h=m.Handler.__new__(m.Handler); h.path=path; h.request_version='HTTP/1.1'; h.requestline='GET '+path+' HTTP/1.1'; h.command='GET'; h.headers=email.message.Message(); h.wfile=io.BytesIO(); h.log_request=lambda *a:None
  if range_header: h.headers['Range']=range_header
  h.do_GET(); return h.wfile.getvalue()
 r=get('/video/'+vid+'.mp4','bytes=0-99'); assert b'206 Partial Content' in r and len(r.split(b'\r\n\r\n',1)[1])==100
 assert b'400 Bad Request' in get('/video/../../etc/passwd')
 for endpoint in ['/api/videos','/api/state?id='+vid,'/api/queues','/']:
  assert b'200 OK' in get(endpoint)
 print('PASS: offline HTTP handlers: Range, filename rejection, videos/state/queues/index')
 # Preserve instruction/description when shifting a boundary.
 starts=[c['fine_index_range'][0] for c in base['coarse']]; old=starts[1]; new=old+1 if old+1<len(base['fine']) else old-1
 d=m.edit(vid,{'changes':{'coarse_boundaries':[0,new]},'move_boundary':[old,new]})
 assert d['coarse'][1]['instruction']==base['coarse'][1]['instruction']; assert d['coarse'][1]['description']==base['coarse'][1]['description']; assert m.undo(vid)==m.recalc(copy.deepcopy(base))
 # Concurrent form fields are one transaction and undo together.
 d=m.edit(vid,{'changes':{'goal.title':'edited goal','fine[0].summary':'edited summary','coarse[0].instruction':'edited subtask'}})
 assert d['goal']['title']=='edited goal' and d['fine'][0]['summary']=='edited summary' and d['coarse'][0]['instruction']=='edited subtask'; assert m.undo(vid)==m.recalc(copy.deepcopy(base))
 print('PASS: shifted subtask text preserved; multi-region transaction and undo preserve all fields')
assert source.read_bytes()==orig
print('PASS: original pilot bytes unchanged; all test journals removed with isolated root')
