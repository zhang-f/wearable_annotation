# corrections/

Append-only per-video action logs written by `review_workbench/server.py` as
reviewers edit segments (`{file_no}_{video_id}.jsonl`, one line per action).
This is generated review-session data, not source — it's gitignored (see
`.gitignore`) and regenerates from scratch as reviewers work. See
`vlm/review_workbench/README.md` for the log format and how
`merge_corrections.py` replays it into the final gold.
