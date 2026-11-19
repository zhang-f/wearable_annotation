#!/usr/bin/env python3
"""Validate the published EgoDual v2 JSONs without source videos or private files."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    files=sorted((ROOT/'annotations').glob('*.json'))
    errors=[];rows=[]
    if len(files)!=manifest['video_count']:errors.append('video count')
    for file in files:
        data=json.loads(file.read_text());rows.append(data)
        if file.stem!=data.get('video_id'):errors.append(f'{file.name}: id')
        if hashlib.sha256(file.read_bytes()).hexdigest()!=manifest['files'].get(file.name):errors.append(f'{file.name}: hash')
        fine=data.get('fine',[]);coarse=data.get('coarse',[])
        if not fine or not coarse:errors.append(f'{file.name}: missing segments');continue
        prev=0.0
        for i,step in enumerate(fine):
            if abs(step['start']-prev)>.011 or step['end']<=step['start']:errors.append(f'{file.name}: fine {i} timeline')
            prev=step['end']
            if step.get('summary') in ('','n') and not step.get('beyond_video_end'):errors.append(f'{file.name}: fine {i} placeholder')
        next_index=0
        for i,part in enumerate(coarse):
            start,end=part['fine_index_range']
            if start!=next_index or end<start or end>=len(fine):errors.append(f'{file.name}: coarse {i} range');break
            if abs(part['start']-fine[start]['start'])>.011 or abs(part['end']-fine[end]['end'])>.011:errors.append(f'{file.name}: coarse {i} time')
            if part.get('predictability_level') not in ('no','weak','strong') or not part.get('predictability_reason'):errors.append(f'{file.name}: coarse {i} predictability')
            if not part.get('goal_contribution'):errors.append(f'{file.name}: coarse {i} contribution')
            next_index=end+1
        if next_index!=len(fine):errors.append(f'{file.name}: incomplete coarse coverage')
        if not data.get('goal',{}).get('procedure'):errors.append(f'{file.name}: missing procedure')
    if sum(len(d.get('fine',[])) for d in rows)!=manifest['fine_count']:errors.append('fine count')
    if sum(len(d.get('coarse',[])) for d in rows)!=manifest['coarse_count']:errors.append('coarse count')
    packed=[json.loads(line) for line in (ROOT/'final_annotations.jsonl').read_text().splitlines() if line.strip()]
    if packed!=rows:errors.append('JSONL differs from per-video files')
    print(json.dumps({'videos':len(rows),'fine':sum(len(d.get('fine',[])) for d in rows),'coarse':sum(len(d.get('coarse',[])) for d in rows),'errors':errors},indent=2))
    return int(bool(errors))
if __name__=='__main__':sys.exit(main())
