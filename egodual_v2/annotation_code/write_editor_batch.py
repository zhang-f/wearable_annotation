import json,csv,pathlib,os,tempfile
ROOT=pathlib.Path('/home/fan/google');OUT=ROOT/'review_run/annotation_v2'
SOURCE={d['video_path'][:-4]:d for d in map(json.loads,open(ROOT/'data_annotation/annotations_fine_completed.jsonl'))}
DURATION={r['video_id']:float(r['ffprobe_duration']) for r in csv.DictReader(open(ROOT/'review_run/video_inventory.csv'))}
def write(v,goal,inventory,lines,groups,notes,fix=None,evidence_manifest=None):
 rows=[x.split('|') for x in lines.strip().splitlines()];src=SOURCE[v];assert len(rows)==len(src['segments']),(v,len(rows),len(src['segments']));fine=[];start=0
 for i,(r,old) in enumerate(zip(rows,src['segments'])):
  assert len(r)==8,(i,r)
  summary,verb,obj,tool,target,hands,left,right=r;end=old['end_time'];beyond=end>DURATION[v]
  s=dict(start=start,end=end,old_summary=old.get('summary',''),summary=summary,verb=verb or None,object=obj or None,tool=tool or None,target=target or None,hands=hands,in_hand_at_end={'left':left.split(';') if left else [],'right':right.split(';') if right else []},type='idle' if summary.startswith('idle') else 'action',ambiguous=False,boundary_note=None,beyond_video_end=beyond,confidence='high',notes='')
  if fix and i in fix:s.update(fix[i])
  if s['type']!=old.get('type'):s['notes']+=' Type re-evaluated from visible interaction.'
  if beyond:s.update(summary=None,verb=None,object=None,tool=None,target=None,in_hand_at_end={'left':[],'right':[]},ambiguous=True,confidence='low',boundary_note='超出视频结尾')
  h=set(sum(fine[-1]['in_hand_at_end'].values(),[])) if fine else set();s['transition_in']=None if not fine else 'NONE' if s['type']=='idle' else 'STRONG' if any(x and x in h for x in (s['object'],s['tool'])) else 'WEAK';fine.append(s);start=end
 coarse=[]
 for a,b,instruction,description,contribution in groups:
  coarse.append(dict(start=fine[a]['start'],end=fine[b]['end'],fine_index_range=[a,b],instruction=instruction,description=description,goal_contribution=contribution,transition_in=fine[a]['transition_in'],predictability_level=None,predictability_status='pending_independent_past_only_test'))
 d=dict(video_id=v,duration=DURATION[v],task=src.get('task'),domain=src.get('domain'),query=src.get('query'),goal=goal,object_inventory=inventory,phases=[dict(start=c['start'],end=c['end'],description=c['description']) for c in coarse],fine=fine,coarse=coarse,notes=notes,evidence_manifest=evidence_manifest)
 inv=set(inventory)
 for s in fine:
  assert all(x in inv for x in [s['object'],s['tool'],s['target']]+sum(s['in_hand_at_end'].values(),[]) if x is not None),(v,s)
  assert s['summary'] is None or len(s['summary'].split())<=12,(v,s['summary'])
 prev=0
 for c in coarse:assert c['fine_index_range'][0]==prev;prev=c['fine_index_range'][1]+1
 assert prev==len(fine)
 p=OUT/'videos'/f'{v}.json';assert not p.exists(),p
 p.parent.mkdir(exist_ok=True);fd,tmp=tempfile.mkstemp(dir=p.parent)
 with os.fdopen(fd,'w')as f:json.dump(d,f,indent=2,ensure_ascii=False);f.write('\n')
 os.replace(tmp,p)
 print(v,len(fine),'steps',len(coarse),'subtasks')
 return d
