import json,csv,pathlib,os
R=pathlib.Path('/home/fan/google'); O=R/'review_run/annotation_v2'
src={x['video_path'][:-4]:x for x in map(json.loads,open(R/'data_annotation/annotations_fine_completed.jsonl'))}
inv={x['video_id']:float(x['ffprobe_duration']) for x in csv.DictReader(open(R/'review_run/video_inventory.csv'))}
def thermostat():
 v='fc264c696a11a50c'; T='thermostat';B='battery';C='battery cover';K='butter knife';S='screwdriver';W='cotton swab';P='battery pack';ST='stool';BIN='bin';inventory=[T,B,C,K,S,W,P,ST,BIN]
 # summary, verb, object, tool, target, hands, left-end, right-end, note
 rows=[
 ('remove the thermostat from the wall','remove',T,None,None,'left',[T],[],None),
 ('turn the thermostat over and inspect the battery cover','inspect',T,None,None,'left',[T],[],'t=5–8s repeatedly turn thermostat; t=9.8s right hand reaches toward stool.'),
 ('pry the battery cover with the butter knife','open',C,K,None,'both',[T],[K],'t=10.1s pick up knife, t=10.5–20.8s lever cover repeatedly; compound interval.'),
 ('put down the butter knife on the stool','put down',K,None,ST,'right',[T],[],None),
 ('pick up the screwdriver','pick up',S,None,None,'right',[T],[S],'t=23.5–26.5s walk to table while holding thermostat; t=26.8s take screwdriver.'),
 ('pry off the battery cover with the screwdriver','remove',C,S,None,'both',[T],[S,C],'t=29.2–33.5s lever cover; t=34.1–35.0s lift cover away.'),
 ('place the battery cover on the stool','place',C,None,ST,'right',[T],[S],None),
 ('put down the screwdriver on the stool','put down',S,None,ST,'right',[T],[],None),
 ('remove a battery from the thermostat','remove',B,None,T,'right',[T],[B],'t=39.8–42.3s fingers work battery free; native end grip partly covers cell.'),
 ('remove the remaining battery from the thermostat','remove',B,None,T,'right',[T],[B],None),
 ('place the thermostat on the stool','place',T,None,ST,'left',[],[B],None),
 ('transfer the batteries into the left hand','move',B,None,None,'both',[B],[], 't=47–49s pause; t=49.7–51.4s collect both batteries in left hand.'),
 ('pick up the cotton swab','pick up',W,None,None,'right',[B],[W],None),
 ('rub the battery terminals with the cotton swab','wipe',B,W,None,'both',[B],[W],'t=53.1–59.0s wipe ends of batteries; t=59.4s right hand lowers swab toward stool.'),
 ('pick up the thermostat from the stool','pick up',T,None,None,'right',[B],[T],None),
 ('carry the thermostat and batteries toward the bin','move',T,None,None,'both',[B],[T],'t=60.5–70.8s hold thermostat and batteries while paused; t=72.8s turn toward bin.'),
 ('open the bin and release the batteries','open',BIN,None,None,'left',[],[T],'t=74.5s lift lid, t=74.7s hand enters bin; boundary at74.65s crosses the opening/releasing event; retained.'),
 ('withdraw the hand from the bin','move',BIN,None,None,'left',[],[T],'t=74.65–75.15s withdraw left hand, leaving lid open.'),
 ('carry the thermostat back to the stool','move',T,None,None,'both',[T],[],'t=75.4–76.8s transfer thermostat from right to left; t=77–78s right hand lowers toward stool.'),
 ('pick up a battery from the battery pack','pick up',B,None,P,'right',[T],[B],None),
 ('insert a battery into the thermostat','insert',B,None,T,'right',[T],[],None),
 ('pick up another battery from the battery pack','pick up',B,None,P,'right',[T],[B],None),
 ('insert the second battery into the thermostat','insert',B,None,T,'right',[T],[],None),
 ('pick up the battery cover from the stool','pick up',C,None,ST,'right',[T],[C],None),
 ('turn the thermostat over and inspect the display','inspect',T,None,None,'both',[T],[C],'t=92–93.8s inspect front; t=94.1–96.2s turn back and inspect batteries.'),
 ('inspect the thermostat display','inspect',T,None,None,'both',[T],[C],'t=97–103.5s hold front toward view; t=104.1s turn back. Display appears blank; no fault inferred.'),
 ('remove a battery from the thermostat','remove',B,None,T,'right',[T],[B,C],None),
 ('turn the battery over beside the thermostat','flip',B,None,None,'right',[T],[B,C],'t=107–111.8s rotate removed battery; t=113.8s begin insertion. Do not infer polarity from task expectation.'),
 ('insert the battery back into the thermostat','insert',B,None,T,'right',[T],[C],None),
 ('close the thermostat battery cover','close',C,None,T,'right',[T],[],'t=115.8s bring cover to opening; t=116.1–119.7s press cover into place.'),
 ('inspect the powered thermostat display','inspect',T,None,None,'both',[T],[],'t=120.4s digits visible; t=124.3s rotate unit and raise toward wall.'),
 ('attach the thermostat to the wall','attach',T,None,None,'left',[],[],'t=125–128.4s align and press to wall; t=128.7s release.'),
 ('press the thermostat controls','press',T,None,None,'right',[],[],'t=129–131s no hand interaction; t=131.5–132.8s press lower control.'),
 ('press the upper thermostat control','press',T,None,None,'right',[],[],'t=134.2–134.6s press upper control; then no interaction through end of segment.')]
 fine=[];start=0
 for i,(row,old) in enumerate(zip(rows,src[v]['segments'])):
  summary,verb,obj,tool,target,hands,left,right,note=row
  fine.append(dict(start=start,end=old['end_time'],summary=summary,verb=verb,object=obj,tool=tool,target=target,hands=hands,in_hand_at_end={'left':left,'right':right},type='action',ambiguous=False,boundary_note=note,beyond_video_end=False,confidence='high',old_summary=old.get('summary',''),notes='',transition_in=None))
  start=old['end_time']
 # Exact object grip is partly occluded at the first extraction end.
 fine[8].update(ambiguous=True,confidence='medium',notes='Exact battery grip at42.333s is partly hidden by right fingers.')
 groups=[(0,7,'Expose the thermostat battery compartment','Remove the thermostat from the wall and inspect its back. Try levering the battery cover with a butter knife, fetch a screwdriver, pry the cover free and put both cover and screwdriver on the stool.','Expose the cells so they can be replaced.'),(8,18,'Remove and set aside the old batteries','Remove both batteries and put the thermostat down. Collect the cells in the left hand, rub their terminals with a cotton swab, pick the thermostat up again, carry the removed cells to the bin and return to the stool.','Clear the battery compartment before fitting replacement cells; the observed handling includes terminal wiping and release into a bin.'),(19,25,'Install replacement batteries and inspect the display','Take two cells from the battery pack and insert them sequentially. Pick up the cover, turn the thermostat between front and back, and inspect its display and battery placement.','Attempt to restore power and check the visible result before reassembly.'),(26,29,'Reposition a battery and close the compartment','Remove one of the inserted cells, rotate it while holding the cover, put it back and press the cover into place.','Complete the observed battery rework and enclose the compartment.'),(30,33,'Remount the thermostat and check its controls','Inspect the display after digits appear, align the thermostat with its wall mount and release it. Press the lower and upper controls, then leave the mounted thermostat in view.','Return the powered thermostat to the wall and check its controls.')]
 coarse=[]
 for a,b,instruction,description,contribution in groups:coarse.append(dict(start=fine[a]['start'],end=fine[b]['end'],fine_index_range=[a,b],instruction=instruction,description=description,goal_contribution=contribution,transition_in=None))
 for i,s in enumerate(fine):
  held=[] if i==0 else sum(fine[i-1]['in_hand_at_end'].values(),[])
  s['transition_in']=None if i==0 else 'NONE' if s['type']=='idle' else 'STRONG' if any(x and x in held for x in [s['object'],s['tool']]) else 'WEAK'
 for c in coarse:c['transition_in']=fine[c['fine_index_range'][0]]['transition_in']
 d=dict(video_id=v,duration=inv[v],**{k:src[v].get(k) for k in ['task','domain','query']},goal={'title':'Replace the thermostat batteries and restore its display','description':'Detach the thermostat, open its battery cover with a screwdriver after trying a butter knife, and remove the two old cells. Handle and wipe the removed batteries, release them into a bin, then insert replacement cells from a pack. Inspect the blank display, remove and rotate one cell, reinstall it, close the cover, verify that digits appear, and reattach the thermostat to the wall.','final_state':'The thermostat is mounted on the wall with digits visible; the person has pressed its controls and withdrawn their hands.','procedure':[dict(start=c['start'],end=c['end'],description=c['description']) for c in coarse]},phases=[dict(start=c['start'],end=c['end'],description=c['description']) for c in coarse],object_inventory=inventory,notes='Only source fine boundaries are treated as trusted. All action descriptions and subtask groups were rewritten from timestamped video. Initial battery insertion is followed by inspection and one-cell rework; no battery polarity or hidden electrical fault is inferred. End-held lists describe grasped objects, not merely touched mounted surfaces. Unannotated tail136.4–141.267s (4.867s): no hand interaction, mounted thermostat remains visible. No steps added. Additional verbs carry and rub are expressed using move/wipe canonical verbs. Detailed goal includes all observed stages; next-subtask predictability is pending independent past-only evaluation.',fine=fine,coarse=coarse,evidence_manifest=str(next((O/'frames_v2'/v).glob('*/manifest.json'))))
 path=O/'videos'/f'{v}.json';assert not path.exists();path.write_text(json.dumps(d,indent=2)+'\n');return d
if __name__=='__main__':thermostat()
