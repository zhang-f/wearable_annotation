#!/usr/bin/env python3
"""Evidence frames: immutable source; original PTS burned before temporal sampling.
Each invocation writes a fresh run directory; manifest names exact current files.
"""
import argparse,bisect,concurrent.futures,csv,datetime,json,math,pathlib,subprocess
from PIL import Image,ImageDraw
ROOT=pathlib.Path('/home/fan/google'); OUT=ROOT/'review_run/annotation_v2'
STAMP="drawtext=text='t=%{pts\\:hms}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6"
def run(args):
 p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if p.returncode: raise RuntimeError(p.stderr[-3000:])
 return p.stdout
def ff(src,dst,filters,seek=None,dur=None):
 args=['ffmpeg','-nostdin','-y','-v','error','-threads','1']
 if seek is not None: args+=['-ss',str(seek)]
 if dur is not None: args+=['-t',str(dur)]
 args+=['-i',str(src),'-copyts','-vf',filters,'-vsync','0','-start_number','0',str(dst)]
 run(args)
def process(v,workers):
 meta={d['video_path'].removesuffix('.mp4'):d for d in map(json.loads,open(ROOT/'data_annotation/annotations_fine_completed.jsonl'))}
 inventory={r['video_id']:r for r in csv.DictReader(open(ROOT/'review_run/video_inventory.csv'))}
 if v not in meta or v not in inventory: raise ValueError('Unknown source video '+v)
 src=ROOT/'review_run/proxies'/f'{v}.mp4'; duration=float(inventory[v]['ffprobe_duration'])
 when=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'); folder=OUT/'frames_v2'/v/when; folder.mkdir(parents=True,exist_ok=False)
 manifest={'video_id':v,'source':str(src),'duration':duration,'timestamp_rule':'drawtext on original PTS before fps; selected end frames keep original PTS','run_dir':str(folder),'steps':[]}
 ov=folder/'overview';ov.mkdir();ff(src,ov/'sheet_%03d.jpg',f'scale=320:-2,{STAMP},fps=0.5,tile=4x4')
 manifest['overview']=[str(x) for x in sorted(ov.glob('sheet_*.jpg'))]
 jobs=[];start=0
 for i,s in enumerate(meta[v]['segments']):
  end=float(s['end_time']); beyond=end>duration;lo=max(0,start-.5);hi=min(duration,end+.5);rate=15 if end-start<1 else 3
  item={'fine_index':i,'start':start,'end':end,'beyond_video_end':beyond,'sample_fps':rate,'view_start':lo,'view_end':hi,'sheets':[]};manifest['steps'].append(item)
  if lo<hi:
   dest=folder/f'step_{i:03d}';dest.mkdir();jobs.append((item,dest))
  start=end
 def step(job):
  item,dest=job
  ff(src,dest/'sheet_%03d.jpg',f"scale=320:-2,{STAMP},fps={item['sample_fps']},tile=4x4",item['view_start'],item['view_end']-item['view_start'])
  item['sheets']=[str(x) for x in sorted(dest.glob('sheet_*.jpg'))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:list(pool.map(step,jobs))
 # Frame timestamps are measured, never inferred from frame number/fps.
 raw=run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(src)])
 pts=[]
 for line in raw.splitlines():
  try: pts.append(float(line.split(',')[0]))
  except ValueError: pass
 if not pts or pts!=sorted(pts): raise ValueError('Missing or nonmonotonic native frame PTS')
 ends=folder/'ends';ends.mkdir();selected={}
 for s in manifest['steps']:
  if s['beyond_video_end']: s['end_frame']=None;continue
  n=max(0,bisect.bisect_left(pts,s['end'])-1);s['end_frame']={'native_index':n,'pts':pts[n]};selected[n]=None
 numbers=sorted(selected)
 if numbers:
  expr='+'.join(f'eq(n,{n})' for n in numbers)
  ff(src,ends/'selected_%04d.jpg',f"select='{expr}',scale=448:-2,{STAMP}")
  files=sorted(ends.glob('selected_*.jpg'))
  if len(files)!=len(numbers):raise ValueError(f'End selection mismatch {len(files)} != {len(numbers)}')
  mapping=dict(zip(numbers,files))
  for s in manifest['steps']:
   if s['end_frame']:s['end_frame']['path']=str(mapping[s['end_frame']['native_index']])
  entries=[s for s in manifest['steps'] if s['end_frame']];sheets=[]
  for a in range(0,len(entries),16):
   part=entries[a:a+16];imgs=[Image.open(s['end_frame']['path']) for s in part];w=max(im.width for im in imgs);h=max(im.height for im in imgs)+28
   sheet=Image.new('RGB',(w*4,h*math.ceil(len(part)/4)),(20,20,20));draw=ImageDraw.Draw(sheet)
   for j,(s,im) in enumerate(zip(part,imgs)):
    x=j%4*w;y=j//4*h;sheet.paste(im,(x,y+28));draw.text((x+5,y+5),f"step #{s['fine_index']} END {s['end']:.3f}s",fill='white');im.close()
   p=ends/f'sheet_{a//16:03d}.jpg';sheet.save(p);sheets.append(str(p))
  manifest['end_sheets']=sheets
 (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(str(folder/'manifest.json'),flush=True)
 return manifest
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('video_ids',nargs='+');parser.add_argument('--workers',type=int,default=3);args=parser.parse_args()
 for v in args.video_ids:process(v,args.workers)
