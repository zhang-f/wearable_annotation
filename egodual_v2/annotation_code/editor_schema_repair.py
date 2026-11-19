"""Normalize schema in editor_02-owned derived output only; preserve source boundaries."""
import json,pathlib,os,tempfile
base=pathlib.Path(__file__).resolve().parent
ids=['b6919021874d152d','c6f351e626d204f7','cafd82c22fda743d','ccb5d74c42da3d7d','ddb63645c6456edb','fced96b0f5b0dbf1']
changes=[]
for v in ids:
 p=base/'videos'/f'{v}.json';d=json.loads(p.read_text());bounds=[(x['start'],x['end'])for x in d['fine']]
 for i,s in enumerate(d['fine']):
  for k,new in [('hands','unclear')]:
   if s[k]=='none':changes.append(dict(video_id=v,fine_index=i,field=k,old=s[k],new=new));s[k]=new
  if s['type']=='idle':
   for k in ['verb','object']:
    if s[k] is not None:changes.append(dict(video_id=v,fine_index=i,field=k,old=s[k],new=None));s[k]=None
 for i,c in enumerate(d['coarse']):
  new={'Put the spatula away and carry the plate to the table.':'Put away spatula and carry plate to table.','Crack egg into a bowl and pour it into the pan.':'Crack egg into bowl and pour into pan.'}.get(c['instruction'])
  if new:changes.append(dict(video_id=v,coarse_index=i,field='instruction',old=c['instruction'],new=new));c['instruction']=new
 for i,s in enumerate(d['fine']):
  held=set(sum(d['fine'][i-1]['in_hand_at_end'].values(),[]))if i else set();s['transition_in']=None if not i else 'NONE'if s['type']=='idle'else 'STRONG'if s['object']in held or s['tool']in held else 'WEAK'
 for c in d['coarse']:c['transition_in']=d['fine'][c['fine_index_range'][0]]['transition_in']
 assert bounds==[(x['start'],x['end'])for x in d['fine']]
 fd,tmp=tempfile.mkstemp(dir=p.parent)
 with os.fdopen(fd,'w')as f:json.dump(d,f,indent=2,ensure_ascii=False);f.write('\n')
 os.replace(tmp,p)
(base/'editor_schema_repairs.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n')
print(len(changes),'schema field normalizations')
