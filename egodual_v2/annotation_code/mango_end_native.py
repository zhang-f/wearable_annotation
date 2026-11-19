from batch01_builder import *
import bisect,subprocess
from PIL import Image,ImageDraw
v='24d95d2a6c9ceb33';p=OUT/'frames'/v/'native_v1'/'ends_verified';p.mkdir(exist_ok=True);src=OUT.parent/'proxies'/f'{v}.mp4'
raw=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','csv=p=0',str(src)],text=True)
pts=[float(l.split(',')[0]) for l in raw.splitlines() if l.strip()];ns=[bisect.bisect_left(pts,s['end_time'])-1 for s in SOURCE[v]['segments']];unique=sorted(set(ns));expr='+'.join('eq(n,%d)'%n for n in unique)
subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','1','-i',str(src),'-vf',f"select='{expr}',scale=320:-2,drawtext=text='%{{pts\\:hms}}':x=4:y=4:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6",'-vsync','0','-start_number','0',str(p/'%03d.jpg')],check=True)
files=sorted(p.glob('[0-9]*.jpg'));assert len(files)==len(unique),(len(files),len(unique));mapping=dict(zip(unique,files))
for a in range(0,len(ns),16):
 im=Image.new('RGB',(1280,1792));d=ImageDraw.Draw(im)
 for j,n in enumerate(ns[a:a+16]):
  tile=Image.open(mapping[n]);xx=j%4*320;yy=j//4*448;im.paste(tile,(xx,yy+24));d.text((xx+4,yy+3),f'step {a+j} native PTS {pts[n]:.3f}',fill='white')
 im.save(p/f'sheet_{a//16:03}.jpg')
(p/'map.json').write_text(json.dumps([dict(step=i,frame=n,pts=pts[n],path=str(mapping[n])) for i,n in enumerate(ns)],indent=2))
print('verified',len(ns))
