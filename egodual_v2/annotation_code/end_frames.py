from build_pilot import *
import subprocess,concurrent.futures
from PIL import Image,ImageDraw
ids=['e531cded0108b6c3','3a122ee7ff513956','0573fc312656e95a']
for v in ids:
 p=OUT/'frames'/v/'ends';p.mkdir(exist_ok=True)
 # Decode once from t=0; select native frames immediately before each end.
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,r_frame_rate','-of','json',str(ROOT/'review_run/proxies'/f'{v}.mp4')]))['streams'][0]
 num,den=map(int,probe['r_frame_rate'].split('/'));fps=num/den;last=int(probe['nb_frames'])-1
 frame_numbers=[min(last,max(0,__import__('math').ceil(min(s['end_time'],DURATION[v])*fps)-1)) for s in SOURCE[v]['segments']]
 selector='+'.join('eq(n,%d)'%n for n in frame_numbers)
 subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-i',str(ROOT/'review_run/proxies'/f'{v}.mp4'),'-vf',f"select='{selector}',scale=448:-2,drawtext=text='%{{pts\\:hms}}':x=4:y=4:fontsize=24:fontcolor=yellow:box=1:boxcolor=black@0.6",'-vsync','0','-start_number','0',str(p/'%03d.jpg')],check=True)
for v in ids:
 files=sorted((OUT/'frames'/v/'ends').glob('*.jpg'))
 for k in range(0,len(files),16):
  canvas=Image.new('RGB',(896,1696));draw=ImageDraw.Draw(canvas)
  for j,f in enumerate(files[k:k+16]):
   im=Image.open(f);im.thumbnail((224,400));x=j%4*224;y=j//4*424;canvas.paste(im,(x,y+24));draw.text((x+8,y+4),'step '+f.stem,fill='white')
  canvas.save(OUT/'frames'/v/f'fullends_{k//16:02d}.jpg')
print('end frames complete')
