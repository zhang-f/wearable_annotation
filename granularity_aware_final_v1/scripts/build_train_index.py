#!/usr/bin/env python3
"""Create compact seek offsets for dynamic sampling from the complete grid.

The complete dense manifest stays immutable.  Offsets let each DDP rank rotate
through every negative pool without materialising ~625k JSON records in memory.
"""
import json
from pathlib import Path
import numpy as np

ROOT = Path('/data/fan/projects/procedure_forecasting/runs/granularity_aware_final_v1')
SOURCE = ROOT / 'data/dense_train.jsonl'
OUT = ROOT / 'data/train_pool_offsets.npz'

POOLS = ('coarse_pos', 'coarse_bg', 'coarse_none', 'fine_pos', 'fine_neg', 'lgran_fine_only', 'lgran_coarse_only')


def main():
    pools = {name: [] for name in POOLS}
    with SOURCE.open('rb') as handle:
        while True:
            offset = handle.tell()
            line = handle.readline()
            if not line:
                break
            row = json.loads(line)
            c, f, state = row['coarse_group'], row['fine_group'], row['pair_state']
            if c in ('C_POS_STRONG', 'C_POS_WEAK'): pools['coarse_pos'].append(offset)
            if c == 'C_NEG_BACKGROUND': pools['coarse_bg'].append(offset)
            if c == 'C_POS_NONE': pools['coarse_none'].append(offset)
            pools['fine_pos' if f == 'F_POS' else 'fine_neg'].append(offset)
            if state == 'FINE_ONLY': pools['lgran_fine_only'].append(offset)
            if state == 'COARSE_ONLY': pools['lgran_coarse_only'].append(offset)
    arrays = {name: np.asarray(value, dtype=np.int64) for name, value in pools.items()}
    tmp = OUT.with_suffix('.tmp.npz')
    np.savez_compressed(tmp, **arrays)
    tmp.replace(OUT)
    counts = {k: int(len(v)) for k, v in arrays.items()}
    (ROOT / 'data/train_pool_offsets.json').write_text(json.dumps({'source': str(SOURCE), 'pools': counts}, indent=2) + '\n')
    print(json.dumps(counts, indent=2))


if __name__ == '__main__':
    main()
