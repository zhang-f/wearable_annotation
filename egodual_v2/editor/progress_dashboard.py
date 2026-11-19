"""Read-only live status for the annotation workspace."""
import datetime
import json
from pathlib import Path

EXPECTED_VIDEOS = 93
EXPECTED_FINE = 4020


def load_json(path, default=None):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def tail_jsonl(path, limit=100):
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []
    out = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def collect(root: Path):
    root = Path(root)
    pred = root / 'predictability'
    validation_path = root / 'validation_after_goal_completion.json'
    if not validation_path.exists():
        validation_path = root / 'editor_final_full_validation.json'
    validation = load_json(validation_path, []) or []
    checks = {x.get('video_id'): x for x in validation if isinstance(x, dict)}
    videos = []
    events = []
    for path in sorted((root / 'annotations').glob('*.json')):
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        fine = data.get('fine') or []
        coarse = data.get('coarse') or []
        goal = data.get('goal') or {}
        check = checks.get(path.stem, {})
        item = {
            'video_id': path.stem,
            'task': data.get('task') or goal.get('title') or '',
            'goal_title': goal.get('title') or '',
            'goal_description': goal.get('description') or '',
            'final_state': goal.get('final_state') or '',
            'subtasks': [{'start': c.get('start'), 'end': c.get('end'),
                          'instruction': c.get('instruction'), 'description': c.get('description'),
                          'predictability_level': c.get('predictability_level')} for c in coarse],
            'fine': len(fine), 'coarse': len(coarse),
            'procedure': bool(goal.get('procedure')),
            'contributions': bool(coarse) and all(bool(c.get('goal_contribution')) for c in coarse),
            'predictability_levels': sum(c.get('predictability_level') in ('no', 'weak', 'strong') for c in coarse),
            'ambiguous': sum(bool(s.get('ambiguous')) for s in fine),
            'boundary_notes': sum(bool(s.get('boundary_note')) for s in fine),
            'validation_errors': check.get('errors', []),
            'validation_warnings': check.get('warnings', []),
            'modified_utc': datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat(),
        }
        videos.append(item)
        events.append({'when': item['modified_utc'], 'stage': 'annotation', 'video_id': path.stem,
                       'message': f"Saved {len(fine)} steps and {len(coarse)} subtasks"})
    manifest = load_json(pred / 'delivery_manifest.json', {}) or {}
    bundles = manifest.get('bundles', [])
    prep = load_json(pred / 'preparation_summary.json', {}) or {}
    text_results = []
    for path in (root / 'predictability_text' / 'results').glob('*.json'):
        result = load_json(path, {}) or {}
        if isinstance(result.get('subtasks'), list):
            text_results.append((path, result))
    text_counts = {result.get('video_id'): len(result['subtasks']) for _, result in text_results}
    for item in videos:
        item['text_predictability_levels'] = text_counts.get(item['video_id'], 0)
    result_files = []
    judged = 0
    for path in pred.glob('*.json'):
        if len(path.stem) != 16 or any(c not in '0123456789abcdef' for c in path.stem):
            continue
        result = load_json(path, {}) or {}
        count = len(result.get('subtasks', []))
        judged += count
        result_files.append(path.name)
        events.append({'when': datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat(),
                       'stage': 'predictability', 'video_id': path.stem,
                       'message': f'Saved {count} judged subtasks'})
    for row in tail_jsonl(root / 'batch01_progress.jsonl'):
        when = row.get('completed_utc') or row.get('ts')
        if when:
            events.append({'when': when, 'stage': 'run log', 'video_id': row.get('video_id'),
                           'message': f"{row.get('status', 'update')}: {row.get('fine_count', '?')} steps, {row.get('coarse_count', '?')} subtasks"})
    for row in tail_jsonl(root / 'goal_contribution_completion.jsonl'):
        vid = row.get('video_id')
        if vid:
            events.append({'when': next((v['modified_utc'] for v in videos if v['video_id'] == vid), ''),
                           'stage': 'detail fill', 'video_id': vid,
                           'message': f"Added {row.get('procedure_items', '?')} procedure items, {row.get('contributions_added', '?')} contributions"})
    for path in sorted(pred.glob('probe*.json')) + sorted(pred.glob('forecast_*.json')) + sorted(pred.glob('judge_*.json')):
        events.append({'when': datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat(),
                       'stage': 'blind trial', 'video_id': None, 'message': f'Saved {path.name}'})
    for path, result in text_results:
        events.append({'when': datetime.datetime.fromtimestamp(path.stat().st_mtime, datetime.timezone.utc).isoformat(),
                       'stage': 'text predictability', 'video_id': result.get('video_id'),
                       'message': f"Classified {len(result['subtasks'])} subtasks from descriptions"})
    events.sort(key=lambda x: x['when'] or '', reverse=True)
    stats = {
        'videos_saved': len(videos), 'videos_total': EXPECTED_VIDEOS,
        'fine_saved': sum(v['fine'] for v in videos), 'fine_total': EXPECTED_FINE,
        'coarse_saved': sum(v['coarse'] for v in videos),
        'procedure_complete': sum(v['procedure'] for v in videos),
        'contributions_complete': sum(v['contributions'] for v in videos),
        'bundles_ready': len(bundles), 'bundles_total': sum(v['coarse'] for v in videos),
        'predictability_judged': judged,
        'text_predictability_videos': len(text_results),
        'text_predictability_subtasks': sum(len(result['subtasks']) for _, result in text_results),
        'predictability_levels': sum(v['predictability_levels'] for v in videos),
        'validation_video_count': len(checks),
        'validation_error_count': sum(len(x.get('errors', [])) for x in validation),
        'blind_trial_files': len(list(pred.glob('probe*.json'))) + len(list(pred.glob('forecast_*.json'))) + len(list(pred.glob('judge_*.json'))),
    }
    return {'updated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'stats': stats, 'videos': videos, 'events': events[:250],
            'reports': {'bundle_preparation': 'predictability/preparation_report.md',
                        'bundle_validation': 'predictability/bundle_validation.json',
                        'annotation_validation': str(validation_path.relative_to(root)),
                        'three_level_protocol': 'predictability/three_level_protocol.md',
                        'text_predictability_result': 'predictability_text/report.md',
                        'text_predictability_validation': 'predictability_text/validation_after_merge.json'},
            'bundle_preparation': prep, 'predictability_result_files': result_files}
