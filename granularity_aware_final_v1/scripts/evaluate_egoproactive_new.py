#!/usr/bin/env python3
"""Official EgoProactive val inference for Qwen/Gemma base and MG-SFT adapters."""
import argparse, contextlib, json, os, re, sys, time, traceback
from pathlib import Path
import av, numpy as np, torch
from PIL import Image

BENCH=Path('/data/fan/projects/procedure_forecasting/runs/egoproactive_eval_v1')
ROOT=Path('/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1/egoproactive')
DATA=BENCH/'data/wearable-ai/egoproactive/wearable_ai_2026_egoproactive_val_700.jsonl'
VIDEOS=BENCH/'data/wearable-ai/egoproactive/val'
STARTER=BENCH/'data/wearable-ai/starter_kit'
SYSTEM_PROMPT=(
    'You are a proactive AI assistant watching a first-person video of the user performing a procedural task. '
    'The user has issued a single high-level query. As the video unfolds you observe a series of short (~8s) chunks; '
    'after each chunk you decide whether to speak or stay silent.\n\n'
    'Output format (single line, no preamble):\n'
    '  - If you should speak: start with the literal token `$interrupt$` followed by your suggestion or answer in plain text.\n'
    '  - If you should stay silent: output the single literal token `$silent$` and nothing else.\n\n'
    'Speak when the user asks you something, when an earlier action needs correction, or when you have useful, timely guidance for the next step. '
    'Stay silent when nothing useful needs to be said.'
)
MAX_FRAMES=32; FRAMES_PER_INTERVAL=16; MAX_HISTORY=4; MAX_NEW_TOKENS=512

def load_jsonl(path): return [json.loads(x) for x in open(path) if x.strip()]
def atomic_json(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(obj,ensure_ascii=False)+'\n');t.replace(p)
def frame_indices(intervals,fps,total):
 per=[]
 for start,end in intervals:
  start_f=int(float(start)*fps);end_f=min(int(float(end)*fps),total-1)
  if end_f<=start_f: per.append([]);continue
  n=min(FRAMES_PER_INTERVAL,end_f-start_f+1);step=(end_f-start_f)/n
  per.append([int(start_f+i*step) for i in range(n)])
 return per

def extract_session_frames(video_path,intervals):
 """Same index sampling as official starter-kit extract_frames; decode once with PyAV."""
 with av.open(str(video_path)) as c:
  s=c.streams.video[0];s.thread_type='SLICE';s.codec_context.thread_count=1
  fps=float(s.average_rate);total=int(s.frames or 0)
  if total<=0: total=sum(1 for _ in c.decode(s));c.seek(0,stream=s,backward=True);s=c.streams.video[0]
  per=frame_indices(intervals,fps,total);needed=set(i for a in per for i in a);keep={};
  if needed:
   for ix,f in enumerate(c.decode(s)):
    if ix in needed: keep[ix]=f.to_image().convert('RGB')
    if ix>=max(needed):break
  return [[keep[i] for i in ids if i in keep] for ids in per], {'fps':fps,'total_frames':total,'decoded_sampled_frames':len(keep)}

def select_context(per_interval,chunk):
 frames=[im for segment in per_interval[:chunk+1] for im in segment]
 if len(frames)>MAX_FRAMES:
  stride=len(frames)/MAX_FRAMES;frames=[frames[int(i*stride)] for i in range(MAX_FRAMES)]
 return frames

def history_messages(row,j):
 turns=row.get('dialog',[]); past=turns[j][1:] if j<len(turns) and len(turns[j])>=1 else []
 past=past[-MAX_HISTORY:] if MAX_HISTORY>0 else []
 out=[]
 for t in past:
  text=t.get('text') or ''
  if not text: continue
  role=str(t.get('role','user')).strip().lower()
  if role not in ('user','assistant'): role='user'
  out.append({'role':role,'content':str(text)})
 return out

def messages_for(row,j,frames):
 # Preserve the benchmark's original user query exactly; EgoProactive does not
 # request a forecasting granularity tag.
 query=str(row.get('query',''))
 msgs=[{'role':'system','content':SYSTEM_PROMPT}]
 if query: msgs.append({'role':'user','content':query})
 msgs.extend(history_messages(row,j))
 mm=[];inserted=False
 for m in msgs:
  if m['role']=='user' and not inserted and frames:
   c=[{'type':'image'} for _ in frames]+[{'type':'text','text':m['content']}]
   mm.append({'role':'user','content':c});inserted=True
  else: mm.append(m)
 return mm

def merge_consecutive_roles(messages):
 """Preserve history text while satisfying strict alternating chat templates."""
 out=[]
 for m in messages:
  if out and out[-1]['role']==m['role'] and m['role'] in ('user','assistant'):
   out[-1]['content']=out[-1]['content']+'\n\n'+m['content']
  else:
   out.append(dict(m))
 return out

def official_answer(raw):
 """Bridge our trained tags to the benchmark's required serialization."""
 s=str(raw).strip()
 if s.lower().startswith('$interrupt$'): return '$interrupt$'+s[len('$interrupt$'):].lstrip()
 if s.lower().startswith('$silent$'): return '$silent$'
 m=re.match(r'^<\s*SPEAK\s*>(.*)$',s,re.I|re.S)
 if m: return '$interrupt$'+m.group(1).strip()
 if re.match(r'^<\s*SILENT\s*>',s,re.I): return '$silent$'
 # Do not infer a decision from ordinary prose; official parser treats it as silent.
 return s

def get_processor_and_model(backbone,device,adapter):
 from transformers import AutoProcessor
 from peft import PeftModel
 is_full_checkpoint=not Path(adapter,'adapter_config.json').exists()
 if backbone=='qwen':
  base='/data/fan/models/Qwen3-VL-8B-Instruct'
  from transformers import Qwen3VLForConditionalGeneration
  proc=AutoProcessor.from_pretrained(base,local_files_only=True)
  # Match the effective Qwen video-frame scale used in MG-SFT; prevent 32 image placeholders from expanding to huge sequences.
  # Match the visual-token scale used by MG-SFT training (~288 visual tokens/frame).
  # 384^2*2 yields 266 patch-merged tokens for a 16:9 1080p frame with this processor.
  proc.image_processor.size={'shortest_edge':4096,'longest_edge':384*384*2}
  model=Qwen3VLForConditionalGeneration.from_pretrained(adapter if is_full_checkpoint else base,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':device})
 elif backbone=='gemma':
  base='/data/fan/models/Gemma-3-12B-IT'
  from transformers import Gemma3ForConditionalGeneration
  proc=AutoProcessor.from_pretrained(base,local_files_only=True)
  model=Gemma3ForConditionalGeneration.from_pretrained(adapter if is_full_checkpoint else base,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='sdpa',device_map={'':device})
 else: raise ValueError(backbone)
 model.config.use_cache=True
 # Full-SFT checkpoints are complete finetuned weights, not a LoRA delta on
 # base -- nothing to wrap with PeftModel, and no zero-shot/disable_adapter
 # path exists for them (evaluator must be run with --finetuned-only).
 if not is_full_checkpoint:
  model=PeftModel.from_pretrained(model,adapter,is_trainable=False,local_files_only=True)
 model.eval()
 return proc,model,adapter

def encode(proc,backbone,mm,frames):
 text=proc.apply_chat_template(mm,tokenize=False,add_generation_prompt=True)
 if backbone=='gemma': x=proc(text=[text],images=[frames] if frames else None,return_tensors='pt')
 else: x=proc(text=[text],images=frames if frames else None,padding=True,return_tensors='pt')
 return {k:v.to(device='cuda',dtype=torch.bfloat16 if v.is_floating_point() else v.dtype) if torch.is_tensor(v) else v for k,v in x.items()}

def generate(proc,model,inputs,adapter_enabled):
 ctx=contextlib.nullcontext() if adapter_enabled else model.disable_adapter()
 with ctx,torch.inference_mode():
  seq=model.generate(**inputs,max_new_tokens=MAX_NEW_TOKENS,do_sample=False,num_beams=1,use_cache=True)
 ids=seq[0,inputs['input_ids'].shape[1]:]
 return proc.tokenizer.decode(ids,skip_special_tokens=True).strip()

def process(backbone,rank,world,adapter,limit=None,max_chunks=None,tag=None,finetuned_only=False):
 torch.set_num_threads(1);torch.cuda.set_device(rank);device=f'cuda:{rank}'
 rows=load_jsonl(DATA);rows=rows[:limit] if limit else rows;assigned=rows[rank::world]
 shard=ROOT/'predictions';shard.mkdir(exist_ok=True)
 suffix=f'_{tag}' if tag else ''
 pbase=shard/f'{backbone}_zero_shot{suffix}_rank{rank}.jsonl';pft=shard/f'{backbone}_finetuned{suffix}_rank{rank}.jsonl';detail=shard/f'{backbone}_details{suffix}_rank{rank}.jsonl';errp=ROOT/'logs'/f'{backbone}_errors{suffix}_rank{rank}.jsonl'
 done0={json.loads(x)['video_path'] for x in open(pbase) if x.strip()} if pbase.exists() else set();done1={json.loads(x)['video_path'] for x in open(pft) if x.strip()} if pft.exists() else set()
 proc,model,adapter=get_processor_and_model(backbone,device,adapter)
 print(json.dumps({'stage':'loaded','backbone':backbone,'rank':rank,'n_assigned':len(assigned),'done_zero':len(done0),'done_ft':len(done1)}),flush=True)
 start=time.time()
 with pbase.open('a') as f0,pft.open('a') as f1,detail.open('a') as fd:
  for n,row in enumerate(assigned):
   vp=str(row['video_path']);intervals=row['video_intervals'];begin=time.time();session_details=[]
   if (finetuned_only and vp in done1) or (not finetuned_only and vp in done0 and vp in done1): continue
   video_path=VIDEOS/vp
   try:
    if max_chunks is not None:
     intervals=intervals[:max_chunks]
     row=dict(row);row['answers']=row['answers'][:max_chunks]
    per,meta=extract_session_frames(video_path,intervals)
    if not per: raise RuntimeError('no intervals/frames decoded')
    out0=[];out1=[]
    for j,interval in enumerate(intervals):
     frames=select_context(per,j);mm=messages_for(row,j,frames)
     if backbone=='gemma': mm=merge_consecutive_roles(mm)
     inputs=encode(proc,backbone,mm,frames)
     raw0=None if finetuned_only else (generate(proc,model,inputs,False) if vp not in done0 else None)
     raw1=generate(proc,model,inputs,True) if vp not in done1 else None
     if raw0 is not None: out0.append(official_answer(raw0))
     if raw1 is not None: out1.append(official_answer(raw1))
     session_details.append({'video_path':vp,'chunk_index':j,'start_sec':interval[0],'end_sec':interval[1],'num_context_frames':len(frames),'gold':row['answers'][j] if j<len(row['answers']) else None,'zero_shot_raw':raw0,'zero_shot_answer':official_answer(raw0) if raw0 is not None else None,'finetuned_raw':raw1,'finetuned_answer':official_answer(raw1) if raw1 is not None else None})
    if not finetuned_only and vp not in done0:
     pred={'video_path':vp,'answers':out0};f0.write(json.dumps(pred,ensure_ascii=False)+'\n');f0.flush();done0.add(vp)
    if vp not in done1:
     pred={'video_path':vp,'answers':out1};f1.write(json.dumps(pred,ensure_ascii=False)+'\n');f1.flush();done1.add(vp)
    fd.write(json.dumps({'video_path':vp,'duration_in_sec':row.get('duration_in_sec'),'query':row.get('query'),'task':row.get('task'),'intervals':session_details,'frame_decode':meta,'wall_clock_sec':time.time()-begin},ensure_ascii=False)+'\n');fd.flush()
   except Exception as e:
    err={'video_path':vp,'rank':rank,'error':repr(e),'traceback':traceback.format_exc()}
    with errp.open('a') as fe: fe.write(json.dumps(err)+'\n')
    # Preserve denominator and session order; failed sessions receive explicit silent decisions and stay visible in the error log.
    sil=['$silent$']*len(intervals)
    if not finetuned_only and vp not in done0: f0.write(json.dumps({'video_path':vp,'answers':sil})+'\n');f0.flush();done0.add(vp)
    if vp not in done1: f1.write(json.dumps({'video_path':vp,'answers':sil})+'\n');f1.flush();done1.add(vp)
   if (n+1)%5==0 or n==0:
    progress={'backbone':backbone,'rank':rank,'completed_assigned':n+1,'assigned_total':len(assigned),'zero_shot_completed':len(done0),'finetuned_completed':len(done1),'elapsed_sec':time.time()-start,'sessions_per_sec':(n+1)/max(time.time()-start,1e-6)}
    atomic_json(ROOT/'logs'/f'{backbone}_progress_rank{rank}.json',progress);print(json.dumps(progress),flush=True)
 torch.cuda.synchronize()
 print(json.dumps({'stage':'rank_complete','backbone':backbone,'rank':rank,'elapsed_sec':time.time()-start,'zero_shot':len(done0),'finetuned':len(done1),'peak_gpu_memory_gb':torch.cuda.max_memory_allocated()/1e9}),flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--backbone',choices=['qwen','gemma'],required=True);ap.add_argument('--adapter',required=True);ap.add_argument('--limit',type=int,default=None);ap.add_argument('--max-chunks',type=int,default=None);ap.add_argument('--tag',default=None);ap.add_argument('--finetuned-only',action='store_true');ap.add_argument('--rank',type=int,default=None);ap.add_argument('--world-size',type=int,default=None);a=ap.parse_args()
 rank=a.rank if a.rank is not None else int(os.environ.get('LOCAL_RANK',os.environ.get('RANK',0)));world=a.world_size if a.world_size is not None else int(os.environ.get('WORLD_SIZE',1));process(a.backbone,rank,world,a.adapter,a.limit,a.max_chunks,a.tag,a.finetuned_only)
if __name__=='__main__':main()
