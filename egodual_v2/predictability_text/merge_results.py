"""Validate all text-based predictable labels and copy them into output annotations."""
import json, os, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
RESULT=ROOT/'predictability_text/results'
VIDEOS=ROOT/'annotations'

def atomic(path,obj):
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.'+path.name)
    try:
        with os.fdopen(fd,'w') as f:
            json.dump(obj,f,indent=2,ensure_ascii=False);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def main():
    files=sorted(VIDEOS.glob('*.json'))
    assert len(files)==93, f'Expected 93 annotation files, got {len(files)}'
    updates=[]
    for file in files:
        data=json.loads(file.read_text())
        path=RESULT/file.name
        assert path.exists(),f'Missing {path.name}'
        result=json.loads(path.read_text())
        assert result['video_id']==file.stem and result['method']=='adjacent_subtask_text'
        labels=result['subtasks'];coarse=data['coarse']
        assert len(labels)==len(coarse),(file.stem,len(labels),len(coarse))
        assert [x['index'] for x in labels]==list(range(len(coarse))),file.stem
        for c,x in zip(coarse,labels):
            assert x['level'] in ('no','weak','strong') and isinstance(x['reason'],str) and x['reason'].strip(),(file.stem,x)
            c['predictability_level']=x['level'];c['predictability_reason']=x['reason']
        updates.append((file,data))
    for file,data in updates:atomic(file,data)
    print(json.dumps({'videos':len(updates),'subtasks':sum(len(d['coarse']) for _,d in updates),'status':'merged'}))
if __name__=='__main__':main()
