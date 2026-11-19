from build_root_batch import *
v='e9203b673adb9f69';bag='backpack';zipper='zipper slider';fabric='backpack fabric';bottle='oil bottle';cap='bottle cap';swab='cotton swab';metal='metal tool';laptop='laptop'
rows=[]
def row(summary,verb,obj,tool=None,target=None,hands='both',left=None,right=None,note=None,ambiguous=False):rows.append(dict(summary=summary,verb=verb,object=obj,tool=tool,target=target,hands=hands,in_hand_at_end={'left':left or [],'right':right or []},type='idle' if obj is None else 'action',ambiguous=ambiguous,boundary_note=note,confidence='medium' if ambiguous else 'high',notes=''))
row('idle: sit facing the backpack',None,None,hands='unclear')
row('lift and reposition the backpack','move',bag,left=[bag],right=[zipper])
for i in range(2,7):row('pull the zipper slider along the backpack','move',zipper,hands='right',left=[bag],right=[zipper])
row('pull fabric away from the zipper slider','remove',fabric,left=[fabric],right=[zipper])
row('release the backpack fabric','put down',fabric,hands='left',right=[zipper])
row('pick up the oil bottle','pick up',bottle,hands='left',left=[bottle])
row('unscrew the oil bottle cap','unscrew',cap,hands='right',left=[bottle],right=[cap])
row('put down the bottle cap on the backpack','put down',cap,target=bag,hands='right',left=[bottle])
row('dip the cotton swab into the oil bottle','insert',swab,target=bottle,hands='right',left=[bottle],right=[swab],note='t=29.1s pick up swab, then t=30–37s dip/rub it repeatedly around bottle opening; compound segment.')
row('screw the cap onto the oil bottle','screw',cap,target=bottle,hands='right',left=[bottle],right=[swab],note='t=38.1s pick up cap while retaining swab, t=39–41s screw cap on.')
row('put down the oil bottle beside the backpack','put down',bottle,hands='left',right=[swab])
row('rub the zipper slider with the cotton swab','wipe',zipper,swab,hands='right',left=[zipper],right=[swab])
row('pull the zipper slider along the backpack','move',zipper,hands='left',left=[zipper],right=[swab])
row('rub beside the zipper slider with the cotton swab','wipe',zipper,swab,hands='right',left=[zipper],right=[swab])
row('work fabric away from the zipper slider','remove',fabric,swab,hands='both',left=[fabric],right=[swab],note='t=52–68s repeatedly pick/probe fabric and slider with fingers/swab; no hidden repair inferred.')
row('put down the cotton swab on the backpack','put down',swab,target=bag,hands='right',note='t=69.5s lower swab; t=69.8–70.0s left hand moves laptop beside backpack.')
row('pick up the metal tool','pick up',metal,hands='right',right=[metal],ambiguous=True,note='t=70.8–71.4s collect a narrow metal tool; its exact class is unclear, so named generically.')
row('reposition the backpack on the lap','move',bag,hands='left',left=[bag],right=[metal])
row('grasp the zipper slider','hold',zipper,hands='left',left=[zipper],right=[metal])
row('inspect the fabric beside the zipper slider','inspect',fabric,hands='both',left=[zipper],right=[metal])
for i in range(24,34):
 row('work fabric away from the slider with the metal tool','remove',fabric,metal,hands='right',left=[zipper],right=[metal],ambiguous=True,note='The tool tip and fabric contact are partly obscured by fingers; narrow metal tool identity cannot be established. Action is visible probing/pulling around the slider, not a claimed part replacement.')
for i in range(34,43):
 row('pull the zipper slider back and forth','move',zipper,hands='both',left=[bag] if i in (34,36,38,40,42) else [zipper],right=[zipper,metal],note='Repeated visible testing of the same front-pocket zipper; metal tool remains between right fingers.')
row('set the backpack down after checking the zipper','place',bag,hands='both',left=[bag],right=[metal],note='t=116s move zipper, t=117s lower backpack; no new fine boundaries added.')
assert len(rows)==44
fine=[];start=0
for i,(s,old) in enumerate(zip(rows,src[v]['segments'])):
 s.update(start=start,end=old['end_time'],old_summary=old.get('summary',''),beyond_video_end=False,transition_in=None);fine.append(s);start=old['end_time']
for i,s in enumerate(fine):
 held=[] if not i else sum(fine[i-1]['in_hand_at_end'].values(),[])
 s['transition_in']=None if not i else 'NONE' if s['type']=='idle' else 'STRONG' if any(x and x in held for x in [s['object'],s['tool']]) else 'WEAK'
groups=[(0,8,'Inspect the stuck zipper and trapped fabric','Reposition the backpack, tug the front-pocket zipper repeatedly and pinch fabric beside its slider. Release the fabric after the initial attempts.','Identify the jam and attempt to release it by hand.'),(9,14,'Prepare an oiled cotton swab','Pick up the oil bottle and unscrew its cap. Put the cap down, take a cotton swab, wet it at the bottle opening, close the bottle and set it aside.','Prepare the applicator used on the stuck slider.'),(15,19,'Lubricate the slider and loosen the fabric','Rub the slider with the swab, tug the pull and repeatedly work at the adjacent fabric. Put the swab on the backpack and shift the laptop beside it.','Attempt to free the jam using the wetted swab and fingers.'),(20,33,'Work trapped fabric out with a metal tool','Take a narrow metal tool, reposition the backpack and hold the slider close. Repeatedly probe and pull the fabric beside the slider while holding it steady.','Continue the repair after the swab and finger attempts; exact tool identity remains uncertain.'),(34,43,'Test the zipper movement and set down the backpack','Move the slider back and forth along the pocket opening several times, repositioning the fabric and the backpack. Lower the backpack at the end while retaining the metal tool.','Check the observed movement after working on the jam; no unseen durability test is claimed.')]
coarse=[]
for a,b,ins,desc,con in groups:coarse.append(dict(start=fine[a]['start'],end=fine[b]['end'],fine_index_range=[a,b],instruction=ins,description=desc,goal_contribution=con,transition_in=fine[a]['transition_in']))
d=dict(video_id=v,duration=inv[v],**{k:src[v].get(k) for k in ['task','domain','query']},goal=dict(title='Free the stuck front-pocket zipper on a backpack',description='Inspect and tug the zipper and fabric at the front pocket. Wet a cotton swab with liquid from the oil bottle, close the bottle and rub the swab around the slider while trying to free nearby fabric. Put the swab down, use a narrow metal tool to work repeatedly beside the slider, then move the zipper back and forth to check it and set down the backpack.',final_state='The front-pocket zipper slider is moved back and forth across the opening after the repair attempts. The backpack rests in front of the wearer; the metal tool is still held.',procedure=[dict(start=c['start'],end=c['end'],description=c['description']) for c in coarse]),phases=[dict(start=c['start'],end=c['end'],description=c['description']) for c in coarse],object_inventory=[bag,zipper,fabric,bottle,cap,swab,metal,laptop],notes='All source fine boundaries preserved. Entire overview, all673 dense sampled frames and native end contact sheets visually inspected. Metal tool type remains unclear and is deliberately generic; detailed grasping/probing interval is ambiguous rather than assumed to use pliers or a fork. Liquid is described as oil bottle from appearance/use, no chemical formulation inferred. Subtasks were regrouped from observed steps. Whole-task narrative includes unsuccessful repeated pulls and later tool work. Tail118.63–118.734s has no additional interaction. Predictability pending independent prior-context assessment.',fine=fine,coarse=coarse,evidence_manifest=str(next((O/'frames_v2'/v).glob('*/manifest.json'))))
p=O/'videos'/f'{v}.json';assert not p.exists();p.write_text(json.dumps(d,indent=2)+'\n')
