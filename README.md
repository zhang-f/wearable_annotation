# EgoProactive interrupt-timing annotator

A small local tool for hand-annotating **when an AI assistant should speak up**
while watching a first-person (egocentric) video of someone doing a task —
at three different granularities (free / coarse / fine). The point of the
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
the task definition, the order to annotate the three granularities in, and
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
tool/                       the annotator (server.py + index.html)
docs/ANNOTATION_SOP.md       what to annotate and how — read before starting
annotations/                 your output lands here (gitignored except .gitkeep)
scripts/                     analysis scripts (agreement/overlap between annotators)
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
