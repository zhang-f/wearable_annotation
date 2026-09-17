#!/usr/bin/env python3
"""DDP pair-aware LoRA/Full-SFT for the corrected independent dense grid."""
import argparse, contextlib, csv, json, os, random, time, signal
from pathlib import Path
import numpy as np
import torch
import torch.distributed as dist
import torch.nn.functional as F
from torch.nn.parallel import DistributedDataParallel as DDP

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from final_common import ROOT, atomic_json, append_tokens, configure_trainable, decision_tokens, decode_prefix, device_batch, load_model, load_processor, make_prompt_inputs, seed_all


def fetch(handle, offset):
    handle.seek(int(offset)); return json.loads(handle.readline())


class DecodeTimeout(RuntimeError): pass

def timed_decode(row, seconds=120):
    """Bound a pathological seek/decode so one corrupt/slow video cannot idle
    seven ranks until the NCCL watchdog fires."""
    def expire(_signum, _frame): raise DecodeTimeout(f'video decode exceeded {seconds}s: {row["video_id"]}')
    previous = signal.signal(signal.SIGALRM, expire); signal.setitimer(signal.ITIMER_REAL, seconds)
    try: return decode_prefix(row)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0); signal.signal(signal.SIGALRM, previous)

def next_decodable(handle, pool, rank, role):
    for attempt in range(8):
        row = fetch(handle, pool.next())
        try: return row, *timed_decode(row)
        except Exception as exc:
            path = ROOT / 'logs' / f'decode_retry_rank{rank}.jsonl'; path.parent.mkdir(exist_ok=True)
            with path.open('a') as out: out.write(json.dumps({'time':time.time(),'role':role,'video_id':row['video_id'],'pair_id':row['pair_id'],'attempt':attempt,'error':repr(exc)})+'\n')
    raise RuntimeError(f'No decodable candidate after 8 attempts for role={role}')


class RotatingPool:
    def __init__(self, values, seed):
        self.values = np.asarray(values, dtype=np.int64); self.rng = np.random.default_rng(seed); self.order = self.rng.permutation(len(self.values)); self.cursor = 0
    def next(self):
        if self.cursor >= len(self.order): self.order = self.rng.permutation(len(self.values)); self.cursor = 0
        v = self.values[self.order[self.cursor]]; self.cursor += 1; return int(v)


def lprobs(outputs, original, suffix):
    logits = outputs.logits[:, original - 1: original - 1 + suffix.shape[1], :]
    return torch.gather(F.log_softmax(logits.float(), -1), -1, suffix.to(logits.device).unsqueeze(-1)).squeeze(-1)[0]


def forward_suffix(model, prompt_inputs, suffix, device):
    inputs, original = append_tokens(prompt_inputs, suffix)
    if os.environ.get('MEM_DEBUG'):
        before = torch.cuda.memory_allocated(device)/1e9
    output = model(**device_batch(inputs, device), use_cache=False)
    if os.environ.get('MEM_DEBUG'):
        after = torch.cuda.memory_allocated(device)/1e9
        print(json.dumps({'dbg':'fwd_call','suffix_len':int(suffix.shape[1]),'input_ids_len':int(inputs['input_ids'].shape[1]),'before_gb':before,'after_gb':after,'delta_gb':after-before}), flush=True)
    return lprobs(output, original, suffix)


def branch(model, prompt_inputs, target_decision, content, speak_tokens, silent_tokens, device, need_score=True):
    """Decision NLL, content NLL, and s=meanLP(S)-meanLP(L).

    Decision strings use mean token log probability exactly as specified. The
    content CE begins after `<SPEAK>` and is separately per-example normalized.
    """
    is_speak = target_decision == 'SPEAK'
    if is_speak:
        suffix_s = torch.cat([speak_tokens, content], 1)
        lp_s_all = forward_suffix(model, prompt_inputs, suffix_s, device)
        lp_s = lp_s_all[:speak_tokens.shape[1]]
        content_loss = -lp_s_all[speak_tokens.shape[1]:].mean() if content.shape[1] else lp_s.sum() * 0
    else:
        lp_s = forward_suffix(model, prompt_inputs, speak_tokens, device)
        content_loss = lp_s.sum() * 0
    lp_l = forward_suffix(model, prompt_inputs, silent_tokens, device) if need_score or not is_speak else None
    chosen = lp_s if is_speak else lp_l
    decision_loss = -chosen.mean()
    score = lp_s.mean() - lp_l.mean() if need_score else None
    return decision_loss, content_loss, score


def allmean(value, count, world):
    """Global group mean with DDP's gradient averaging accounted for."""
    count_t = torch.tensor(float(count), device=value.device)
    dist.all_reduce(count_t, op=dist.ReduceOp.SUM)
    if count_t.item() == 0: return value * 0
    return value * (world / count_t.item())


def content_tokens(tokenizer, text):
    if not text: return torch.empty((1, 0), dtype=torch.long)
    return tokenizer(' ' + text, add_special_tokens=False, return_tensors='pt')['input_ids']


def choose_role(step, rank):
    roles = ('lgran_fine_only','lgran_fine_only','lgran_coarse_only','lgran_coarse_only','coarse_pos','coarse_bg','fine_pos','fine_neg')
    return roles[(step + rank) % len(roles)]


def save_checkpoint(model, processor, path, backbone, mode, variant, step, trainable_count):
    if dist.get_rank() == 0:
        path.mkdir(parents=True, exist_ok=True)
        base = model.module if isinstance(model, DDP) else model
        base.save_pretrained(path, safe_serialization=True)
        processor.save_pretrained(path)
        atomic_json(path / 'checkpoint_meta.json', {'backbone': backbone, 'mode': mode, 'variant': variant, 'step': step, 'trainable_parameters': trainable_count})
    dist.barrier()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backbone', choices=('qwen','gemma'), required=True)
    ap.add_argument('--mode', choices=('lora','full'), required=True)
    ap.add_argument('--variant', choices=('no_none','weighted_none'), required=True)
    ap.add_argument('--steps', type=int, default=1254)
    ap.add_argument('--grad-accum', type=int, default=2)
    ap.add_argument('--smoke-only', action='store_true')
    args = ap.parse_args()
    rank, local, world = int(os.environ['RANK']), int(os.environ['LOCAL_RANK']), int(os.environ['WORLD_SIZE'])
    torch.cuda.set_device(local); torch.set_num_threads(1); dist.init_process_group('nccl'); seed_all(42 + rank)
    device = f'cuda:{local}'; out = ROOT / f'{args.backbone}_{args.mode}_{args.variant}'
    out.mkdir(parents=True, exist_ok=True)
    arrays = np.load(ROOT / 'data/train_pool_offsets.npz')
    pools = {k: RotatingPool(arrays[k], 4200 + rank * 97 + i) for i,k in enumerate(arrays.files)}
    required = ('coarse_pos','coarse_bg','coarse_none','fine_pos','fine_neg','lgran_fine_only','lgran_coarse_only')
    if any(len(arrays[k]) == 0 for k in required): raise RuntimeError('Empty required dynamic pool')
    processor = load_processor(args.backbone); speak_tokens, silent_tokens = decision_tokens(processor.tokenizer)
    model = load_model(args.backbone, device); model, targets, trainable = configure_trainable(model, args.backbone, args.mode)
    model.config.use_cache = False; model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False})
    if os.environ.get('MEM_DEBUG') and rank == 0:
        gc_flags = {n: m.gradient_checkpointing for n, m in model.named_modules() if hasattr(m, 'gradient_checkpointing')}
        print(json.dumps({'dbg':'gc_check','is_gradient_checkpointing':getattr(model,'is_gradient_checkpointing',None),'training':model.training,'n_flags_true':sum(1 for v in gc_flags.values() if v),'n_flags_total':len(gc_flags)}), flush=True)
    # DDP wrapping showed a huge, unexplained per-rank memory blowup specific
    # to Gemma3 (mostly-frozen-params + DDP's bucket/hook bookkeeping), even
    # at world_size=1 -- a bare forward went from ~25GB to >100GB purely from
    # being called through the DDP wrapper. allmean() already manually
    # all-reduces loss values for logging; gradients are now all-reduced the
    # same way after backward(), so DDP's automatic sync is not needed for
    # correctness.
    ddp = model
    lr = 5e-5 if args.mode == 'lora' else 1e-5
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    if args.mode == 'full':
        # Full-SFT AdamW state (2 fp32 moments/param) plus DDP's full-model
        # replication per rank leaves no headroom on 140GB GPUs for
        # weighted_none's extra branch or for Gemma-3-12B at all; 8-bit
        # optimizer states remove ~75% of that overhead with the standard
        # AdamW update rule intact.
        import bitsandbytes as bnb
        optimizer = bnb.optim.AdamW8bit(trainable_params, lr=lr, weight_decay=.01)
    else:
        optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=.01)
    total_steps = 50 if args.smoke_only else args.steps
    log_path = out / 'logs/loss.csv'; (out / 'logs').mkdir(exist_ok=True)
    if rank == 0:
        log_path.write_text('step,total,decision,content,granularity,coarse_none,grad_norm,elapsed_sec\n')
        atomic_json(out / 'config.json', {'backbone':args.backbone,'mode':args.mode,'variant':args.variant,'lr':lr,'steps':total_steps,'gradient_accumulation':args.grad_accum,'world_size':world,'lora_targets':targets,'trainable_parameters':sum(p.numel() for p in model.parameters() if p.requires_grad),'decision_score':'mean token logP(<SPEAK>) - mean token logP(<SILENT>)','loss':'Ld + Lc + 0.5*Lg','none_policy':'masked' if args.variant=='no_none' else 'separate positive group weight 0.25','optimizer':'bitsandbytes.optim.AdamW8bit' if args.mode=='full' else 'torch.optim.AdamW'})
    started=time.time(); recent=[]; optimizer.zero_grad(set_to_none=True); accumulated_values = torch.zeros(5, device=device)
    if os.environ.get('MEM_SNAPSHOT') and rank == 0:
        torch.cuda.memory._record_memory_history(max_entries=100000)
    handle = (ROOT / 'data/dense_train.jsonl').open('rb')
    try:
      for micro_step in range(total_steps * args.grad_accum):
        step = micro_step // args.grad_accum
        role=choose_role(micro_step, rank); row, video, meta, actual = next_decodable(handle, pools[role], rank, role)
        # canonical video is decoded once, then shared in memory across C/F.
        c_in=make_prompt_inputs(row,'COARSE',processor,video,meta); f_in=make_prompt_inputs(row,'FINE',processor,video,meta)
        if os.environ.get('MEM_DEBUG'):
            print(json.dumps({'dbg':'row','micro_step':micro_step,'rank':rank,'role':role,'dataset':row['dataset'],'video_id':row['video_id'],'c_seq':int(c_in['input_ids'].shape[1]),'f_seq':int(f_in['input_ids'].shape[1]),'mem_before_fwd_gb':torch.cuda.memory_allocated(device)/1e9}),flush=True)
        c_content=content_tokens(processor.tokenizer,row['coarse_target']) if row['coarse_decision']=='SPEAK' else torch.empty((1,0),dtype=torch.long)
        f_content=content_tokens(processor.tokenizer,row['fine_target']) if row['fine_decision']=='SPEAK' else torch.empty((1,0),dtype=torch.long)
        c_d,c_l,s_c=branch(ddp,c_in,row['coarse_decision'],c_content,speak_tokens,silent_tokens,device,need_score=True)
        if os.environ.get('MEM_DEBUG'):
            print(json.dumps({'dbg':'after_coarse_branch','micro_step':micro_step,'rank':rank,'mem_gb':torch.cuda.memory_allocated(device)/1e9,'reserved_gb':torch.cuda.memory_reserved(device)/1e9,'peak_gb':torch.cuda.max_memory_allocated(device)/1e9}),flush=True)
        if os.environ.get('MEM_SNAPSHOT') and rank == 0 and micro_step == 0:
            torch.cuda.memory._dump_snapshot('/tmp/oom_snapshot2.pickle')
            torch.cuda.memory._record_memory_history(enabled=None)
            print(json.dumps({'dbg':'snapshot_dumped'}), flush=True)
            sys.exit(0)
        f_d,f_l,s_f=branch(ddp,f_in,row['fine_decision'],f_content,speak_tokens,silent_tokens,device,need_score=True)
        if os.environ.get('MEM_DEBUG'):
            print(json.dumps({'dbg':'after_fine_branch','micro_step':micro_step,'rank':rank,'mem_gb':torch.cuda.memory_allocated(device)/1e9,'peak_gb':torch.cuda.max_memory_allocated(device)/1e9}),flush=True)
        anchor=s_c*0+s_f*0
        # The schedule selects separate C+/C-/F+/F- roles.  Branch forwards
        # are shared with L_gran but their CE enters only in its selected role,
        # making both optimizer-facing decision marginals exactly 1:1.
        base_c = role in ('coarse_pos','coarse_bg')
        cdb=allmean(c_d if base_c else anchor, int(base_c), world)
        ccb=allmean(c_l if role == 'coarse_pos' else anchor, int(role == 'coarse_pos'), world)
        f_base = role in ('fine_pos','fine_neg')
        fdm=allmean(f_d if f_base else anchor,int(f_base),world)
        fcm=allmean(f_l if role == 'fine_pos' else anchor,int(role == 'fine_pos'),world)
        if args.variant=='weighted_none':
            nrow,nvideo,nmeta,_=next_decodable(handle,pools['coarse_none'],rank,'coarse_none'); n_in=make_prompt_inputs(nrow,'COARSE',processor,nvideo,nmeta)
            ncontent=content_tokens(processor.tokenizer,nrow['coarse_target'])
            nd,nc,_=branch(ddp,n_in,'SPEAK',ncontent,speak_tokens,silent_tokens,device,need_score=False)
            nd=allmean(nd,1,world); nc=allmean(nc,1,world)
            cd=(cdb+.25*nd)/1.25; cc=(ccb+.25*nc)/1.25
        else:
            nd=anchor; nc=anchor; cd=cdb; cc=ccb
        ld=.5*(cd+fdm); lc=.5*(cc+fcm)
        if row['pair_state']=='FINE_ONLY': lg_local=F.softplus(-(s_f-s_c)); lg_count=1
        elif row['pair_state']=='COARSE_ONLY': lg_local=F.softplus(-(s_c-s_f)); lg_count=1
        else: lg_local=anchor; lg_count=0
        # Directional means are globally balanced by the fixed DDP role schedule.
        lg=allmean(lg_local,lg_count,world)
        loss=ld+lc+.5*lg
        if not torch.isfinite(loss): raise RuntimeError(f'Non-finite loss at step {step}, rank {rank}')
        update = (micro_step + 1) % args.grad_accum == 0
        (loss / args.grad_accum).backward()
        values=torch.stack([loss.detach(),ld.detach(),lc.detach(),lg.detach(),nd.detach()]); dist.all_reduce(values); values/=world
        accumulated_values += values
        if not update:
            continue
        if world > 1:
            # Manual replacement for DDP's automatic gradient sync (see note
            # at ddp construction above): average each trainable param's
            # locally-accumulated gradient across ranks before stepping.
            for p in trainable_params:
                if p.grad is not None:
                    dist.all_reduce(p.grad)
                    p.grad /= world
        norm=torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
        if not torch.isfinite(norm) or norm <= 0: raise RuntimeError(f'Invalid gradient norm {norm}')
        optimizer.step(); optimizer.zero_grad(set_to_none=True)
        values = accumulated_values / args.grad_accum; accumulated_values.zero_()
        recent.append(float(values[0])); elapsed=time.time()-started
        if rank==0:
            with log_path.open('a') as h: h.write(f'{step+1},{values[0].item()},{values[1].item()},{values[2].item()},{values[3].item()},{values[4].item()},{float(norm)},{elapsed}\n')
            if step==49:
                save_status={'status':'passed','steps':50,'finite_losses':True,'finite_gradients':True,'canonical_shared_visual_prefix':True,'last_loss':values[0].item()}
                atomic_json(out/'reports/smoke_results.json',save_status)
            if (step+1)%25==0 or step==0: print(json.dumps({'step':step+1,'loss':values[0].item(),'Ld':values[1].item(),'Lc':values[2].item(),'Lg':values[3].item(),'elapsed_sec':elapsed}),flush=True)
        if step+1 in (50,400,800,total_steps): save_checkpoint(ddp,processor,out/'checkpoints'/('smoke' if step+1==50 else f'step_{step+1:04d}' if step+1<total_steps else 'final'),args.backbone,args.mode,args.variant,step+1,sum(p.numel() for p in model.parameters() if p.requires_grad))
      if rank==0:
        atomic_json(out/'reports/training_results.json',{'status':'completed','steps':total_steps,'backbone':args.backbone,'mode':args.mode,'variant':args.variant,'final_loss':recent[-1],'mean_last_50_loss':sum(recent[-50:])/len(recent[-50:]),'wall_clock_hours':(time.time()-started)/3600,'trainable_parameters':sum(p.numel() for p in model.parameters() if p.requires_grad)})
    finally:
      handle.close(); dist.destroy_process_group()

if __name__=='__main__': main()
