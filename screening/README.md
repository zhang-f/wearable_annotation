# Screening the 700 EgoProactive videos

`screening.html` is a standalone page to hand-screen all 700 videos — mark each
**keep / unsure / drop** for suitability for multi-granularity segmentation, then
export your decisions to send back. Marks are saved in your browser
(localStorage) as you go, so it's safe to close and resume across sessions.

Everything here reads only `../tool/wearable_ai_2026_egoproactive_val_700.jsonl`
(already in the repo). No video files are included — the gated dataset is
downloaded separately (see the main repo README).

## Option A — screen with video playback (recommended)
1. Download the videos into `videos/` at the **repo root** (main README → "Get the
   videos"; gated, ~23GB).
2. From the **repo root**, serve with Range support (needed for seeking):
   ```
   python3 vlm/serve_review.py --dir . --port 8768
   ```
3. Open **http://localhost:8768/screening/screening.html**

## Option B — screen by text only (no download, no server)
Open `screening/screening.html` directly in a browser (`file://`). Everything
works except the ▶ play links (those need the videos + the server).

## Using it
- Filter by **domain**, **sort by duration**, **search** task/query/id, and
  **Group by task** so duplicate tasks cluster (112 tasks have >1 recording — you
  can batch-decide those).
- Per row: **keep / unsure / drop** (click the active one again to clear). Live
  counts up top.
- **⬇ Export decisions** downloads `screening_decisions.json` —
  `[{video_path, decision}]` for all 700 (`decision` is `"unmarked"` until set).
  Send that file back.

## Regenerating the page
```
cd screening && python3 make_screening.py     # -> screening/screening.html
```
