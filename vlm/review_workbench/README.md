# Review workbench

## 1. What this is

A multi-reviewer human terminal-review tool for the 500×2 (coarse+fine)
M-v4.2 draft annotations produced by the automated pipeline (see
`../RUNBOOK.md`, `../METHODS.md`). Reviewers claim videos, watch them, and
fix only the segments that are wrong — this is a **default-pass** system: a
segment nobody touches is not "unreviewed," it's "reviewed and judged
correct," and is carried into the final output unchanged once its video is
marked done. Every correction is appended to a per-video log under
`../corrections/` (never overwrites anything); `merge_corrections.py` replays
those logs on top of the read-only QC jsonl to produce the final gold. The
QC/draft jsonl files this reads are never written to by any part of this
tool.

## 2. Setup

**Requirements:** Python 3.9+, Linux or macOS (the server uses `fcntl` for
file locking, which doesn't exist on Windows). Nothing to `pip install` for
the workbench itself — `http.server`/`fcntl`/`json` are all stdlib. The
optional Chinese→English translation feature additionally needs the
`openai` package (already a repo dependency, see `../requirements.txt`) and
a reachable vLLM instance; **if either is missing, the server still starts
and runs fine** — translation just falls back to local format-normalization
only, with no crash and no separate flag to set (see §5).

**Data prerequisites** (must already exist — produced by the earlier
pipeline stages, not by this tool):
- `outputs/final/annotations_{coarse,fine}_qc.jsonl` — the read-only QC
  base every review sits on top of.
- `outputs/final/review_priority.json` — video ordering/tiering and the
  `failed_final` list (videos with no QC data to review).
- The keep-set mp4s, on disk somewhere reachable from this machine.

**Video directory:** point `--video-dir` (or the `EGOPROACTIVE_VIDEO_DIR`
env var) at the directory containing the keep-set `.mp4` files. No copying
or symlinking into this repo is needed — the server streams directly from
wherever you point it, with HTTP Range support (required for the player's
seek-while-scrubbing to work).

All commands below are run from the **`vlm/`** directory (not the repo
root, and not from inside `review_workbench/` itself):

```bash
cd vlm
export EGOPROACTIVE_VIDEO_DIR=/path/to/keepset/mp4s   # or pass --video-dir
python3 review_workbench/init_assignment.py           # (re)builds assignment.json from review_priority.json
python3 review_workbench/server.py --port 8910 --video-dir "$EGOPROACTIVE_VIDEO_DIR"
```

Open `http://<host>:8910/`. `init_assignment.py` is safe to re-run — it
refreshes video metadata (domain/duration/segment counts/flags) but never
resets an existing claim or status, so re-running it after new QC output
lands does not disturb reviewers mid-session.

**Multi-reviewer access:** run one server instance; everyone points at the
same host/port so they share one `assignment.json` and one `corrections/`
directory (claim exclusivity depends on this — two separate instances would
let two people claim the same video). If reviewers aren't on the same
network as the host, forward the port over SSH instead of exposing it
publicly:

```bash
ssh -L 8910:localhost:8910 user@host    # run on each reviewer's machine
# then open http://localhost:8910/ locally
```

## 3. Workflow

> Screenshots aren't included in this revision — the author generating this
> doc doesn't have browser-automation tooling available to capture real ones
> without fabricating something misleading. Placeholders are marked below;
> add real screenshots under `docs/` (`docs/index.png`, `docs/workbench.png`,
> `docs/claim.png`) and reference them here when available.

1. Open the index page. First visit asks for your reviewer name (stored in
   a cookie — same browser, same name, until you change it).
2. **Claim work**: click a video's `#` to claim it and jump straight into
   the workbench, or use the range box (e.g. `0051-0100`) to claim a whole
   block at once. Filters (`only mine` / `only unclaimed` / by tier / by
   status) help you find what to work on; rows claimed by someone else are
   greyed out and not clickable.

   `[index.png placeholder]`

3. **Review one video**: the video plays, with a coarse and a fine timeline
   underneath and two scrollable segment-list columns.
   - Press `B` to enter **boundary skim mode** — it auto-plays ±2s around
     each boundary in turn, so you can sanity-check every cut without
     manually scrubbing.
   - **Only touch segments that are actually wrong.** Everything else is
     already correct-by-default; leaving it alone is the expected outcome
     for most segments in most videos.
   - Fix what needs fixing with the row buttons (or keyboard shortcuts,
     §4) — retime, edit, merge, delete, add.
   - When the whole video looks right, press `Shift+D` (or the "✓ Mark
     video done" button). This marks it done and automatically jumps you to
     your next claimed-but-unfinished video.

   `[workbench.png placeholder]`

4. Repeat until your claimed range is done. Progress (yours and everyone
   else's) is visible on the index page at all times.

## 4. Keyboard reference

Matches the in-page `?` overlay exactly.

| Key | Action |
|---|---|
| `j` / `k` | select next/prev segment in the active column, seek to end&minus;1.5s |
| `Tab` | switch active column between coarse and fine |
| `1`&ndash;`4` | playback speed |
| `B` | boundary skim mode (auto-plays &plusmn;2s around each boundary, advances automatically) |
| `t` | retime selected segment's `end_time` to the current playhead |
| `[` / `]` | nudge `end_time` &mp;0.1s (Shift: &mp;0.5s) |
| `e` | edit summary — opens a popup, **pauses the video**, type or click &#127908; to speak (Chinese or English; always previewed/translated before it commits, see §5) |
| `d` | flip a directional verb in the summary (insert&harr;remove, screw&harr;unscrew, open&harr;close, attach&harr;detach, plug&harr;unplug) |
| `i` | toggle segment `type` between `action`/`idle` |
| `m` | merge selected segment into the next one |
| `x` | delete selected segment (confirms first) |
| `n` | add a boundary wherever the playhead currently is, in the active column — opens the same popup as `e` |
| `u` | undo the most recent action on the selected segment |
| `Shift+D` | mark this video done, jump to your next claimed-unfinished video |
| `?` | toggle this shortcut list |

Every one of these also has an on-screen button — the keyboard is a speed
option, not a requirement.

## 5. Correction semantics

**The five actions, precisely:**

- **retime** — sets a segment's `end_time` to a specific value (the current
  playhead via `t`, or a small nudge via `[`/`]`). The server clamps it to
  stay strictly between the previous and next segment's boundaries, so a
  retime can never invert order or collapse a segment to zero length.
- **edit** — replaces a segment's `summary` text (and/or its `type`,
  action/idle). Free text, typed or spoken, English or Chinese.
- **merge** — the **current** segment is absorbed into the **next** one,
  which survives: the merged segment's `end_time` is the next segment's
  (unchanged) `end_time`, its `summary` is the **next** segment's summary
  (not the current one's — if you want the current segment's wording to
  survive, edit the merged result afterward), and `boundary_confidence` is
  the minimum of the two. `merge_info.merged_from` accumulates.
- **delete** — removes a segment; its time span is absorbed by the
  **previous** segment (previous segment's `end_time` extends to cover it).
  If you delete the very first segment (no previous one exists), the next
  segment's start simply becomes 0 — no other change needed.
- **add** — splits whatever segment currently contains the playhead into
  two at that exact instant. The first half keeps the original segment's
  summary/confidence (it's a continuation of what was already there); the
  second half is the genuinely new segment and gets whatever summary you
  type/speak. Rejected with a clear error if the playhead is exactly on an
  existing boundary rather than strictly inside a segment.

**Undo (`u`)** targets a specific prior action by its log sequence number
(`seq`), not "the last thing anyone did" — each segment remembers which
`seq` most recently touched it, and undo tells the replay to skip that one
line as if it never happened. Because the whole segment list is recomputed
fresh from the log every time, this correctly reverses a merge/delete/add
too (skipping that line restores the segment layout it would otherwise have
produced) — it isn't limited to simple text edits. A segment nothing has
ever touched has nothing to undo (the button is disabled).

**Default-pass, precisely:** a segment with zero corrections against it is
emitted into the final gold byte-for-byte as it appears in the QC jsonl. A
segment only gets marked reviewed once its **whole video** is marked done
(`Shift+D`) — `merge_corrections.py` sets `human_reviewed: true` on every
segment of a done video (touched or not) and `false` on every segment of a
video nobody has finished yet, even if it was partially edited. This means
a half-reviewed video's current state is still visible/usable in the merged
output, just correctly flagged as not-yet-signed-off.

**Chinese input / voice input / translation:** any summary you type or speak
goes through a two-step confirm: click/press once and the server translates
(if it detects Chinese) and format-normalizes the text, showing you exactly
what will be saved; click/press again to commit it. Format normalization
lowercases ordinary words but preserves acronym-looking tokens (`LED`,
`M&M's`) as typed, matching the existing corpus's convention. If no vLLM
instance is reachable, non-Chinese text still gets normalized locally (no
network dependency for plain English edits); Chinese text falls back to
being normalized as-is (untranslated) rather than blocking your edit — check
the result before confirming if you're not sure translation actually ran.
Voice input uses the browser's built-in speech recognition (Chrome/Edge;
needs network access to the browser vendor's speech service) and reports
plainly when it's unavailable rather than failing silently.

## 6. Data & merge

**`corrections/{file_no}_{video_id}.jsonl`** — one file per video, one JSON
object per line, append-only:

```json
{"seq": 3, "ts": 1786911777.94, "reviewer": "alice", "file_no": "0001",
 "video_id": "01e536365b8b57ad", "granularity": "fine", "seg_index": 2,
 "action": "edit", "payload": {"summary": "hand opens the lid"}}
```

| field | meaning |
|---|---|
| `seq` | monotonic per-video counter (across both granularities); what `undo` targets |
| `ts` | unix timestamp |
| `reviewer` | who did it |
| `file_no` / `video_id` | which video |
| `granularity` | `coarse` or `fine` (or `video` for the `mark_done` bookkeeping line) |
| `seg_index` | which segment, in the list state *at the moment this action was submitted* (`null` for `undo`/`mark_done`) |
| `action` | `retime` \| `edit` \| `merge` \| `delete` \| `add` \| `undo` \| `mark_done` |
| `payload` | action-specific; `edit`/`add` carry `summary` (final English/normalized text) and, if translated, `summary_raw` (what the reviewer actually typed/spoke, kept for traceability) |

**`merge_corrections.py`** — reads `assignment.json` + every
`corrections/*.jsonl` + the QC jsonl, replays each video, writes
`../outputs/final/annotations_{coarse,fine}_final.jsonl`. Safe to re-run any
time (idempotent, read-only on all its inputs). Output schema = the QC
schema plus one added field per record: `human_reviewed` (bool, see §5).
Its input/output paths resolve relative to the script's own location, not
your shell's current directory, so (unlike most scripts here) it's safe to
invoke via a full/relative path from outside `vlm/` too, not just from
`vlm/` itself:

```bash
python3 review_workbench/merge_corrections.py
python3 review_workbench/merge_corrections.py --out-dir /somewhere/else   # optional
```

The printed summary breaks down how many videos are `human_reviewed=true`,
how many were touched by at least one correction, and how many are still
pure default-pass.

**Concurrency / claim mutex:** claiming and every action-log append go
through an `fcntl.flock` exclusive lock on `assignment.json` (for claims) or
that video's own log file (for actions), so two simultaneous claims on the
same video, or two simultaneous writes to the same video's log, can't race —
exactly one wins, the other gets a clear rejection. A video claimed by
someone else shows as greyed-out and non-enterable on the index; releasing
an unfinished claim (button on the index row) returns it to the unclaimed
pool. A **done** video's claim cannot be released back to unclaimed by
mistake — release only clears the claim on in-progress videos.

## 7. Reviewer guide

**Coarse** = one **subtask**: a self-contained operation that accomplishes a
recognizable intermediate goal of the overall task (e.g. "peels the sticker
backing", "spreads glue on the notebook cover", "washes the cutting board").
Ask: *has one intermediate goal just been achieved?* — if yes, the boundary
belongs there. Picking up/adjusting/putting down a tool within the same
goal does not start a new segment.

**Fine** = one **atomic action**: a new segment begins when either the
manipulated object changes, or the verb on the same object changes (e.g.
"picks up the bulb" → "unscrews the bulb"; "holds the board" → "flips the
board"). Which hand performs the action is *not* a boundary by itself —
only a genuine hand-to-hand transfer is (see the hallucination note below).
Sustained repetition of the same verb+object is one segment regardless of
duration.

**Common error types to watch for**, each with a real example from this
pipeline's own development history (see `../METHODS.md` for the full
account):

| Type | What it looks like | Example |
|---|---|---|
| **Direction reversed** | insert/remove, screw/unscrew, open/close, attach/detach, plug/unplug flipped | model says "removes the battery from the flashlight" when the footage shows inserting it — the pipeline's known open issue (`../METHODS.md` §5), not fully solved automatically. Use `d` to flip once you've confirmed the true direction from the video. |
| **Hallucination** | an action, hand, or object that isn't actually in frame | earlier pipeline versions invented a second hand or mislabeled left/right on single-hand footage (`../METHODS.md` §2.6) — fixed for that specific case, but treat any hand-identity claim with suspicion if only one hand is ever visible. |
| **Boundary drift** | the cut is real, but the timestamp is a beat early/late | use `t` while scrubbing, or `[`/`]` for a fine nudge, rather than deleting and re-adding. |
| **Over-merged** | one segment actually covers two distinct actions | use `n` to split at the true transition point. |
| **Over-split** | two adjacent segments are really one continuous action artificially cut in half (or the auto-fixer flagged but didn't catch a repeated near-duplicate) | use `m` to merge; check the merged segment's summary afterward (merge always keeps the *next* segment's wording, see §5). |

**When you're not sure:** don't guess. Leave the segment as-is (default-pass
covers it) and note your uncertainty via an `edit` that appends a short
parenthetical to the summary (e.g. "... (uncertain: direction unclear)")
rather than silently forcing a judgment call the footage doesn't actually
support. A visible, honest "not sure" is more useful downstream than a
confident guess.

## 8. FAQ

**Video won't load / spinner forever.** Almost always `--video-dir` (or
`EGOPROACTIVE_VIDEO_DIR`) pointing at the wrong place, or the file missing
from that directory — the server logs a clear warning at startup if the
directory itself doesn't exist, but a missing individual file just 404s
silently in the browser. Check the server's stdout/log for the actual path
it's serving from.

**Will I lose progress if my browser crashes / the server restarts / power
goes out?** No. Every action is `POST`ed and fsync'd to its log file the
moment you take it — there's no "unsaved" client-side state to lose (except
whatever you're mid-typing in an open edit popup that you haven't confirmed
yet). Reopening the same video replays the log fresh and shows you exactly
where you left off.

**How do I release a video I claimed but don't want to finish?** Click
"release" next to your name on that row in the index page. It returns to
the unclaimed pool for anyone (including you) to claim again. A video
already marked done cannot be accidentally released this way.

**How do I undo something?** Select the segment (click it or `j`/`k` to it)
and press `u`, or click its "Undo" button — this is per-segment and targets
the most recent action *on that specific segment*, not a global undo stack.
If the button/key is disabled, that segment hasn't been touched by anything
undoable yet.

**What if I disagree with how `merge` picks the surviving summary?** Merge
is mechanical (always keeps the next segment's summary, see §5) — if that's
not the wording you want, just `edit` the result immediately afterward.
