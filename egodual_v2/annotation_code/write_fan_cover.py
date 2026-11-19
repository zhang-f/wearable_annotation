from build_root_batch import *
v='d95755db6e6f482f';C='fan cover';SC='screw';D='screwdriver';CL='cleaning cloth';P='breaker panel';SW='circuit breaker switch';H='fan housing';COUNTER='counter';ST='step stool'
rows=[]
def add(summary,verb,obj,tool=None,target=None,hands='both',left=None,right=None,note=None,ambiguous=False):rows.append(dict(summary=summary,verb=verb,object=obj,tool=tool,target=target,hands=hands,in_hand_at_end={'left':left or [],'right':right or []},type='action',ambiguous=ambiguous,boundary_note=note,confidence='medium' if ambiguous else 'high',notes=''))
add('reach for the breaker panel','reach for',P,hands='right')
add('open the breaker panel','open',P,hands='right')
add('flip a circuit breaker switch','adjust',SW,hands='right',note='Switch direction and printed circuit identity cannot be read; no off/on state asserted.')
add('withdraw the hand from the breaker panel','move',P,hands='right')
add('move to the bathroom work area','move',ST,hands='unclear',note='t=5–10s enter bathroom and climb toward vent; no hand-held object at segment end.',ambiguous=True)
add('grasp the fan cover beside its screw','hold',C,left=[C],right=[SC])
add('unscrew the right fan cover screw by hand','unscrew',SC,hands='right',left=[C],right=[SC])
add('unscrew the left fan cover screw by hand','unscrew',SC,hands='left',left=[SC],right=[C])
add('pull the fan cover away from the wall','remove',C,left=[C],right=[C])
add('carry the fan cover to the sink counter','move',C,target=COUNTER,left=[C],right=[C])
add('place the fan cover on the counter','place',C,target=COUNTER,left=[C],right=[C],note='t=33s lay cover down; hands still steady its edges at33.533s.')
add('place a cover screw on the counter','place',SC,target=COUNTER,hands='right',right=[SC],note='t=34–35s handle loose screws beside the screwdriver; exact individual screw identity is indistinguishable.')
add('transfer a cover screw between the hands','move',SC,left=[SC],right=[SC],ambiguous=True,note='t=35.5–36.5s small fastener is partly hidden between fingertips; does not establish which of identical screws is held.')
add('put down the cover screw on the counter','put down',SC,target=COUNTER,hands='left')
add('pick up the cleaning cloth','pick up',CL,hands='right',right=[CL])
add('wipe the front of the fan cover','wipe',C,CL,hands='right',left=[C],right=[CL])
add('wipe the back and edges of the fan cover','wipe',C,CL,hands='right',left=[C],right=[CL],note='t=41.4s flip cover, t=42–48s wipe rear slats and rim; boundaries preserved.')
add('place the fan cover on the counter','place',C,target=COUNTER,hands='left',right=[CL])
add('raise the cleaning cloth toward the fan housing','move',CL,hands='left',left=[CL],note='t=51–53s climb toward open housing while raising cloth.')
add('wipe around the exposed fan housing','wipe',H,CL,hands='left',left=[CL],note='t=54–63s wipe housing rim and accessible interior; do not infer invisible wiring work.')
add('carry the cleaning cloth back to the counter','move',CL,target=COUNTER,hands='both',right=[CL])
add('put down the cleaning cloth on the counter','put down',CL,target=COUNTER,hands='right',left=[C],note='t=66.0s take cover, t=67s set cloth aside.')
add('pick up a cover screw','pick up',SC,hands='left',left=[SC],right=[C])
add('position the screw in the fan cover hole','insert',SC,target=C,hands='left',left=[SC],right=[C])
add('adjust the screw in the fan cover hole','adjust',SC,target=C,hands='left',left=[C],right=[C])
add('steady the fan cover on the counter','hold',C,left=[C],right=[C])
add('pick up the screwdriver','pick up',D,hands='left',left=[D],right=[C])
add('carry the fan cover and screwdriver toward the wall','move',C,left=[D],right=[C])
add('raise the fan cover toward the housing','move',C,target=H,left=[D],right=[C])
add('align the fan cover with the housing','place',C,target=H,left=[D,C],right=[SC])
add('turn the cover screw by hand','screw',SC,hands='right',left=[D,C],right=[SC])
add('adjust the cover screw and realign the fan cover','adjust',SC,hands='right',left=[D,C],right=[SC],note='t=94–102s repeatedly try screw; t=103s change grip and steady cover.')
add('try to seat the cover screw','screw',SC,hands='right',left=[D],right=[C],note='t=104–110s repeated fastener alignment; attachment is not yet successful.')
add('remove the misaligned fan cover','remove',C,left=[D],right=[C])
add('put down the screwdriver on the counter','put down',D,target=COUNTER,hands='left',right=[C],note='t=113–115s lower cover and driver; driver is left on counter.')
add('reposition the fan cover over the housing','place',C,target=H,left=[SC],right=[C],note='t=116–124s lift/reseat cover repeatedly; t=125–129s begin holding and turning left fastener.')
add('turn the left cover screw by hand','screw',SC,hands='left',left=[SC],right=[C])
add('adjust the left cover screw by hand','adjust',SC,hands='left',left=[SC],right=[C])
add('screw the left fastener into the housing','screw',SC,hands='left',left=[C],right=[C])
add('turn the right cover screw by hand','screw',SC,hands='right',left=[C],right=[SC])
add('pick up the screwdriver from the counter','pick up',D,hands='right',right=[D])
add('position the screwdriver on the right cover screw','place',D,target=SC,hands='right',left=[C],right=[D],note='t=153–155s retrieve driver and rise; t=156–160s align tip on screw.')
add('tighten the right cover screw with the screwdriver','screw',SC,D,hands='right',right=[D])
add('continue tightening the right cover screw','screw',SC,D,hands='right',right=[D])
add('finish tightening and press the fan cover','press',C,hands='left',left=[C],right=[D],note='t=189–191s final driver turns then t=191.4s press cover with left palm.')
add('put down the screwdriver on the step stool','put down',D,target=ST,hands='right',note='t=192s lower arms, t=193–195s descend, t=195.3s place driver on stool.')
add('return to the breaker panel','move',P,hands='right',note='t=196–198s walk out; t=198.9s right hand reaches breaker.')
add('flip the circuit breaker switch','adjust',SW,hands='right',note='0.1s source segment retained; boundary lies in visible breaker interaction, no switch direction inferred.')
add('close the breaker panel','close',P,hands='left',note='t=199.1–199.6s finish breaker interaction, t=200.3–201.5s close panel door.')
assert len(rows)==49
fine=[];start=0
for i,(s,old) in enumerate(zip(rows,src[v]['segments'])):
 s.update(start=start,end=old['end_time'],old_summary=old.get('summary',''),beyond_video_end=False,transition_in=None);fine.append(s);start=old['end_time']
for i,s in enumerate(fine):
 held=[] if not i else sum(fine[i-1]['in_hand_at_end'].values(),[]);s['transition_in']=None if not i else 'STRONG' if any(x and x in held for x in [s['object'],s['tool']]) else 'WEAK'
groups=[(0,3,'Operate the circuit breaker before working on the cover','Reach up, open the breaker panel, flip a switch and withdraw the hand. The switch label and direction cannot be established from the frames.','Perform the observed initial breaker operation before approaching the bathroom vent.'),(4,13,'Remove the fan cover and set aside its screws','Move into the bathroom, steady the cover and unscrew its right and left fasteners by hand. Pull the cover away, take it to the sink counter and set down the cover and loose screws.','Expose the housing and bring the removable cover to the cleaning surface.'),(14,21,'Wipe the fan cover and exposed housing','Take the pink cloth and wipe the front, rear, slats and edges of the cover. Set the cover down, raise the cloth to the open housing, wipe the accessible rim/interior, then return and set the cloth aside.','Clean the removable grille and exposed housing surfaces before reinstallation.'),(22,34,'Prepare the cover and attempt to refit it','Take a fastener, position it in a cover hole, collect the screwdriver and bring the cover back to the wall. Try to align and thread the fastener, adjust the cover repeatedly, then remove it and set the screwdriver down.','Prepare the cleaned cover for mounting and record the first unsuccessful alignment attempt.'),(35,40,'Reseat the cover and start the mounting screws','Raise and reseat the cover repeatedly, turn the left screw by hand and then work the right screw. Retrieve the screwdriver after the cover is held in position.','Align the cover and start the fasteners before tightening with the tool.'),(41,45,'Tighten the cover screws and lower the screwdriver','Position the driver on the right screw and turn it repeatedly. Finish the visible tightening, press the cover, descend and place the screwdriver on the step stool.','Secure the reinstalled cover and set the tool aside.'),(46,48,'Operate the breaker and close the panel','Return to the open breaker panel, flip the switch and close the panel door.','Finish the observed post-maintenance breaker operation; no fan sound or operation is inferred.')]
coarse=[dict(start=fine[a]['start'],end=fine[b]['end'],fine_index_range=[a,b],instruction=ins,description=desc,goal_contribution=con,transition_in=fine[a]['transition_in']) for a,b,ins,desc,con in groups]
# Keep instructions concise without changing observed content.
coarse[0]['instruction']='Operate the breaker before removing the cover'
d=dict(video_id=v,duration=inv[v],**{k:src[v].get(k) for k in ['task','domain','query']},goal=dict(title='Clean and reinstall the bathroom fan cover',description='Open the breaker panel and operate a switch, then enter the bathroom and remove the blue grille cover by undoing its two fasteners. Wipe both sides and slats of the cover with a pink cloth and wipe the exposed housing. Prepare the cover screws and repeatedly attempt to realign the grille, set down the screwdriver and reseat the cover, then start the fasteners by hand and tighten the right fastener with the screwdriver. Press the mounted cover, set the tool on the step stool, return to the breaker panel, operate the switch again and close the panel.',final_state='The blue cover is refitted over the wall housing and the breaker panel is closed. No audio or airflow evidence establishes fan operation.',procedure=[dict(start=c['start'],end=c['end'],description=c['description']) for c in coarse]),phases=[dict(start=c['start'],end=c['end'],description=c['description']) for c in coarse],object_inventory=[C,SC,D,CL,P,SW,H,COUNTER,ST],notes='Only human fine boundaries trusted. All877 dense sampled frames, complete overview and49 native end frames inspected. Subtasks newly grouped from actual steps; repeated failed refitting is preserved in narrative. Circuit breaker switch direction and labels unreadable, so off/on state is not asserted. Fixed panel/cover counted as held only while fingers grip/support them. Original0.1s segment47 preserved. Tail202.15–202.467s shows closed panel with no further task interaction. Predictability pending independent prior-context assessment.',fine=fine,coarse=coarse,evidence_manifest=str(next((O/'frames_v2'/v).glob('*/manifest.json'))))
p=O/'videos'/f'{v}.json';assert not p.exists();p.write_text(json.dumps(d,indent=2)+'\n')
