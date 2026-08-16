# EgoProactive interrupt-timing annotator

A small local tool for hand-annotating **when an AI assistant should speak up**
while watching a first-person (egocentric) video of someone doing a task —
at two different granularities (coarse / fine). The point of the
project is to measure how much people *disagree* about the right moment to
interrupt, at different levels of granularity — see
[`docs/ANNOTATION_SOP.md`](docs/ANNOTATION_SOP.md) for the actual task.

## 1. Get the videos (not included in this repo — ~23GB)

Videos are **not** checked into this repo (GitHub can't hold 23GB of mp4s).
Download them from Hugging Face into `videos/` at the repo root:

```bash
pip install -U "huggingface_hub[cli]"
mkdir -p videos
huggingface-cli download facebook/wearable-ai --repo-type dataset \
    --include "egoproactive/val/*" --local-dir ./hf_download
mv hf_download/egoproactive/val/* videos/
rm -rf hf_download
```

`facebook/wearable-ai` is a gated dataset — if the download fails with a
permission error, visit https://huggingface.co/datasets/facebook/wearable-ai,
accept the terms, and make sure you're logged in locally (`huggingface-cli
login`) before retrying.

If you were given a specific subset list instead of the full ~700 videos,
only download those filenames (ask whoever sent you this repo).

The small metadata file (`tool/wearable_ai_2026_egoproactive_val_700.jsonl`
— query/task/domain per video) is already included in this repo, no
separate download needed for that.

## 2. Start the tool

Python 3.9+, no packages required for the core tool (translation is
optional, see below).

```bash
cd tool
python3 server.py
```

Then open **http://localhost:8765/** in your browser. If your videos aren't
in the default `videos/` folder at the repo root, point at them explicitly:

```bash
python3 server.py --video-dir /path/to/your/videos
```

The first time you open the page, it'll ask for an annotator ID (your name
or initials) — this is stored in your browser and used to tag your results
and name your output file, so it's asked once, not every time.

## 3. Annotate

Read **[`docs/ANNOTATION_SOP.md`](docs/ANNOTATION_SOP.md) first** — it has
the task definition, the order to annotate the two granularities in, and
one rule that matters more than the others: **don't compare notes with
other annotators while you're doing this.** (Explained in the SOP — it's
not an oversight, disagreement between annotators is the actual data we
need.)

Everything you mark is saved to disk immediately as you go (no save
button, safe to close the window anytime) into
`annotations/annotations_<your-id>_<date>.jsonl`.

## 4. Send your results back

When you're done (or want to send partial progress), just send back your
`annotations/annotations_<your-id>_<date>.jsonl` file — email, shared
drive, Slack, whatever's easiest. You don't need git access to this repo
to do this.

## Repo layout

```
tool/                       the human annotator (server.py + index.html)
docs/ANNOTATION_SOP.md       what to annotate and how — read before starting
annotations/                 your output lands here (gitignored except .gitkeep)
scripts/                     analysis scripts (agreement/overlap between annotators)
vlm/                         VLM auto-annotation pipeline (parallel/complementary to tool/, see below)
videos/                      put downloaded videos here (gitignored)
```

## Optional: Chinese-note-to-English translation

When you mark a point, a small popup lets you jot a quick note in Chinese
(optional — you can also just type directly into the English field in the
marks list, or leave it blank). If you type Chinese and hit Enter, it's
translated to English automatically and only the English is saved (the
Chinese itself is never written to disk).

This uses a local model (Qwen3-8B, ~16GB) downloaded automatically the
first time you use it, and needs a GPU with ~16GB free VRAM to run at a
reasonable speed (CPU works but is slow). If you don't have that, it's not
required — just type your descriptions in English directly, or leave them
blank. A failed/skipped translation never blocks marking or saving.

## VLM module (`vlm/`)

A parallel, complementary pipeline to `tool/`: instead of a human marking
interrupt points by hand, a vision-language model watches the video and
proposes segment boundaries + one-sentence summaries automatically. This
is meant to (a) bootstrap examples for few-shot prompting, and (b)
eventually scale annotation beyond what's practical by hand. It does
**not** replace `tool/` or the human SOP — VLM output is a draft, reviewed
and corrected by a human (via `vlm/build_review.py`'s generated
`review.html`) before it's trusted for anything. For the full 500-video
batch specifically, human review happens through a dedicated
multi-reviewer tool — see
[`vlm/review_workbench/README.md`](vlm/review_workbench/README.md).

### Granularity (same two tiers as `docs/ANNOTATION_SOP.md`, not three)

- **coarse** — one segment per subtask/major step. Boundary = the moment
  the subtask is *visibly complete* (hand releases the object and/or
  attention shifts onward), not when prep for the next step begins.
- **fine** — one segment per identifiable sub-action. Boundary = a
  **hand-object change**: the instant either hand's held/operated object
  changes (picked up, put down, switched hands, or turns to a different
  object). Every sub-action counts, including brief ones.

(The tool's UI historically also had a `free` tier for unconstrained human
pacing; that's a manual-annotation-only concept and doesn't apply to the
VLM pipeline, which only ever runs coarse/fine.)

### Environment

- **ffmpeg with drawtext** (needs libfreetype) — used to burn `t=XX.Xs`
  timestamps into extracted frames so the VLM can read exact times off the
  image instead of guessing from frame order. Check with:
  ```bash
  ffmpeg -filters 2>&1 | grep drawtext
  ```
  `annotate.py` also needs an actual `.ttf` file on disk for the filter's
  `fontfile=` argument; it auto-detects a few common Debian/Ubuntu paths
  (see `FONT_FILE_CANDIDATES` in `annotate.py`) and falls back to
  `--font-file /path/to/some.ttf` if none are found. On Debian/Ubuntu:
  `apt install fonts-dejavu-core`.
- **Python packages**: see `vlm/requirements.txt` (`openai`, used as an
  OpenAI-compatible client against your own local vLLM server — no
  external API calls, no API key needed).
- **vLLM serving convention**: `annotate.py` expects an OpenAI-compatible
  endpoint at `http://localhost:8000/v1` (see `VLM_BASE_URL` in
  `annotate.py`) serving a model under the name in `VLM_MODEL`
  (`Qwen3-VL-8B-Instruct`). `vllm` itself is **not** in requirements.txt —
  install/version-pin it separately for your GPU setup. Example:
  ```bash
  vllm serve Qwen/Qwen3-VL-8B-Instruct \
      --served-model-name Qwen3-VL-8B-Instruct \
      --port 8000 --max-model-len 98304 \
      --limit-mm-per-prompt '{"image": 128}'
  ```
  The context/image limits matter: a full-video Stage1 pass at a higher
  `--s1_fps` can need 50k+ prompt tokens and 60-100+ images for a ~40s
  clip — undersized `--max-model-len` or `--limit-mm-per-prompt` will
  fail requests. Size these up for longer videos.

### Bootstrap quick start

```bash
cd vlm
pip install -r requirements.txt
# ... start vllm serve in another terminal/session, see above ...

python3 annotate.py --granularity coarse --out my_coarse.jsonl --limit 1
python3 annotate.py --granularity fine   --out my_fine.jsonl   --limit 1
python3 build_review.py --coarse my_coarse.jsonl --fine my_fine.jsonl --out-dir .
python3 serve_review.py --dir .
# open http://localhost:8768/review.html
```

`--jsonl`/`--video_dir` default to this repo's own conventions
(`tool/wearable_ai_2026_egoproactive_val_700.jsonl` and `videos/`) so no
path flags are needed once videos are downloaded per step 1 above.
`vlm/examples/` has a real worked example (`selected.jsonl` +
`bootstrap_coarse.jsonl` + `bootstrap_fine.jsonl`) from one video, if you
want to see expected output shape without running the VLM yourself.

### Deploy on a new machine

```bash
git clone git@github.com:zhang-f/wearable_annotation.git
cd wearable_annotation

# 1. videos (see "Get the videos" above for the gated-dataset caveat)
pip install -U "huggingface_hub[cli]"
mkdir -p videos
huggingface-cli download facebook/wearable-ai --repo-type dataset \
    --include "egoproactive/val/*" --local-dir ./hf_download
mv hf_download/egoproactive/val/* videos/
rm -rf hf_download

# 2. VLM deps + font (Debian/Ubuntu)
sudo apt install -y ffmpeg fonts-dejavu-core
cd vlm && pip install -r requirements.txt

# 3. serve the model (separate terminal/session; adjust for your GPU count/VRAM)
vllm serve Qwen/Qwen3-VL-8B-Instruct \
    --served-model-name Qwen3-VL-8B-Instruct \
    --port 8000 --max-model-len 98304 \
    --limit-mm-per-prompt '{"image": 128}'

# 4. smoke test on one video
python3 annotate.py --granularity coarse --out /tmp/smoke_coarse.jsonl --limit 1
```
