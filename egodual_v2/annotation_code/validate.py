#!/usr/bin/env python3
"""Read-only structural validation. Usage: python validate.py [video.json ...]."""
import argparse,csv,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE=pathlib.Path(__file__).resolve().parent

def validate(d,src,duration):
 errors=[];warnings=[]
 def ck(test,msg):
  if not test:errors.append(msg)
 def no_predictable(x):
  if isinstance(x,dict):return 'predictable' not in x and all(no_predictable(v) for v in x.values())
  if isinstance(x,list):return all(no_predictable(v) for v in x)
  return True
 ck(no_predictable(d),'predictable field prohibited')
 f=d['fine'];c=d['coarse'];inv=d['object_inventory'];ck(len(inv)==len(set(inv)),'duplicate inventory')
 ck(len(f)==len(src['segments']),'fine count differs from source');ck(abs(d['duration']-duration)<.001,'duration differs from ffprobe inventory')
 start=0
 for i,(x,old) in enumerate(zip(f,src['segments'])):
  tag=f'fine[{i}]';ck(abs(x['start']-start)<=.01 and abs(x['end']-old['end_time'])<=.01,tag+' boundary differs');ck(x['end']>x['start'],tag+' nonpositive length');start=old['end_time']
  ck(x['old_summary']==old.get('summary',''),tag+' old_summary differs')
  ck(x['type'] in ['action','idle'],tag+' invalid type');ck(x['hands'] in ['left','right','both','unclear'],tag+' invalid hands');ck(x['confidence'] in ['high','medium','low'],tag+' invalid confidence');ck(isinstance(x['ambiguous'],bool),tag+' ambiguous not boolean')
  beyond=x['end']>duration;ck(x['beyond_video_end']==beyond,tag+' wrong beyond flag')
  if beyond:ck(all(x[k] is None for k in ['summary','verb','object','tool','target']),tag+' beyond fields non-null');ck(bool(x['boundary_note']),tag+' beyond needs note')
  else:
   ck(isinstance(x['summary'],str) and x['summary'].strip() not in ('','n'),tag+' empty placeholder');ck(len(x['summary'].split())<=12,tag+' summary exceeds 12 words')
   ck(x['summary']!=x['old_summary'] or bool(x.get('notes')),tag+' unchanged summary needs explanation')
  if x['type']=='idle' and not beyond:ck(x['summary'].startswith('idle') and x['verb'] is None and x['object'] is None,tag+' idle fields invalid')
  ck(set(x['in_hand_at_end'])=={'left','right'},tag+' missing hand lists')
  objects=[x[k] for k in ['object','tool','target'] if x[k] is not None]
  for h in ['left','right']:
   ck(isinstance(x['in_hand_at_end'][h],list),tag+' hand not list');objects+=x['in_hand_at_end'][h]
  ck(all(z in inv for z in objects),tag+' object absent from inventory')
  held=set(sum(f[i-1]['in_hand_at_end'].values(),[])) if i else set()
  tr=None if not i else 'NONE' if x['type']=='idle' else 'STRONG' if x['object'] in held or x['tool'] in held else 'WEAK'
  ck(x['transition_in']==tr,tag+' transition not derived')
  if i and x['summary']==f[i-1]['summary']:warnings.append(tag+' same summary as preceding step')
 next_index=0
 for i,x in enumerate(c):
  a,b=x['fine_index_range'];tag=f'coarse[{i}]';ck(a==next_index and 0<=a<=b<len(f),tag+' range not consecutive');next_index=b+1
  if not 0<=a<=b<len(f):continue
  ck(abs(x['start']-f[a]['start'])<=.01 and abs(x['end']-f[b]['end'])<=.01,tag+' times not fine-aligned');ck(x['transition_in']==f[a]['transition_in'],tag+' transition differs');ck(0<len(x['instruction'].split())<=10,tag+' instruction exceeds 10 words')
  if a==b:warnings.append(tag+' one step only')
  if x['end']-x['start']<5:warnings.append(tag+' shorter than 5 seconds')
 ck(next_index==len(f),'coarse does not cover every fine step')
 if not 3<=len(c)<=8:warnings.append('coarse count outside 3–8')
 if f[-1]['end']<duration:warnings.append(f'uncovered tail {duration-f[-1]["end"]:.3f}s retained; see video notes')
 return dict(video_id=d['video_id'],fine_count=len(f),coarse_count=len(c),errors=errors,warnings=warnings)

def main():
 p=argparse.ArgumentParser();p.add_argument('files',nargs='*');a=p.parse_args()
 source={x['video_path'][:-4]:x for x in map(json.loads,open(ROOT/'data_annotation/annotations_fine_completed.jsonl'))}
 duration={x['video_id']:float(x['ffprobe_duration']) for x in csv.DictReader(open(ROOT/'review_run/video_inventory.csv'))}
 results=[]
 for file in a.files or sorted((BASE/'videos').glob('*.json')):
  d=json.loads(pathlib.Path(file).read_text());results.append(validate(d,source[d['video_id']],duration[d['video_id']]))
 print(json.dumps(results,ensure_ascii=False,indent=2));return int(any(x['errors'] for x in results))
if __name__=='__main__':sys.exit(main())
