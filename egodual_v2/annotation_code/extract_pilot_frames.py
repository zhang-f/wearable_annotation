import json,pathlib,subprocess,concurrent.futures
ROOT=pathlib.Path('/home/fan/google'); OUT=ROOT/'review_run/annotation_v2/frames'
IDS=['e531cded0108b6c3','3a122ee7ff513956','0573fc312656e95a']
jobs=[]
for l in open(ROOT/'data_annotation/annotations_fine_completed.jsonl'):
 d=json.loads(l);v=d['video_path'][:-4]
 if v not in IDS:continue
 start=0
 for i,s in enumerate(d['segments']):
  end=s['end_time']; lo=max(0,start-.5); rate=15 if end-start<1 else 3
  folder=OUT/v/f'step_{i:03d}';folder.mkdir(parents=True,exist_ok=True)
  jobs.append((v,lo,end+.5-lo,rate,folder));start=end

def run(j):
 v,lo,dur,rate,folder=j
 subprocess.run(['ffmpeg','-y','-v','error','-threads','1','-ss',str(lo),'-t',str(dur),'-i',str(ROOT/'review_run/proxies'/f'{v}.mp4'),'-copyts','-vf',f"fps={rate},scale=320:-2,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=20:fontcolor=yellow:box=1:boxcolor=black@0.6,tile=4x4",'-vsync','0',str(folder/'dense_%03d.jpg')],check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,jobs))
print(len(jobs),'steps extracted')
