import json,pathlib,subprocess,concurrent.futures,math
from PIL import Image,ImageDraw
ROOT=pathlib.Path('/home/fan/google');OUT=ROOT/'review_run/annotation_v2';IDS=['00735eddaeaaff4a','008a392f0747e13b','050e205b707d34c2','09608c5b07b02b7d','0af87fb5405568e9','14e98d6cd1072bfc','1b320f890d95b5d1','24d95d2a6c9ceb33','3c1d649e2700fae3','4918e35d642df5a0']
SOURCE={x['video_path'][:-4]:x for x in map(json.loads,open(ROOT/'data_annotation/annotations_fine_completed.jsonl'))}
DRAW="scale=320:-2,drawtext=text='%{pts\\:hms}':x=4:y=4:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6"
jobs=[]
for v in IDS:
 src=str(ROOT/'review_run/proxies'/f'{v}.mp4');base=OUT/'frames'/v/'native_v1';base.mkdir(parents=True,exist_ok=True)
 jobs.append(['ffmpeg','-v','error','-threads','1','-i',src,'-vf',DRAW+',fps=0.5,tile=4x4','-vsync','0',str(base/'overview_%03d.jpg')])
 st=0
 for i,s in enumerate(SOURCE[v]['segments']):
  en=s['end_time'];folder=base/f'step_{i:03d}';folder.mkdir(exist_ok=True);rate=15 if en-st<1 else 3
  jobs.append(['ffmpeg','-v','error','-threads','1','-ss',str(max(0,st-.5)),'-t',str(en+.5-max(0,st-.5)),'-i',src,'-copyts','-vf',DRAW+f',fps={rate},tile=4x4','-vsync','0',str(folder/'dense_%03d.jpg')]);st=en
 def endpoint():pass
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,r_frame_rate','-of','json',src]))['streams'][0];n=int(probe['nb_frames']);fps=eval(probe['r_frame_rate']);indices=sorted({min(n-1,max(0,math.ceil(s['end_time']*fps)-1)) for s in SOURCE[v]['segments']})
 (base/'end_frame_map.json').write_text(json.dumps([dict(step=i,frame=min(n-1,max(0,math.ceil(s['end_time']*fps)-1)),file=indices.index(min(n-1,max(0,math.ceil(s['end_time']*fps)-1)))) for i,s in enumerate(SOURCE[v]['segments'])],indent=2))
 ends=base/'ends';ends.mkdir(exist_ok=True)
 jobs.append(['ffmpeg','-v','error','-threads','1','-i',src,'-vf',DRAW+",select='"+'+'.join('eq(n,%d)'%i for i in indices)+"'",'-vsync','0','-start_number','0',str(ends/'%03d.jpg')])
def run(cmd):
 # Keep existing complete extraction; this script writes only its new version directory.
 pattern=cmd[-1];probe=pathlib.Path(pattern.replace('%03d','000' if '-start_number' in cmd else '001'))
 if probe.exists():return
 subprocess.run(['ffmpeg','-y']+cmd[1:],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:list(e.map(run,jobs))
for v in IDS:
 base=OUT/'frames'/v/'native_v1';mapping=json.loads((base/'end_frame_map.json').read_text())
 for k in range(0,len(mapping),16):
  canvas=Image.new('RGB',(1280,1792));draw=ImageDraw.Draw(canvas)
  for j,x in enumerate(mapping[k:k+16]):
   im=Image.open(base/'ends'/f"{x['file']:03d}.jpg");px=j%4*320;py=j//4*448;canvas.paste(im,(px,py+24));draw.text((px+4,py+4),'step '+str(x['step']),fill='white')
  canvas.save(base/f'endsheet_{k//16:02d}.jpg')
print('extracted',len(jobs),'outputs')
