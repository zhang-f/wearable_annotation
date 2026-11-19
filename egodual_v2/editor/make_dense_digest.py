import json,pathlib,sys,math
from PIL import Image,ImageDraw
p=pathlib.Path(sys.argv[1]);m=json.loads(p.read_text());base=p.parent;dest=base/'dense_digest_compact';dest.mkdir(exist_ok=False);frames=[]
for st in m['steps']:
 for f in st['sheets']:
  im=Image.open(f);w=im.width//4;h=im.height//4
  for j in range(16):
   tile=im.crop(((j%4)*w,(j//4)*h,(j%4+1)*w,(j//4+1)*h))
   # Padding tiles have no burned yellow timestamp. Keep every actual sampled frame.
   pixels=tile.crop((0,0,min(250,w),min(35,h))).getdata()
   if sum(1 for r,g,b in pixels if r>150 and g>120 and b<100)<5:continue
   tile=tile.resize((160,round(h*160/w)));frames.append((st['fine_index'],tile))
for n in range(0,len(frames),64):
 part=frames[n:n+64];h=max(x.height for _,x in part)+18;can=Image.new('RGB',(1280,h*math.ceil(len(part)/8)));dr=ImageDraw.Draw(can)
 for j,(i,im) in enumerate(part):
  x=j%8*160;y=j//8*h;can.paste(im,(x,y+18));dr.text((x+3,y+2),f'STEP {i}',fill='white')
 can.save(dest/f'digest_{n//64:03d}.jpg')
print(len(frames),'frames',math.ceil(len(frames)/64),'pages')
