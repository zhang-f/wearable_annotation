import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageStat
p=Path('/home/fan/google/review_run/annotation_v2/frames_v2/3c1d649e2700fae3/20261106T074405757721Z');m=json.loads((p/'manifest.json').read_text());tiles=[]
for x in m['steps']:
 for f in x['sheets'][1:]:
  im=Image.open(f);w=im.width//4;h=im.height//4
  for y in range(4):
   for z in range(4):
    t=im.crop((z*w,y*h,(z+1)*w,(y+1)*h))
    if max(ImageStat.Stat(t).mean)>1:tiles.append((x['fine_index'],t.copy()))
q=p/'extras_packed';q.mkdir(exist_ok=True)
for a in range(0,len(tiles),16):
 im=Image.new('RGB',(1280,1792));d=ImageDraw.Draw(im)
 for j,(idx,t) in enumerate(tiles[a:a+16]):
  x=j%4*320;y=j//4*448;im.paste(t,(x,y+24));d.text((x+4,y+3),f'step {idx} continuation',fill='white')
 im.save(q/f'{a//16:03}.jpg')
print('frames',len(tiles),'pages',(len(tiles)+15)//16)
