#!/usr/bin/env python3
"""Build the independent 0.5 s COARSE/FINE decision timeline.

This is deliberately independent of pair states: labels are assigned to each
task first, then pair states are derived.  No temporal deletion or negative
spacing is applied here.
"""
import bisect
import collections
import csv
import json
import math
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import av
import numpy as np

PROJECT = Path('/data/fan/projects/procedure_forecasting')
ROOT = PROJECT / 'runs/granularity_aware_final_v1'
OLD = PROJECT / 'runs/granularity_aware_sft_v1'
V2 = PROJECT / 'runs/mg_sft_v2'
A101 = Path('/data/fan/datasets/assembly101')
EPIC = PROJECT / 'epic_hierarchy_qwen235b_v1'
GRID_SEC = 0.5
WINDOW_SEC = 8.0
FRAMES = 16


def read_json(path):
    return json.loads(Path(path).read_text())


def read_jsonl(path):
    with Path(path).open() as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def atomic_json(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)


def norm(value):
    return re.sub(r'\s+', ' ', str(value or '').strip())


def stream_meta(video_path):
    with av.open(video_path) as container:
        stream = container.streams.video[0]
        fps = float(stream.average_rate)
        duration = float(stream.duration * stream.time_base)
        frames = int(stream.frames or math.ceil(duration * fps))
    if fps <= 0 or duration <= 0 or frames <= 0:
        raise RuntimeError(f'Invalid video stream metadata: {video_path}')
    return {'fps': fps, 'duration_sec': duration, 'frame_count': frames}


def actual_pts(video, meta):
    """Persist only PTS/index metadata, never RGB frames or frame dumps."""
    safe_id = re.sub(r'[^A-Za-z0-9_.-]+', '_', video['video_id'])
    cache = ROOT / 'data/frame_pts' / video['dataset'] / f'{safe_id}.npy'
    if cache.exists():
        pts = np.load(cache, mmap_mode='r')
    else:
        cache.parent.mkdir(parents=True, exist_ok=True)
        values = []
        with av.open(video['video_path']) as container:
            stream = container.streams.video[0]
            for frame in container.decode(stream):
                if frame.pts is not None:
                    values.append(float(frame.pts * stream.time_base))
        pts = np.asarray(values, dtype=np.float64)
        if len(pts) == 0 or np.any(np.diff(pts) < 0):
            raise RuntimeError(f'Invalid presentation timestamps: {video["video_path"]}')
        tmp = cache.with_suffix('.tmp')
        with tmp.open('wb') as handle:
            np.save(handle, pts)
        tmp.replace(cache)
    if len(pts) == 0 or pts[0] > 1e-6:
        raise RuntimeError(f'No observed frame at t=0 for {video["video_path"]}')
    meta = dict(meta)
    meta['frame_count'] = int(len(pts))
    meta['duration_sec'] = max(float(meta['duration_sec']), float(pts[-1]))
    meta['pts'] = pts
    return meta


def cache_pts_worker(item):
    """Decode only frame presentation timestamps for one video.

    Kept process-safe and atomic so interrupted bounded-parallel construction
    can resume from completed per-video metadata files.
    """
    dataset, video_id, video_path = item
    safe_id = re.sub(r'[^A-Za-z0-9_.-]+', '_', video_id)
    cache = ROOT / 'data/frame_pts' / dataset / f'{safe_id}.npy'
    if cache.exists():
        return dataset, video_id, 'cached'
    cache.parent.mkdir(parents=True, exist_ok=True)
    values = []
    with av.open(video_path) as container:
        stream = container.streams.video[0]
        time_base = stream.time_base
        for frame in container.decode(stream):
            if frame.pts is not None:
                values.append(float(frame.pts * time_base))
    pts = np.asarray(values, dtype=np.float64)
    if len(pts) == 0 or np.any(np.diff(pts) < 0):
        raise RuntimeError(f'Invalid presentation timestamps: {video_path}')
    tmp = cache.with_suffix('.tmp')
    with tmp.open('wb') as handle:
        np.save(handle, pts)
    tmp.replace(cache)
    return dataset, video_id, len(pts)


def planned_prefix(query_time, meta):
    """Map desired times to the latest observed presentation timestamp."""
    start = max(0.0, query_time - WINDOW_SEC)
    desired = [start + (query_time - start) * i / (FRAMES - 1) for i in range(FRAMES)]
    indices = []
    timestamps = []
    for wanted in desired:
        index = int(np.searchsorted(meta['pts'], wanted + 1e-9, side='right') - 1)
        if index < 0:
            raise AssertionError(f'No observed frame at/before desired time {wanted}')
        timestamp = float(meta['pts'][index])
        if timestamp > wanted + 1e-7 or timestamp > query_time + 1e-7:
            raise AssertionError(f'Future frame: {timestamp} > {wanted}/{query_time}')
        indices.append(index)
        timestamps.append(timestamp)
    return indices, timestamps


def assembly_source():
    split = {}
    for side in ('train', 'test'):
        for record in (PROJECT / f'runs/mg_sft_v1/data/{side}_recordings.txt').read_text().splitlines():
            if record:
                split[record] = side
    probe = read_json(PROJECT / 'runs/mg_sft_v1/data/video_probe.json')
    goals = {}
    for path in (V2 / 'data/train.jsonl', V2 / 'data/val.jsonl'):
        for row in read_jsonl(path):
            if row['dataset'] == 'assembly101':
                goals.setdefault(row['video_id'], row['goal'])
    coarse = collections.defaultdict(list)
    for path in sorted((A101 / 'annotations/coarse-annotations/coarse_labels').glob('*.txt')):
        task, record = path.stem.split('_', 1)
        for line in path.read_text().splitlines():
            fields = line.split('\t')
            if len(fields) < 3:
                continue
            try:
                start, end = int(fields[0]), int(fields[1])
            except ValueError:
                continue
            label = norm(fields[2])
            if end > start and label:
                coarse[record].append({'start_sec': start / 30.0, 'end_sec': end / 30.0, 'label': label, 'task': task})
    fine = collections.defaultdict(dict)
    for path in sorted((A101 / 'annotations/fine-grained-annotations').glob('*.csv')):
        if path.name == 'actions.csv':
            continue
        with path.open(newline='') as handle:
            for row in csv.DictReader(handle):
                if '/HMC' not in row.get('video', ''):
                    continue
                try:
                    start, end = int(row['start_frame']), int(row['end_frame'])
                except (ValueError, TypeError):
                    continue
                label = norm(row.get('action_cls'))
                if not label or end <= start:
                    continue
                record = row['video'].split('/')[0]
                key = (start, end, row.get('action_id', ''), label)
                fine[record][key] = {'start_sec': start / 30.0, 'end_sec': end / 30.0, 'label': label, 'action_id': row.get('action_id')}
    videos = []
    for record, side in sorted(split.items()):
        if record not in probe or 'selected' not in probe[record]:
            continue
        duration = float(probe[record]['duration'])
        coarse_segments = [x for x in coarse[record] if x['end_sec'] <= duration]
        coarse_segments.sort(key=lambda x: (x['start_sec'], x['end_sec'], x['label']))
        raw_fine = sorted(fine[record].values(), key=lambda x: (x['start_sec'], x['end_sec'], str(x['action_id']), x['label']))
        segments = []
        for cid, segment in enumerate(coarse_segments):
            children = [x for x in raw_fine if segment['start_sec'] <= x['start_sec'] and x['end_sec'] <= segment['end_sec']]
            children.sort(key=lambda x: (x['start_sec'], x['end_sec'], str(x['action_id']), x['label']))
            segments.append({'coarse_id': cid, 'label': segment['label'], 'start_sec': segment['start_sec'], 'end_sec': segment['end_sec'], 'predictability': 'strong' if cid else None, 'fine_actions': children})
        if segments:
            video_path = probe[record]['selected']
            videos.append({'dataset': 'assembly101', 'video_id': record, 'recording_id': record, 'split': side, 'video_path': video_path, 'goal': goals.get(record, f"{segments[0]['label']}"), 'segments': segments, 'meta': stream_meta(video_path)})
    return videos


def epic_source():
    hierarchy = {p.stem: p for p in (EPIC / 'final_v1/videos').glob('*.json')}
    split = {}
    path = {}
    goal = {}
    for side, manifest in [('train', V2 / 'data/train.jsonl'), ('test', V2 / 'data/val.jsonl')]:
        for row in read_jsonl(manifest):
            if row['dataset'] == 'epic_kitchens':
                split[row['video_id']] = side
                path[row['video_id']] = row['video_path']
                goal[row['video_id']] = row['goal']
    videos = []
    for video_id in sorted(set(hierarchy) & set(split)):
        source = read_json(hierarchy[video_id])
        segments = []
        for segment in sorted(source.get('coarse_segments', []), key=lambda x: x.get('coarse_id', 0)):
            children = []
            for item in sorted(segment.get('fine_actions', []), key=lambda x: x.get('fine_idx', 0)):
                label = norm(item.get('canonical_fine_text') or item.get('narration') or ' '.join(x for x in [item.get('verb'), item.get('noun')] if x))
                if label:
                    children.append({'start_sec': float(item['start_sec']), 'end_sec': float(item['end_sec']), 'label': label, 'action_id': item.get('original_action_id')})
            segments.append({'coarse_id': segment.get('coarse_id'), 'label': norm(segment.get('label')), 'start_sec': float(segment['start_sec']), 'end_sec': float(segment['end_sec']), 'predictability': segment.get('predictability'), 'fine_actions': children})
        if not segments or not Path(path[video_id]).is_file():
            continue
        meta = stream_meta(path[video_id])
        videos.append({'dataset': 'epic_kitchens', 'video_id': video_id, 'recording_id': video_id, 'split': split[video_id], 'video_path': path[video_id], 'goal': source.get('goal') or goal[video_id], 'segments': segments, 'meta': meta})
    return videos


def eligible_fine_events(segments):
    events = []
    for segment in segments:
        seen = set()
        for item in segment['fine_actions'][1:]:
            # Simultaneous onsets are not valid independent next-step targets.
            if item['start_sec'] in seen:
                continue
            seen.add(item['start_sec'])
            events.append({**item, 'coarse_id': segment['coarse_id'], 'coarse_label': segment['label'], 'coarse_start_sec': segment['start_sec'], 'coarse_end_sec': segment['end_sec']})
    return sorted(events, key=lambda x: (x['start_sec'], x['end_sec'], str(x['action_id'])))


def coarse_events(segments):
    return sorted([{'start_sec': x['start_sec'], 'end_sec': x['end_sec'], 'label': x['label'], 'predictability': x['predictability'], 'coarse_id': x['coarse_id']} for x in segments[1:] if x['predictability'] in ('strong', 'weak', 'none')], key=lambda x: x['start_sec'])


def first_in_interval(events, starts, query_time, end_time):
    index = bisect.bisect_right(starts, query_time + 1e-9)
    if index < len(events) and events[index]['start_sec'] <= end_time + 1e-9:
        return events[index]
    return None


def current_segment(segments, query_time):
    for segment in segments:
        if segment['start_sec'] <= query_time < segment['end_sec']:
            return segment
    return None


def row_for(video, query_index, coarse, fine):
    query = query_index * GRID_SEC
    end = min(query + GRID_SEC, video['meta']['duration_sec'])
    segment = current_segment(video['segments'], query)
    frame_indices, frame_timestamps = planned_prefix(query, video['meta'])
    coarse_event = first_in_interval(coarse[0], coarse[1], query, end)
    fine_event = first_in_interval(fine[0], fine[1], query, end)
    # A fine step is only eligible while its parent coarse subtask is active.
    if fine_event and (not segment or segment['coarse_id'] != fine_event['coarse_id']):
        fine_event = None
    coarse_pred = coarse_event['predictability'] if coarse_event else 'background'
    coarse_decision = 'SPEAK' if coarse_event else 'SILENT'
    fine_decision = 'SPEAK' if fine_event else 'SILENT'
    if coarse_pred == 'none':
        pair_state = 'NONE_FINE_SPEAK' if fine_decision == 'SPEAK' else 'NONE_FINE_SILENT'
        valid_lgran = False
    else:
        pair_state = {('SILENT', 'SILENT'): 'BOTH_SILENT', ('SILENT', 'SPEAK'): 'FINE_ONLY', ('SPEAK', 'SILENT'): 'COARSE_ONLY', ('SPEAK', 'SPEAK'): 'BOTH_SPEAK'}[(coarse_decision, fine_decision)]
        valid_lgran = pair_state in ('FINE_ONLY', 'COARSE_ONLY')
    return {
        'pair_id': f"dense0p5:{video['dataset']}:{video['video_id']}:{query_index:07d}",
        'dataset': video['dataset'], 'video_id': video['video_id'], 'recording_id': video['recording_id'], 'split': video['split'],
        'video_path': video['video_path'], 'query_time': query, 'query_timestamp_sec': query, 'horizon_end_sec': end,
        'frame_indices': frame_indices, 'frame_timestamps': frame_timestamps,
        'frame_selection': 'PyAV presentation-timestamp floor: latest decoded frame at or before each desired timestamp',
        'goal': video['goal'], 'current_subtask': segment['label'] if segment else None,
        'coarse_predictability': coarse_pred, 'coarse_decision': coarse_decision,
        'coarse_target': coarse_event['label'] if coarse_event else None,
        'coarse_event_start_sec': coarse_event['start_sec'] if coarse_event else None,
        'coarse_event_end_sec': coarse_event['end_sec'] if coarse_event else None,
        'fine_decision': fine_decision, 'fine_target': fine_event['label'] if fine_event else None,
        'fine_event_start_sec': fine_event['start_sec'] if fine_event else None,
        'fine_event_end_sec': fine_event['end_sec'] if fine_event else None,
        'use_coarse_decision_loss_base': coarse_pred in ('strong', 'weak', 'background'),
        'use_coarse_content_loss_base': coarse_pred in ('strong', 'weak'),
        'use_coarse_none_loss': coarse_pred == 'none',
        'use_fine_decision_loss': True,
        'use_fine_content_loss': fine_decision == 'SPEAK',
        'pair_state': pair_state, 'pair_valid_for_Lgran': valid_lgran,
        'coarse_group': {'strong': 'C_POS_STRONG', 'weak': 'C_POS_WEAK', 'none': 'C_POS_NONE', 'background': 'C_NEG_BACKGROUND'}[coarse_pred],
        'fine_group': 'F_POS' if fine_decision == 'SPEAK' else 'F_NEG',
        'grid_interval_sec': GRID_SEC,
    }


def write_rows(path, videos):
    tmp = path.with_suffix('.tmp')
    counts = collections.Counter()
    with tmp.open('w') as handle:
        for video in videos:
            fine = eligible_fine_events(video['segments'])
            coarse = coarse_events(video['segments'])
            fstarts = [x['start_sec'] for x in fine]
            cstarts = [x['start_sec'] for x in coarse]
            total = math.ceil(video['meta']['duration_sec'] / GRID_SEC)
            for index in range(total):
                row = row_for(video, index, (coarse, cstarts), (fine, fstarts))
                assert all(t <= row['query_time'] + 1e-7 for t in row['frame_timestamps'])
                assert not (row['coarse_predictability'] == 'none' and row['coarse_decision'] == 'SILENT')
                assert not (row['coarse_predictability'] == 'none' and row['pair_valid_for_Lgran'])
                handle.write(json.dumps(row, ensure_ascii=False) + '\n')
                counts[row['coarse_group']] += 1
                counts[row['fine_group']] += 1
                counts[row['pair_state']] += 1
    tmp.replace(path)
    return counts


def summarize(path):
    total = 0
    coarse = collections.Counter()
    fine = collections.Counter()
    states = collections.Counter()
    datasets = collections.Counter()
    invalid = collections.Counter()
    for row in read_jsonl(path):
        total += 1
        coarse[row['coarse_group']] += 1
        fine[row['fine_group']] += 1
        states[row['pair_state']] += 1
        datasets[row['dataset']] += 1
        if not row['pair_valid_for_Lgran']:
            invalid[row['pair_state']] += 1
    return {'rows': total, 'coarse_raw': dict(coarse), 'fine_raw': dict(fine), 'pair_states': dict(states), 'by_dataset': dict(datasets), 'lgran_masked_states': dict(invalid)}


def main():
    all_videos = assembly_source() + epic_source()
    missing = []
    for video in all_videos:
        safe_id = re.sub(r'[^A-Za-z0-9_.-]+', '_', video['video_id'])
        cache = ROOT / 'data/frame_pts' / video['dataset'] / f'{safe_id}.npy'
        if not cache.exists():
            missing.append((video['dataset'], video['video_id'], video['video_path']))
    if missing:
        # Timestamp decoding is CPU/I/O work, bounded to avoid pressuring the
        # storage server while greatly reducing a serial metadata-only pass.
        with ProcessPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(cache_pts_worker, item) for item in missing]
            for n, future in enumerate(as_completed(futures), 1):
                future.result()
                if n % 25 == 0 or n == len(futures):
                    print(f'cached actual PTS: {n}/{len(futures)}', flush=True)
    train = []
    test = []
    for video in all_videos:
        video['meta'] = actual_pts(video, video['meta'])
        (train if video['split'] == 'train' else test).append(video)
    train.sort(key=lambda x: (x['dataset'], x['video_id']))
    test.sort(key=lambda x: (x['dataset'], x['video_id']))
    train_ids = {(x['dataset'], x['video_id']) for x in train}
    test_ids = {(x['dataset'], x['video_id']) for x in test}
    assert not train_ids & test_ids
    train_path = ROOT / 'data/dense_train.jsonl'
    test_path = ROOT / 'data/dense_test.jsonl'
    write_rows(train_path, train)
    write_rows(test_path, test)
    report = {
        'grid_interval_sec': GRID_SEC, 'visual_window_sec': WINDOW_SEC, 'frames_per_prefix': FRAMES,
        'label_definition': 'COARSE and FINE independently use their own next eligible event in (t,t+0.5]; pair_state is derived afterward. Coarse none is SPEAK with content and is excluded only from L_gran.',
        'no_temporal_guard_bands': True, 'no_negative_spacing': True,
        'train_video_count': len(train_ids), 'test_video_count': len(test_ids), 'video_overlap': 0,
        'train': summarize(train_path), 'test': summarize(test_path),
    }
    atomic_json(ROOT / 'reports/dense_manifest_audit.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
