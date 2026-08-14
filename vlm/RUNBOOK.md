# RUNBOOK — M-v4 annotation, single-video production chain

Operational guide to annotate **one video** through the frozen M-v4 chain, both
granularities. It documents the **production path only** (fresh full chain, no reuse of
prior archives). The per-**video** loop is intentionally *not* provided as a script — wrap
these steps yourself per §3 (see METHODS.md for the why/what of each layer).

Every step calls an entry point in an existing repo file; no step requires manual editing.

**Version note (2026-08-14): the chain in production is M-v4.2**, two small prompt-only
patches on top of the frozen M-v4 described below — no entry points, signatures, or file
layout changed, only `prompt_template_v3.md`'s text. See METHODS.md §2.11 (hand-transfer
capture) and §2.12 (no-person/unattended-machine spans emit no Pass A entries). §2.12's
caveat matters operationally: a long unattended-machine stretch is de-spammed but may not
be typed `type:"idle"` in the output — don't assume `idle` typing is exhaustive (METHODS §5).

---

## 0. Environment prerequisites

**Serving** — Qwen3-VL-8B-Instruct on GPU1 via vLLM (OpenAI API on port 8000):

```bash
CUDA_VISIBLE_DEVICES=1 python -m vllm.entrypoints.openai.api_server \
  --model <local-path-or-hf-id>/Qwen3-VL-8B-Instruct \
  --port 8000 \
  --max-model-len 98304 \
  --limit-mm-per-prompt image:660 \
  --mm-processor-kwargs '{"max_pixels": 150000}' \
  --enforce-eager
```
(`image:660` is the per-request frame ceiling the pipeline's 640 budget stays under;
`max_pixels 150000` ≈ 448px longest edge ≈ 140 tok/frame. Exact vLLM/torch versions are
machine-specific — see `vlm/requirements.txt`. `[需查证: pin versions on the target host]`.)

Health check: `curl -s localhost:8000/v1/models | jq -r '.data[0].id'` → `Qwen3-VL-8B-Instruct`.

**Frozen config in effect** (do not change; see METHODS.md §4): fps **coarse 2 / Pass A 5 /
Stage 2 8**; resolution **448px**; frame budget **660**; **temperature 0** (0.2 on retry);
`repetition_penalty` default-on for Pass A/B.

**Shell setup** (run once per video; `$VID` is the basename without `.mp4`):

```bash
cd /ssd/fan/wearable_annotation/vlm
source /ssd/fan/anaconda3/etc/profile.d/conda.sh && conda activate vlm
export JSONL=/ssd/fan/wearable_annotation/tool/wearable_ai_2026_egoproactive_val_700.jsonl
export VIDEO_DIR=/ssd/fan/wearable_annotation/videos          # symlink to the mp4 dir
export OUT=/path/to/output_dir                                # holds archives + annotations_*.jsonl
export VID=459e3ad53e531fca                                   # one video (basename)
mkdir -p "$OUT"/{global,coarse,narrations,fine_raw,fine_m}
```

---

## 1. Inputs, outputs, and intermediate-file flow

Input row for a video = the matching line of `$JSONL` (`{video_path, task, domain,
duration_in_sec, query}`). Frames are **never** persisted — each pass extracts to a private
`/tmp` temp dir and deletes it on exit (Python `TemporaryDirectory`).

```
$VIDEO_DIR/$VID.mp4
   │
   ├─(2.1 Pass 0, per VIDEO, 2→1→0.5→0.25 fps)──────────► $OUT/global/$VID.json
   │                                                          │ (task_understanding, phases)
   ├─(2.2 Pass 1 + Stage 2 coarse, per VIDEO, 2fps/8fps)─────►│ reads global ─► $OUT/coarse/$VID.json
   │                                                          │                  (coarse segments)
   ├─(2.3 Pass A, per COARSE SEGMENT, 5fps)── reads coarse ──► $OUT/narrations/$VID_fine.json
   │                                                          │  (per-segment {t,action})
   ├─(2.4 Pass B v4, per COARSE SEGMENT, text)─ reads narr ──► $OUT/fine_raw/$VID_fine.json
   │                                                          │  (atomic segs + idle, type)
   ├─(2.5 Pass M, per COARSE-SEG run, text)──── reads raw ───► $OUT/fine_m/$VID_fine.json
   │                                                          │  (merged fine, merge_info)
   └─(2.6 Stage 2 fine + assemble, per VIDEO, 8fps)─ reads coarse+global+fine_m ─►
                                        $OUT/annotations_coarse.jsonl  (append)
                                        $OUT/annotations_fine.jsonl    (append)
```

**Loop scope:** steps 2.1 / 2.2 / 2.6 run **once per video**; 2.3 / 2.4 iterate **over the
video's coarse segments** (that inner loop is inside each command). The **per-video** loop is
yours to add (§3).

Naming pattern (fixed): `global/<vid>.json`, `coarse/<vid>.json`,
`narrations/<vid>_fine.json`, `fine_raw/<vid>_fine.json`, `fine_m/<vid>_fine.json`, and the
two append-only outputs `annotations_{coarse,fine}.jsonl`.

---

## 2. The chain, step by step

Each command is copy-pasteable given §0's env vars.

### 2.1 Pass 0 — global understanding (per VIDEO)
Entry point: **`annotate_v3.pass0`** (prompt: `prompt_template_v3.md` `## PASS 0 PROMPT`).

```bash
python3 - <<'PY'
import os, json, tempfile
import annotate, annotate_v3 as v3
vid, OUT, VD = os.environ['VID'], os.environ['OUT'], os.environ['VIDEO_DIR']
annotate.FONT_FILE = annotate._find_font_file(None)
row = next(json.loads(l) for l in open(os.environ['JSONL']) if json.loads(l)['video_path'] == vid + '.mp4')
with tempfile.TemporaryDirectory(dir='/tmp') as wd:
    p0, fps, nfr = v3.pass0(row, os.path.join(VD, vid + '.mp4'), wd)
json.dump({**p0, 'pass0_fps': fps}, open(f"{OUT}/global/{vid}.json", 'w'), ensure_ascii=False, indent=1)
print('pass0:', fps, 'fps,', len(p0['phases']), 'phases')
PY
```
Output: `global/<vid>.json` = `{task_understanding, phases:[{description, approx_range}], pass0_fps}`.
Expected: a handful of phases; fps auto-dropped so `dur*fps ≤ 660`.
Self-check: `jq '.phases|length' "$OUT/global/$VID.json"`  → ≥ 1.

### 2.2 Pass 1 (coarse) + Stage 2 coarse (per VIDEO)
Entry points: **`annotate_v3.coarse_pass1`** then **`annotate_v3.stage2_v3(...,'coarse')`**
(prompts `## COARSE PASS 1 PROMPT`, `## STAGE 2 PROMPT`). Over-budget videos window
internally.

```bash
python3 - <<'PY'
import os, json, tempfile
import annotate, annotate_v3 as v3
vid, OUT, VD = os.environ['VID'], os.environ['OUT'], os.environ['VIDEO_DIR']
annotate.FONT_FILE = annotate._find_font_file(None)
row = next(json.loads(l) for l in open(os.environ['JSONL']) if json.loads(l)['video_path'] == vid + '.mp4')
video = os.path.join(VD, vid + '.mp4')
p0 = json.load(open(f"{OUT}/global/{vid}.json"))
with tempfile.TemporaryDirectory(dir='/tmp') as wd:
    coarse, va, cwin = v3.coarse_pass1(row, video, wd, {'task_understanding': p0['task_understanding'], 'phases': p0['phases']})
    s1 = [s['end_time'] for s in coarse]
    coarse = v3.stage2_v3(row, video, wd, coarse, 'coarse')
for i, s in enumerate(coarse):
    s['end_time_stage1'] = s1[i] if i < len(s1) else s['end_time']; s.setdefault('type', 'action')
json.dump({'segments': coarse, 'video_assessment': va, 'n_windows': cwin},
          open(f"{OUT}/coarse/{vid}.json", 'w'), ensure_ascii=False, indent=1)
print('coarse:', len(coarse), 'segs,', cwin, 'window(s)')
PY
```
Output: `coarse/<vid>.json` = `{segments:[{summary, end_time, end_time_stage1, boundary_confidence, type}], video_assessment, n_windows}`.
Expected: coarse = subtask-level segments; `end_time` strictly increasing; last ≈ duration.
Self-check: `jq '.segments|length' "$OUT/coarse/$VID.json"`  → ≥ 1.

### 2.3 Pass A — dense narration (per COARSE SEGMENT)
Entry points: **`annotate_v3._passA` + `build_fineA` + `_ex`**, looped over coarse segments
(coarse segments longer than the 128s budget are blind-cut into 90s/overlap-4s windows).
Prompt `## FINE PASS A PROMPT`.

```bash
python3 - <<'PY'
import os, json, tempfile
import annotate, annotate_v3 as v3
vid, OUT, VD = os.environ['VID'], os.environ['OUT'], os.environ['VIDEO_DIR']
annotate.FONT_FILE = annotate._find_font_file(None)
row = next(json.loads(l) for l in open(os.environ['JSONL']) if json.loads(l)['video_path'] == vid + '.mp4')
video = os.path.join(VD, vid + '.mp4')
coarse = json.load(open(f"{OUT}/coarse/{vid}.json"))['segments']
full, prev = [], 0.0
with tempfile.TemporaryDirectory(dir='/tmp') as wd:
    for sidx, cs in enumerate(coarse):
        ss, se = prev, cs['end_time']; prev = se
        if (se - ss) > v3.BLIND_THRESH_S:
            wins, s = [], ss
            while True:
                we = min(se, s + v3.BLIND_WIN_S); wins.append((s, we))
                if we >= se: break
                s += v3.BLIND_WIN_S - v3.BLIND_OVERLAP_S
        else:
            wins = [(ss, se)]
        narr = []
        for wi, (ws, we) in enumerate(wins):
            frames = v3._ex(video, wd, f"fa_{sidx}_{wi}", v3.FINE_FPS, ws, we)
            n, _ = v3._passA(v3.build_fineA(row, cs['summary'], ws, we, win=((ws, we) if len(wins) > 1 else None)), frames, f"seg{sidx}w{wi}")
            narr += n
        narr.sort(key=lambda e: e['t'])
        m = []
        for e in narr:
            if m and abs(e['t'] - m[-1]['t']) < 1.0 and e['action'] == m[-1]['action']: continue
            m.append(e)
        full.append({'coarse_idx': sidx, 'range': [round(ss, 1), round(se, 1)], 'coarse_summary': cs['summary'], 'narration': m})
json.dump(full, open(f"{OUT}/narrations/{vid}_fine.json", 'w'), ensure_ascii=False, indent=1)
print('passA:', sum(len(b['narration']) for b in full), 'entries over', len(full), 'coarse segs')
PY
```
Output: `narrations/<vid>_fine.json` = `[{coarse_idx, range:[ss,se], coarse_summary, narration:[{t, action}]}]`.
Expected: one block per coarse segment; `action` = `"<hand> <verb> <object>"`, single hand = `"hand"`.
Self-check: `jq '[.[].narration|length]|add' "$OUT/narrations/${VID}_fine.json"`  → > coarse count.

### 2.4 Pass B v4 — boundary derivation + explicit idle (per COARSE SEGMENT)
Entry point: **`rerun_passB_v4.passB_v4`**, text-only (no frames), per narration block.
Prompt `## FINE PASS B V4 PROMPT`.

```bash
python3 - <<'PY'
import os, json
import rerun_passB_v4 as v4b
vid, OUT = os.environ['VID'], os.environ['OUT']
task = next(json.loads(l) for l in open(os.environ['JSONL']) if json.loads(l)['video_path'] == vid + '.mp4').get('task', '')
raw = []
for blk in json.load(open(f"{OUT}/narrations/{vid}_fine.json")):
    ss, se = blk['range']
    for s in v4b.passB_v4({'task': task}, blk['coarse_summary'], ss, se, blk['narration']):
        s['coarse_idx'] = blk['coarse_idx']; raw.append(s)
json.dump(raw, open(f"{OUT}/fine_raw/{vid}_fine.json", 'w'), ensure_ascii=False, indent=1)
print('passB v4:', len(raw), 'raw segs,', sum(1 for s in raw if s.get('type') == 'idle'), 'idle')
PY
```
Output: `fine_raw/<vid>_fine.json` = `[{summary, end_time, boundary_confidence, type, coarse_idx}]`
(`type` ∈ {action, idle}; timing spans `[t_k, t_{k+1})`).
Self-check: `jq 'length' "$OUT/fine_raw/${VID}_fine.json"`  → ≥ coarse count.

### 2.5 Pass M — model semantic merge (per COARSE-SEG run)
Entry point: **`refine_fine.refine_M`** wrapped by **`rerun_passB_v4.refine_preserving_idle`**
(idle segments never merge), text-only. Prompt `## FINE REFINE M PROMPT`.

```bash
python3 - <<'PY'
import os, json
import rerun_passB_v4 as v4b, refine_fine as rf
vid, OUT = os.environ['VID'], os.environ['OUT']
task = next(json.loads(l) for l in open(os.environ['JSONL']) if json.loads(l)['video_path'] == vid + '.mp4').get('task', '')
csums = [s['summary'] for s in json.load(open(f"{OUT}/coarse/{vid}.json"))['segments']]
raw = json.load(open(f"{OUT}/fine_raw/{vid}_fine.json"))
fine = v4b.refine_preserving_idle(raw, lambda run: rf.refine_M(run, task, csums)[0])
json.dump(fine, open(f"{OUT}/fine_m/{vid}_fine.json", 'w'), ensure_ascii=False, indent=1)
print('passM:', len(fine), 'fine segs from', len(raw), 'raw')
PY
```
Output: `fine_m/<vid>_fine.json` = `[{summary, end_time, boundary_confidence, merge_info}]`
(+ `type` on idle rows). This is the fine segmentation **before** Stage 2.
Self-check: `jq 'length' "$OUT/fine_m/${VID}_fine.json"`  → ≤ raw count.

### 2.6 Stage 2 fine + assemble final records (per VIDEO)
Entry point: **`annotate_v3.stage2_v3(...,'fine')`**, then assemble the two output records
(validation via **`annotate_v2.validate`** + **`annotate_v3.phase_flags`**). Prompt
`## STAGE 2 PROMPT`.

```bash
python3 - <<'PY'
import os, json, tempfile
import annotate, annotate_v2 as v2, annotate_v3 as v3
vid, OUT, VD = os.environ['VID'], os.environ['OUT'], os.environ['VIDEO_DIR']
annotate.FONT_FILE = annotate._find_font_file(None)
row = next(json.loads(l) for l in open(os.environ['JSONL']) if json.loads(l)['video_path'] == vid + '.mp4')
video = os.path.join(VD, vid + '.mp4'); dur = row['duration_in_sec']
cd = json.load(open(f"{OUT}/coarse/{vid}.json")); coarse = cd['segments']
fine = json.load(open(f"{OUT}/fine_m/{vid}_fine.json"))
with tempfile.TemporaryDirectory(dir='/tmp') as wd:
    s1 = [s['end_time'] for s in fine]
    fine = v3.stage2_v3(row, video, wd, fine, 'fine')
for i, s in enumerate(fine):
    s['end_time_stage1'] = s1[i] if i < len(s1) else s['end_time']
    s.setdefault('type', 'action'); s.setdefault('merge_info', {'merged_from': 1, 'rule': None, 'source_indices': []})
p0 = json.load(open(f"{OUT}/global/{vid}.json"))
base = dict(video_path=vid + '.mp4', task=row.get('task', ''), domain=row.get('domain', ''),
            query=row.get('query', ''), duration_in_sec=dur,
            pass0={'task_understanding': p0['task_understanding'], 'phases': p0['phases'], 'pass0_fps': p0.get('pass0_fps')})
crec = dict(base, granularity='coarse', n_windows=cd['n_windows'], segments=coarse,
            video_assessment=cd['video_assessment'],
            validation_flags=v3.phase_flags(coarse, p0['phases']) + v2.validate(coarse, cd['video_assessment'], dur))
frec = dict(base, granularity='fine', segments=fine, video_assessment=cd['video_assessment'],
            validation_flags=v2.validate(fine, cd['video_assessment'], dur))
open(f"{OUT}/annotations_coarse.jsonl", 'a').write(json.dumps(crec, ensure_ascii=False) + '\n')
open(f"{OUT}/annotations_fine.jsonl", 'a').write(json.dumps(frec, ensure_ascii=False) + '\n')
print('done: coarse', len(coarse), '/ fine', len(fine), '-> annotations_{coarse,fine}.jsonl')
PY
```
Output (append): `annotations_coarse.jsonl`, `annotations_fine.jsonl`. Segment schema:
`{summary, end_time, end_time_stage1, boundary_confidence, type, merge_info}` (`merge_info`
carries real values only for fine); outer: `{video_path, task, domain, query, duration_in_sec,
pass0, granularity, n_windows(coarse), video_assessment, validation_flags}`. Fine
`video_assessment` is inherited from coarse (Pass B v4 emits none — see METHODS §5).
Self-check:
`for g in coarse fine; do jq -c 'select(.video_path=="'$VID'.mp4")|{g:.granularity,n:(.segments|length)}' "$OUT/annotations_$g.jsonl"; done`
→ fine count should be ≥ 2× coarse count.

---

## 3. Engineering conventions (for the per-video wrapper)

The per-video loop is a thin wrapper you write around §2 (there is **no** batch runner file in
this repo). It must honour:

- **Resume / dedup:** key on `(video_path, granularity)`. Skip a video whose `video_path`
  already appears in **both** `annotations_coarse.jsonl` and `annotations_fine.jsonl`. The
  per-video archives (`global/`, `coarse/`, `narrations/`, `fine_raw/`, `fine_m/`) also let a
  crashed video resume from its last completed step.
- **Retry (already inside the frozen chain — do not re-implement):** a parse failure is
  re-sent once (`annotate_v3._passA`/`_passB`, `coarse_pass1.call`, `refine_fine._call_M`,
  each `for attempt in (1,2)`); the retry uses `temperature 0.2` and adds
  `repetition_penalty=1.1` where it isn't already default.
- **Degeneration criterion (also inside the chain):** Pass A retries when the unique-entry
  ratio < 0.5 (`UNIQUE_RATIO`, `annotate_v3._passA`); Pass B retries when segment count >
  narration entries (`annotate_v3._passB`). Persist the raw output and mark the video
  `failed` if it still fails, then continue.
- **Circuit breaker:** stop the batch after **10 consecutive** videos failing with the same
  error category, and surface it for inspection.
- **Temp cleanup:** every step already extracts frames to a `TemporaryDirectory(dir='/tmp')`
  that is deleted on exit — never let frames accumulate. Keep an eye on free space if `/tmp`
  is small; the JSON archives themselves are tiny.
- **Progress:** log a line every 25 videos (done / failed / mean seconds / free disk).

Run the six steps of §2 in order per video; append-only outputs make the batch idempotent
under the resume rule above.
