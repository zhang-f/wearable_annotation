from build_pilot import SOURCE,DURATION,OUT,save
from validate import validate
import json,datetime

def row(summary,verb,obj,tool=None,target=None,hands='both',left=(),right=(),note=None,amb=False,notes=''):
 return [summary,verb,obj,tool,target,hands,list(left),list(right),dict(boundary_note=note,ambiguous=amb,confidence='medium' if amb else 'high',notes=notes)]

def finish(v,goal,procedure,inv,rows,groups,notes):
 path=OUT/'videos'/f'{v}.json'
 if path.exists():raise RuntimeError('Refusing to overwrite existing annotation '+str(path))
 phases=[(a,b,c) for a,b,c in procedure]
 d=save(v,goal,phases,inv,rows,[g[:4] for g in groups],notes)
 d['goal']['procedure']=[dict(start=a,end=b,description=c) for a,b,c in procedure]
 for c,g in zip(d['coarse'],groups):c['goal_contribution']=g[4]
 d['annotation_provenance']={'method':'overview followed by every fine dense interval and native end-state review','evidence_directory':f'frames/{v}/native_v1','fine_boundaries':'preserved human divisions','description_source':'independent visual rewrite; old_summary kept for provenance only','predictability':'not assessed by annotator who viewed future'}
 result=validate(d,SOURCE[v],DURATION[v]);assert not result['errors'],result
 path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 (OUT/f'validation_{v}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 with (OUT/'batch01_progress.jsonl').open('a') as f:f.write(json.dumps(dict(video_id=v,status='completed',fine_count=len(rows),coarse_count=len(groups),ambiguous=sum(x['ambiguous'] for x in d['fine']),boundary_notes=sum(bool(x['boundary_note']) for x in d['fine']),completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),ensure_ascii=False)+'\n')
 return d

def smoke():
 v='4918e35d642df5a0';S='smoke detector';B='battery';rows=[
 row('idle: approach the smoke detector',None,None,hands='unclear'),
 row('twist the smoke detector on its mounting plate','twist',S,left=[S],right=[S]),
 row('twist the smoke detector on its mounting plate','twist',S,note='t=8.1–11.3s another twist attempt, release at t=11.5s; boundary at 7.6s interrupts repeated grip-and-twist attempts.'),
 row('twist the smoke detector off its mounting plate','twist',S,target='mounting plate',hands='right',right=[S],note='t=11.5–13s hands release; t=13.3s regrasp and twist; t=17.267s body starts separating.'),
 row('lower the smoke detector from the wall','move',S,hands='both',left=[S],right=[S]),
 row('open the smoke detector battery compartment','open',S,hands='right',left=[S]),
 row('pull out the smoke detector battery tray','pull',S,left=[S],right=[S],note='t=23.5–29.5s repeated tray pulling and regripping; housing occludes exact electrical contact.'),
 row('remove the battery from the smoke detector','remove',B,target=S,left=[B],right=[S]),
 row('move the battery away from the smoke detector','move',B,hands='left',left=[B],right=[S]),
 row('pick up a replacement battery','pick up',B,hands='right',left=[S],right=[B],note='t=33.2s lower old battery out of view; t=35.3–36.5s reach to battery package and retrieve replacement.'),
 row('align the battery with the smoke detector compartment','align',B,target=S,hands='right',left=[S],right=[B]),
 row('insert the battery into the smoke detector','insert',B,target=S,hands='right',left=[S],right=[S],note='t=42.1–45s insert battery; t=45.3–46s push compartment shut.'),
 row('close the smoke detector battery compartment','close',S,left=[S],right=[S],note='t=46.0–46.6s continues preceding compartment closure; no new hand-object change.'),
 row('turn the smoke detector in both hands','turn',S,left=[S],right=[S]),
 row('press the smoke detector test button','press',S,hands='right',left=[S],note='t=48.3–53.8s right thumb presses test button; t=54.2s releases. Video has no audio, so no claim that alarm sounded.'),
 row('open the smoke detector battery compartment','open',S,hands='right',left=[S]),
 row('remove the battery from the smoke detector','remove',B,target=S,hands='right',left=[S],right=[B],notes='differs_from_expectation: after first installation and test-button press, battery is removed again rather than immediately remounting detector.'),
 row('turn the battery in the right hand','turn',B,hands='right',left=[S],right=[B]),
 row('align the battery with the smoke detector compartment','align',B,target=S,hands='right',left=[S],right=[B]),
 row('insert the battery into the smoke detector','insert',B,target=S,hands='right',left=[S],right=[S],note='t=65.3–68.7s seat battery after rotating it; t=69–70.9s close compartment.'),
 row('close the smoke detector battery compartment','close',S,left=[S],right=[S],note='t=70.9–71.8s continues closing then rotates detector toward test button.'),
 row('press the smoke detector test button','press',S,hands='right',left=[S],right=[S]),
 row('turn the smoke detector toward the mounting plate','turn',S,left=[S],right=[S]),
 row('raise the smoke detector toward the mounting plate','move',S,target='mounting plate',hands='right',right=[S]),
 row('twist the smoke detector onto the mounting plate','twist',S,target='mounting plate',hands='right',note='t=78.5–83.4s align and twist detector into plate; t=83.8–84.6s both hands check attachment; t=85.1–86.1s press test button. Compound interval retained.'),
 row('idle: inspect the mounted smoke detector',None,None,hands='unclear')]
 procedure=[(0,17.29,'Approach the wall-mounted detector. Grip and twist it several times, briefly releasing and trying again, until its body begins to detach from the circular mounting plate.'),(17.29,33,'Lower and turn the detector, open its battery door, pull the tray outward and work the blue rectangular battery free. Move the removed battery away from the detector.'),(33,54.31,'Lower the old battery and retrieve another from packaging on the nearby stool. Turn the new battery toward the compartment, slide it inside, close the door and press the front test button while holding the detector.'),(54.31,71.8,'Open the battery door again, remove the same replacement battery, rotate it in the right hand and make several alignment attempts. Seat it again and press the compartment shut.'),(71.8,88.4,'Press the test button again; a red indicator illuminates. Change grip, raise the detector to its mounting plate and twist it into place. Check its attachment with both hands, press the mounted test button and withdraw the hands. No audible test result is available.')]
 return finish(v,['Replace the smoke detector battery','Detach a wall-mounted smoke detector and exchange its rectangular battery. Reopen the compartment to adjust the replacement, test the detector, then twist it back onto its mounting plate.','The detector is back on its wall plate with the battery door closed. A red indicator is visible during button presses; the silent video cannot establish alarm sound or electrical performance.'],procedure,[S,B,'mounting plate','battery package','stool'],rows,[(0,4,'Detach the smoke detector from its mounting plate','Approach the detector, repeatedly grip and twist its body, release and retry, then lower it away from the exposed mounting plate.','Makes the battery compartment accessible without the detector being mounted on the wall.'),(5,8,'Remove the existing smoke detector battery','Open the battery door, pull the tray outward, free the rectangular battery and move it away from the detector.','Removes the existing power source so it can be replaced.'),(9,14,'Install and check the replacement battery','Set the removed battery aside, retrieve a replacement, align and insert it, close the compartment, turn the detector and press its test button.','Places a replacement power source in the detector and performs an initial visible button check.'),(15,21,'Reseat the replacement battery and test again','Reopen the door, remove and rotate the battery, realign and seat it, close the compartment and press the front button again.','Corrects the initial installation attempt before returning the detector to its mount.'),(22,25,'Mount and check the smoke detector','Turn and raise the detector, align it with the wall plate, twist it into position, check its attachment, press its button and inspect it after releasing.','Restores the detector to its installed position and checks the mounted unit.')],'All fine boundaries preserved. No soundtrack: button pressing and red light are visible, but successful audible alarm testing is not asserted. Replacement battery is distinguished from old one by the package retrieval; both use canonical battery as visually similar instances. Same battery is removed and reseated after first test. Fixed mounting plate is a target, never held. Hands holding detached detector support its body; button pressing alone on the mounted detector is not in_hand. Every dense page and native end frame reviewed; evidence uses PTS burn before fps.')
if __name__=='__main__':smoke()
