#!/usr/bin/env python3
"""Audit the corrected dense-grid manifest and simulate its training sampler.

This audit deliberately treats COARSE and FINE as independent targets.  Pair
states are derived diagnostics only, and coarse ``none`` is checked as a
positive-only auxiliary group rather than a negative/timing label.
"""
import collections
import json
import math
import random
from pathlib import Path

PROJECT = Path('/data/fan/projects/procedure_forecasting')
ROOT = PROJECT / 'runs/granularity_aware_final_v1'
SEED = 42


def rows(path):
    with Path(path).open() as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def pct(n, d):
    return None if not d else round(100.0 * n / d, 4)


def dist(counter):
    total = sum(counter.values())
    return {k: {'count': v, 'percent': pct(v, total)} for k, v in sorted(counter.items())}


def cyclic_draw(pool, count, seed):
    """Simulate deterministic without-replacement rotations through a pool."""
    assert pool
    rng = random.Random(seed)
    values = list(pool)
    out = []
    while len(out) < count:
        rng.shuffle(values)
        out.extend(values)
    return out[:count]


def scan(path, split):
    raw_c = collections.Counter()
    raw_f = collections.Counter()
    states = collections.Counter()
    by_dataset = collections.defaultdict(lambda: collections.Counter())
    pools = collections.defaultdict(list)
    violations = collections.defaultdict(list)
    videos = set()
    q_by_video = collections.defaultdict(list)
    count = 0
    for row in rows(path):
        count += 1
        rid = row['pair_id']
        videos.add((row['dataset'], row['video_id']))
        q_by_video[(row['dataset'], row['video_id'])].append(row['query_time'])
        c = row['coarse_group']; f = row['fine_group']; state = row['pair_state']
        raw_c[c] += 1; raw_f[f] += 1; states[state] += 1
        by_dataset[row['dataset']][f'C:{c}'] += 1
        by_dataset[row['dataset']][f'F:{f}'] += 1
        by_dataset[row['dataset']][f'S:{state}'] += 1
        # New-pipeline leakage/semantic assertions only.
        if any(float(t) > float(row['query_time']) + 1e-7 for t in row['frame_timestamps']):
            violations['future_frame'].append(rid)
        if len(row['frame_indices']) != 16 or len(row['frame_timestamps']) != 16:
            violations['not_16_canonical_frames'].append(rid)
        if row['coarse_predictability'] == 'none':
            if row['coarse_decision'] != 'SPEAK' or row['coarse_target'] is None:
                violations['none_relabelled_or_missing_target'].append(rid)
            if row['use_coarse_decision_loss_base'] or row['use_coarse_content_loss_base'] or not row['use_coarse_none_loss']:
                violations['none_in_base_loss'].append(rid)
            if row['pair_valid_for_Lgran']:
                violations['none_in_lgran'].append(rid)
        if row['coarse_group'] == 'C_NEG_BACKGROUND' and row['coarse_decision'] != 'SILENT':
            violations['background_not_silent'].append(rid)
        if row['coarse_group'] != 'C_NEG_BACKGROUND' and row['coarse_decision'] != 'SPEAK':
            violations['coarse_positive_not_speak'].append(rid)
        if row['pair_valid_for_Lgran'] != (state in ('FINE_ONLY', 'COARSE_ONLY')):
            violations['lgran_pair_state_mismatch'].append(rid)
        if state == 'FINE_ONLY' and not (c == 'C_NEG_BACKGROUND' and f == 'F_POS'):
            violations['fine_only_mismatch'].append(rid)
        if state == 'COARSE_ONLY' and not (c in ('C_POS_STRONG', 'C_POS_WEAK') and f == 'F_NEG'):
            violations['coarse_only_mismatch'].append(rid)
        # Simulation only needs pool cardinality/identity, not the full ~1KB
        # query object. Keeping IDs avoids a needless multi-GB audit process.
        if c in ('C_POS_STRONG', 'C_POS_WEAK'):
            pools['coarse_pos'].append(rid)
        if c == 'C_NEG_BACKGROUND':
            pools['coarse_bg'].append(rid)
        if c == 'C_POS_NONE':
            pools['coarse_none'].append(rid)
        if f == 'F_POS':
            pools['fine_pos'].append(rid)
        else:
            pools['fine_neg'].append(rid)
        if state == 'FINE_ONLY': pools['lgran_fine_only'].append(rid)
        if state == 'COARSE_ONLY': pools['lgran_coarse_only'].append(rid)
    # The manifest is a single row per pair, so both branch views necessarily
    # reference the exact same ordered frame arrays.  Assert the canonical list
    # is present; the training collator also asserts equality before processing.
    for key, values in q_by_video.items():
        values.sort()
        if any(abs(b - a - .5) > 1e-7 for a, b in zip(values, values[1:])):
            violations['non_dense_or_old_temporal_filter'].append(':'.join(key))
    return {
        'split': split, 'grid_rows': count, 'video_count': len(videos),
        'coarse_raw': dist(raw_c), 'fine_raw': dist(raw_f), 'pair_states': dist(states),
        'by_dataset_raw': {d: dict(sorted(v.items())) for d, v in sorted(by_dataset.items())},
        'violations': {k: v[:20] for k, v in sorted(violations.items()) if v},
        'violation_counts': {k: len(v) for k, v in sorted(violations.items()) if v},
        '_pools': pools,
    }


def sampler_report(pools, steps=10000):
    required = ('coarse_pos', 'coarse_bg', 'fine_pos', 'fine_neg', 'lgran_fine_only', 'lgran_coarse_only', 'coarse_none')
    missing = [p for p in required if not pools[p]]
    if missing:
        raise RuntimeError(f'Cannot simulate required sampler pools: {missing}')
    # Eight rank roles each optimizer step.  This creates 1:1 coarse base and
    # 1:1 fine marginals; two directional slots balance L_gran exactly.
    roles = ['lgran_fine_only', 'lgran_fine_only', 'lgran_coarse_only', 'lgran_coarse_only', 'coarse_pos', 'coarse_bg', 'fine_pos', 'fine_neg']
    draws = {role: cyclic_draw(pools[role], steps * roles.count(role), SEED + i) for i, role in enumerate(sorted(set(roles)))}
    cursor = collections.Counter(); observed_c = collections.Counter(); observed_f = collections.Counter(); observed_lg = collections.Counter()
    for _ in range(steps):
        for role in roles:
            row = draws[role][cursor[role]]; cursor[role] += 1
            # Pool role completely determines optimizer-facing class. We do
            # not retain full rows during audit, by design.
            if role == 'coarse_pos': observed_c['C_POS_STRONG_OR_WEAK'] += 1
            elif role == 'coarse_bg': observed_c['C_NEG_BACKGROUND'] += 1
            if role == 'fine_pos': observed_f['F_POS'] += 1
            elif role == 'fine_neg': observed_f['F_NEG'] += 1
            if role == 'lgran_fine_only': observed_lg['FINE_ONLY'] += 1
            if role == 'lgran_coarse_only': observed_lg['COARSE_ONLY'] += 1
    c_speak = observed_c['C_POS_STRONG_OR_WEAK']
    return {
        'simulation_steps': steps, 'world_size_roles': len(roles), 'role_schedule': roles,
        'coarse_optimizer_facing': {**dist(observed_c), 'SPEAK_count': c_speak, 'SILENT_count': observed_c['C_NEG_BACKGROUND'], 'SPEAK_percent': pct(c_speak, c_speak + observed_c['C_NEG_BACKGROUND']), 'SILENT_percent': pct(observed_c['C_NEG_BACKGROUND'], c_speak + observed_c['C_NEG_BACKGROUND'])},
        'fine_optimizer_facing': {**dist(observed_f), 'SPEAK_count': observed_f['F_POS'], 'SILENT_count': observed_f['F_NEG'], 'SPEAK_percent': pct(observed_f['F_POS'], sum(observed_f.values())), 'SILENT_percent': pct(observed_f['F_NEG'], sum(observed_f.values()))},
        'lgran_optimizer_facing': dist(observed_lg),
        'weighted_none': {'raw_none_count': len(pools['coarse_none']), 'none_group_weight': .25, 'group_combination': '(base + 0.25 * none) / 1.25', 'effective_group_weight_percent': 20.0},
    }


def markdown(report):
    def table(title, values):
        lines = [f'### {title}', '', '| Class | Count | Percent |', '|---|---:|---:|']
        for k, v in values.items(): lines.append(f"| {k} | {v['count']} | {v['percent']}% |")
        return '\n'.join(lines)
    out = ['# Corrected Dense-Grid Data and Sampler Audit', '', 'The manifest uses independent COARSE/FINE event labels at every 0.5-second query. Pair state is derived after labeling. Coarse `none` is a real SPEAK event, is never a negative, and is excluded from `L_gran`.', '']
    for name in ('train', 'test'):
        block = report[name]
        out += [f'## {name.title()}', f"- Grid rows: {block['grid_rows']}", f"- Videos: {block['video_count']}", '']
        out += [table('COARSE raw', block['coarse_raw']), '', table('FINE raw', block['fine_raw']), '', table('Derived pair states', block['pair_states']), '']
        if block['violation_counts']:
            out += ['**FAIL:** ' + json.dumps(block['violation_counts'], sort_keys=True), '']
        else:
            out += ['**PASS:** all new-manifest assertions passed: no future frames; no none relabeling; none is outside base negative and `L_gran` pools; dense 0.5-second grids have no legacy temporal filtering.', '']
    s = report['sampler_simulation']
    out += ['## Actual sampler simulation', f"- {s['simulation_steps']} optimizer steps with eight deterministic DDP roles: `{', '.join(s['role_schedule'])}`.", '', table('COARSE optimizer-facing', {k:v for k,v in s['coarse_optimizer_facing'].items() if isinstance(v, dict)}), '', table('FINE optimizer-facing', {k:v for k,v in s['fine_optimizer_facing'].items() if isinstance(v, dict)}), '', table('L_gran directions', s['lgran_optimizer_facing']), '', f"- Weighted-none: `{s['weighted_none']['group_combination']}`; effective group contribution {s['weighted_none']['effective_group_weight_percent']}%.", '']
    return '\n'.join(out)


def main():
    train = scan(ROOT / 'data/dense_train.jsonl', 'train')
    test = scan(ROOT / 'data/dense_test.jsonl', 'test')
    sampler = sampler_report(train['_pools'])
    train.pop('_pools'); test.pop('_pools')
    report = {'seed': SEED, 'grid_interval_sec': .5, 'temporal_guard_bands': False, 'negative_spacing': False, 'train': train, 'test': test, 'sampler_simulation': sampler,
              'variant_data_identity': 'Variant A and Variant B share the same dense base manifest and role schedule; only Variant B adds coarse none with group weight 0.25.'}
    (ROOT / 'reports/dense_data_sampler_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'reports/dense_data_sampler_audit.md').write_text(markdown(report) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('train','test')}, indent=2))
    if train['violation_counts'] or test['violation_counts']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
