import json,csv,pathlib
ROOT=pathlib.Path('/home/fan/google'); OUT=ROOT/'review_run/annotation_v2'
SOURCE={d['video_path'][:-4]:d for d in map(json.loads,open(ROOT/'data_annotation/annotations_fine_completed.jsonl'))}
DURATION={d['video_id']:float(d['ffprobe_duration']) for d in csv.DictReader(open(ROOT/'review_run/video_inventory.csv'))}
def save(v,goal,phases,inventory,rows,groups,notes):
 src=SOURCE[v]; fine=[];start=0
 for i,(old,row) in enumerate(zip(src['segments'],rows)):
  summary,verb,obj,tool,target,hands,left,right,*extra=row;meta=extra[0] if extra else {}
  end=old['end_time']; beyond=end>DURATION[v]
  item=dict(start=start,end=end,summary=None if beyond else summary,verb=None if beyond else verb,object=None if beyond else obj,tool=None if beyond else tool,target=None if beyond else target,hands=hands,in_hand_at_end={'left':left,'right':right},type='idle' if summary.startswith('idle') else 'action',ambiguous=meta.get('ambiguous',False),boundary_note=meta.get('boundary_note'),beyond_video_end=beyond,confidence=meta.get('confidence','high'),old_summary=old.get('summary',''),notes=meta.get('notes',''))
  if item['type']!=old.get('type'):item['notes']+=' Type changed based on visible interaction.'
  if beyond:item['boundary_note']='超出视频结尾';item['ambiguous']=True;item['confidence']='low';item['in_hand_at_end']={'left':[],'right':[]}
  held=set(sum(fine[-1]['in_hand_at_end'].values(),[])) if fine else set()
  item['transition_in']=None if not fine else ('NONE' if item['type']=='idle' else 'STRONG' if (item['object'] in held or item['tool'] in held) else 'WEAK')
  fine.append(item);start=end
 assert len(rows)==len(src['segments'])
 coarse=[]
 for a,b,instr,desc in groups:coarse.append(dict(start=fine[a]['start'],end=fine[b]['end'],instruction=instr,description=desc,fine_index_range=[a,b],transition_in=fine[a]['transition_in']))
 d=dict(video_id=v,duration=DURATION[v],task=src.get('task'),domain=src.get('domain'),query=src.get('query'),goal=dict(zip(['title','description','final_state'],goal)),phases=[dict(start=a,end=b,description=c) for a,b,c in phases],object_inventory=inventory,notes=notes,fine=fine,coarse=coarse)
 (OUT/'videos'/f'{v}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 return d

def craft():
 return save('e531cded0108b6c3',[
 'Create a spray-painted heart resist on paper',
 'Arrange a heart-shaped paper mask on a white sheet and secure it with tape. Spray gold paint over the mask, remove it, and outline the resulting white heart with a purple marker.',
 'A white heart surrounded by gold paint and a purple outline remains on the sheet; a small mark is added below it.'],
 [(0,12,'Prepare the covered work surface and paper.'),(12,95,'Position and tape the heart mask.'),(95,137,'Spray paint over the mask.'),(137,165,'Remove the painted mask.'),(165,256.867,'Outline the heart and add a small mark.')],
 ['plastic sheet','paper sheet','heart mask','tape','scissors','spray paint can','spray paint cap','marker'],[
 ['press the plastic sheet flat','press','plastic sheet',None,None,'both',[],[],{'boundary_note':'t=0–2.7s no interaction, then t=3.0–4.3s both hands smooth plastic; one segment includes opening pause.'}],
 ['place the paper sheet on the plastic sheet','place','paper sheet',None,'plastic sheet','both',[],[]],
 ['place the heart mask on the paper sheet','place','heart mask',None,'paper sheet','both',[],[],{'boundary_note':'t=13.3s pick up mask, t=14.0s place it, t=16–17.7s press it; multiple hand–object changes.'}],
 ['pick up the tape','pick up','tape',None,None,'right',[],['tape']],
 ['pull a strip of tape from the roll','pull','tape',None,None,'both',['tape'],['tape'],{'notes':'pull is used for unrolling tape; not in the suggested verb list.'}],
 ['move the tape beside the paper sheet','move','tape',None,'paper sheet','right',[],['tape'],{'ambiguous':True,'confidence':'low','boundary_note':'t=32–35s hands are out of view; t=36.3s tape returns at the lap. Exact placement and grip at t=37.12s are partly occluded.'}],
 ['put down the tape beside the paper sheet','put down','tape',None,'paper sheet','right',[],['scissors'],{'boundary_note':'t=40.3s put down tape, t=45.3s pick up scissors; this segment contains distinct interactions.'}],
 ['spray the paper sheet around the heart mask','spray','paper sheet','spray paint can',None,'right',[],['marker'],{'boundary_note':'Large compound segment: t=50.7s cut tape; t=55s apply tape; t=68–86s attach/press mask; t=96s pick up paint can; t=106–120s spray; t=127s cap can; t=146–163s peel mask; t=167–173s draw with marker. Boundaries preserved.','confidence':'medium','notes':'spray and pull are necessary additional verbs. differs_from_expectation: one atomic step was expected, but this interval contains preparation, painting, mask removal and drawing.'}]
 ],[(0,2,'Prepare the paper and heart mask','Flatten the plastic cover, position the white paper and place the heart mask.'),(3,7,'Tape and paint around the heart mask','Prepare tape, secure the mask, spray the paper and begin outlining the revealed heart.')],
 'The preserved eight-step track cannot express all visually distinct subtask boundaries: final step spans 46.83–173s and crosses several intermediate goals. Only two coarse units are defensible without changing fine boundaries. First subtask has three steps, second five. Unannotated tail 173.0–256.867s (83.867s): t=174–236s right hand continues purple outline around heart while left steadies paper; t=238–243s marker rests briefly; t=246–251s marker writes small characters at lower left; t=254–256s hands withdraw. No new steps added. First-pass object vocabulary was retained; the mask is paper, not a rigid stencil inferred from task name.')
if __name__=='__main__':craft()
def cook():
 rows=[
 ['idle: walk to the dish rack',None,None,None,None,'unclear',[],[]],
 ['pick up the plate from the dish rack','pick up','plate',None,None,'right',[],['plate']],
 ['place the plate beside the microwave','place','plate',None,'counter','both',[],[]],
 ['pick up the tortilla chip bag','pick up','tortilla chip bag',None,None,'right',[],['tortilla chip bag']],
 ['place tortilla chips on the plate','place','tortilla chips',None,'plate','right',['tortilla chip bag'],[],{'boundary_note':'t=6.7s change grip on bag; t=7.3–8.7s retrieve chips and place on plate; hand–object changes within segment.'}],
 ['spread the tortilla chips across the plate','spread','tortilla chips',None,'plate','both',[],[]],
 ['pick up the cheese bag','pick up','cheese bag',None,None,'left',['cheese bag'],[]],
 ['open the cheese bag','open','cheese bag',None,None,'both',[],[],{'boundary_note':'t=13.7–14.7s open cheese bag, then t=15.3s set it aside. Both interactions occur within segment.'}],
 ['pick up another plate from the dish rack','pick up','plate',None,None,'left',['plate'],[],{'boundary_note':'t=15.9–18s walking without interaction; t=18.7–19.3s retrieve plate.'}],
 ['place the plate beneath the tortilla chip plate','place','plate',None,'plate','both',[],['plate'],{'boundary_note':'t=21.7s grasp chip plate, t=22.7s set spare plate down, t=23s stack plates; multiple interactions.'}],
 ['move the plate beside the tortilla chips','move','plate',None,'counter','both',['plate'],[]],
 ['put down the plate on the counter','put down','plate',None,'counter','left',[],['cheese bag'],{'boundary_note':'t=25s place spare plate; t=25.7s pick up cheese bag.'}],
 ['hold the cheese bag above the tortilla chips','hold','cheese bag',None,None,'right',[],['cheese bag']],
 ['open the cheese bag','open','cheese bag',None,None,'both',['cheese bag'],['cheese bag']],
 ['pour shredded cheese over the tortilla chips','pour','shredded cheese','cheese bag','tortilla chips','right',[],['cheese bag']],
 ['close the cheese bag','close','cheese bag',None,None,'both',[],[],{'boundary_note':'t=38.3–40.3s close bag; t=40.7s move bag off to side.'}],
 ['pick up the plate of tortilla chips','pick up','plate',None,None,'right',[],['plate'],{'boundary_note':'t=41.3s press microwave control; t=42.3s grasp plate.'}],
 ['open the microwave door','open','microwave',None,None,'left',[],['plate']],
 ['place the plate inside the microwave','place','plate',None,'microwave','right',[],[]],
 ['close the microwave door','close','microwave',None,None,'left',[],[],{'boundary_note':'45.10–45.20s lies inside the ongoing door-closing motion visible t=45.0–45.6s; no separate interaction at cut.'}],
 ['turn on the microwave','turn on','microwave',None,None,'right',[],[]],
 ['idle: wait beside the microwave',None,None,None,None,'both',[],[]],
 ['reach for the microwave handle','reach for','microwave',None,None,'right',[],[]],
 ['open the microwave door','open','microwave',None,None,'right',[],[]],
 ['remove the plate from the microwave','remove','plate',None,'counter','right',[],['plate']],
 ['put down the plate beside the microwave','put down','plate',None,'counter','right',[],[],{'boundary_note':'t=79.3s left hand closes microwave while right hand places plate at t=80.1s.'}],
 ['pick up a tortilla chip from the plate','pick up','tortilla chips',None,None,'right',[],['tortilla chips']],
 ['put down the tortilla chip on the plate','put down','tortilla chips',None,'plate','right',[],[]],
 ['idle: pause beside the plate',None,None,None,None,'both',[],[]],
 ['reach for the seasoning jar','reach for','seasoning jar',None,None,'left',[],[]],
 ['open the seasoning jar','open','seasoning jar',None,None,'both',['seasoning cap'],['seasoning jar']],
 ['shake seasoning over the tortilla chips','shake','seasoning jar',None,'tortilla chips','right',['seasoning cap'],['seasoning jar']],
 ['close the seasoning jar','close','seasoning jar',None,None,'both',['seasoning jar'],[]],
 ['put down the seasoning jar','put down','seasoning jar',None,'counter','left',[],[]],
 ['pick up a tortilla chip from the plate','pick up','tortilla chips',None,None,'right',[],['tortilla chips']],
 ['idle: taste the tortilla chip',None,None,None,None,'right',[],[] ,{'notes':'Eating is treated as idle because this step is consumption rather than preparation.'}],
 ['move the spare plate to the left','move','plate',None,'counter','left',['plate'],[]],
 ['put down the fork on the spare plate','put down','fork',None,'plate','left',[],['salt shaker'],{'boundary_note':'t=106s place spare plate; t=108.7s pick up fork; t=109.3s put fork down; t=109.7s pick up salt shaker.'}],
 ['hold the salt shaker over the tortilla chips','hold','salt shaker',None,None,'right',[],['salt shaker']],
 ['shake salt over the tortilla chips','shake','salt shaker',None,'tortilla chips','right',[],[],{'boundary_note':'t=110.9–112.6s shake salt; t=113s return shaker to counter.'}],
 ['idle: pause beside the tortilla chips',None,None,None,None,'both',[],[]],
 ['reach for the fork','reach for','fork',None,None,'left',[],[]],
 ['idle',None,None,None,None,'unclear',[],[]]
 ]
 return save('3a122ee7ff513956',[
 'Prepare microwave cheese tortilla chips',
 'Arrange tortilla chips on a plate and pour shredded cheese over them. Heat the plate briefly in the microwave, add seasoning and salt, and begin separating the chips with a fork.',
 'Cheese-topped chips are on the counter with seasoning and salt added; the final visible interaction uses a fork.'],
 [(0,12.1,'Collect a plate and arrange tortilla chips.'),(12.1,40.9,'Fetch another plate and add shredded cheese.'),(40.9,80.97,'Heat the chips and remove the plate.'),(80.97,124.667,'Check, season and separate the chips.')],
 ['plate','counter','tortilla chip bag','tortilla chips','cheese bag','shredded cheese','microwave','seasoning jar','seasoning cap','salt shaker','fork'],rows,
 [(0,5,'Arrange tortilla chips on a plate','Collect a plate and spread tortilla chips across it.'),(6,15,'Cover the tortilla chips with shredded cheese','Prepare a spare plate, open the cheese bag and distribute cheese over the chips.'),(16,25,'Heat the chips in the microwave','Load and start the microwave, wait, then remove and set down the plate.'),(26,42,'Season and check the cheese tortilla chips','Inspect the chips, add seasoning and salt, and prepare to separate them with a fork.')],
 'Strict beyond-video rule: final step 115.0–124.7 exceeds ffprobe 124.667 by 0.033s, so description and object fields are null and beyond_video_end=true; boundary not clipped. No uncovered tail. Repeated open-cheese-bag instruction reflects two separate bag handling episodes with a spare-plate fetch in between. Physical dish rack is not a tool. Holding means grasping/supporting, not merely resting fingers on the counter. Heating wait and tasting are idle, attributed to preceding subtask. Fine steps shorter than one second examined at 15 fps. Verb pour used for cheese shaken directly from bag; no spoon inferred. In-hand vocabulary uses packaging as the held object, loose food as the transferred object.')
def curtain():
 rows=[]
 def r(summary,verb,obj,tool=None,target=None,hands='both',left=(),right=(),note=None,amb=False):
  rows.append([summary,verb,obj,tool,target,hands,list(left),list(right),dict(boundary_note=note,ambiguous=amb,confidence='medium' if amb else 'high')])
 r('put down the tape measure','put down','tape measure',target='floor',hands='right',note='t=1.3–2.2s put tape measure down; t=2.3s reach toward marker.')
 r('gather the curtain beside the wall','gather','curtain',left=['curtain'],right=['curtain'],note='t=2.3–6s pause, then t=6–12s gather curtain; opening pause shares this step.')
 r('pick up the curtain hook','pick up','curtain hook',hands='left',left=['curtain'],right=['curtain hook'],note='t=14.3s retrieve hook; t=16.3s left hand grasps curtain while right holds hook.')
 r('hold the curtain hook against the wall','hold','curtain hook',target='wall',hands='right',right=['curtain hook'])
 r('mark the wall through the curtain hook','mark','wall','marker','curtain hook',left=['marker'],right=['curtain hook'],note='t=24.7s pick up marker, then t=25–28s mark through hook.')
 r('mark the wall through the curtain hook','mark','wall','marker','curtain hook',left=['marker'],right=['curtain hook'],note='t=28.47s cut falls inside continuous marking, visible on both sides.')
 r('put down the curtain hook','put down','curtain hook',target='floor',hands='right',left=['marker'],note='t=34s remove hook from wall; t=36s inspect; t=39–40s lower to floor.')
 r('extend the tape measure','extend','tape measure',left=['tape measure'],right=['tape measure'],note='t=40.7s put marker down; t=42s pick up tape measure; t=43s extend tape.')
 r('measure the space beside the curtain','measure','wall','tape measure',hands='both',left=['tape measure'],right=['tape measure'])
 r('put down the tape measure','put down','tape measure',target='floor',hands='right',note='t=51s retract tape and t=52s lower measure to floor.')
 r('hold the curtain hook against the wall','hold','curtain hook',target='wall',right=['curtain hook'],note='t=55.6s pick hook up, then t=56–59s align it with marks.')
 r('mark the wall through the curtain hook','mark','wall','marker','curtain hook',left=['marker'],right=['curtain hook'],note='t=60.3s retrieve marker; t=62–65s mark holes.')
 r('mark the wall through the curtain hook','mark','wall','marker','curtain hook',left=['marker'],right=['curtain hook'],note='t=65.33s boundary divides ongoing marking without a new object interaction.')
 r('put down the curtain hook','put down','curtain hook',target='floor',hands='right',left=['marker'],note='t=68–70s adjust hook; t=71s lower it to floor.')
 r('pick up the drill bit bag','pick up','drill bit bag',right=['drill bit bag'],left=['drill bit bag'],note='t=71.7s put marker down; t=72.7s pick up drill and t=74s put it down; t=74.3s retrieve bit bag.')
 r('open the drill bit bag','open','drill bit bag',left=['drill bit bag'],right=['drill bit bag'])
 r('remove drill bits from the bag','remove','drill bit',target='drill bit bag',left=['drill bit'],right=['drill bit bag'])
 r('put down the drill bit bag','put down','drill bit bag',target='floor',hands='right',left=['drill bit'],note='t=89.7–92s remove bit, t=92.5s put bag down.')
 r('hold the drill bits','hold','drill bit',hands='left',left=['drill bit'])
 r('select a drill bit','select','drill bit',left=['drill bit'],right=['drill bit'],note='t=95–96.7s compare bits; t=97s lower one toward floor.')
 r('pick up the drill','pick up','drill',hands='left',left=['drill'],right=['drill bit'])
 r('insert the drill bit into the drill','insert','drill bit',target='drill',left=['drill'],right=['drill'])
 r('tighten the drill chuck','tighten','drill',left=['drill'],right=['drill'])
 r('drill a hole in the wall','drill','wall','drill',left=['drill'],right=['drill'])
 r('withdraw the drill from the wall','withdraw','drill',target='wall',hands='left',left=['drill'])
 r('drill a hole in the wall','drill','wall','drill',hands='left',left=['drill'])
 r('drill a hole in the wall','drill','wall','drill',hands='left',left=['drill'],note='t=124.66s boundary lies within drilling; t=128s withdraw drill.')
 r('loosen the drill chuck','loosen','drill',left=['drill'],right=['drill'])
 r('replace the drill bit','replace','drill bit',target='drill',left=['drill'],right=['drill bit'],note='t=134.3s put removed bit down; t=134.7s retrieve another bit.')
 r('tighten the drill chuck','tighten','drill',left=['drill'],right=['drill'],note='t=135.4s insert bit then t=136–142s tighten chuck.')
 r('drill a hole in the wall','drill','wall','drill',hands='left',left=['drill'],note='t=143–146s adjust drill controls, then t=147s bring drill to wall.')
 r('drill a hole in the wall','drill','wall','drill',hands='left',left=['drill'],note='t=148.83s cut lies inside ongoing drilling.')
 r('drill a hole in the wall','drill','wall','drill',hands='left',left=['drill'],note='t=153.2s cut lies inside ongoing drilling; withdraw at t=157.2s.')
 r('pick up the wall anchor bag','pick up','wall anchor bag',hands='right',right=['wall anchor bag'],note='t=158–160s put drill down, then t=161s retrieve anchor bag.')
 r('open the wall anchor bag','open','wall anchor bag',left=['wall anchor bag'],right=['wall anchor bag'])
 r('remove wall anchors from the bag','remove','wall anchor',target='wall anchor bag',left=['wall anchor bag'],right=['wall anchor'])
 r('select a wall anchor from the bag','select','wall anchor',left=['wall anchor bag'],right=['wall anchor'])
 r('put down the wall anchor bag','put down','wall anchor bag',target='floor',hands='left',right=['wall anchor'])
 r('bring the wall anchor to the hole','move','wall anchor',target='wall',hands='right',right=['wall anchor'])
 r('press the wall anchor into the hole','press','wall anchor',target='wall',hands='right',right=['drill bit'],note='t=180.5–181s try anchor; t=183s pick up drill bit.')
 r('insert the drill bit into the drill','insert','drill bit',target='drill',left=['drill'],right=['drill'])
 r('remove the drill bit from the drill','remove','drill bit',target='drill',hands='right',left=['drill'],note='t=187.6s remove bit, then t=188.1s put it down.')
 r('insert another drill bit into the drill','insert','drill bit',target='drill',left=['drill'],right=['drill'],note='t=188.7s insert another bit; t=189–193s tighten chuck.')
 r('drill a hole in the wall','drill','wall','drill',hands='left',left=['drill'])
 r('drill a hole in the wall','drill','wall','drill',hands='left',left=['drill'],note='t=201.99s boundary divides continued drilling before withdrawal.')
 r('pick up a wall anchor','pick up','wall anchor',hands='right',right=['wall anchor'],note='t=207s put drill down, t=208s retrieve anchor.')
 r('press the wall anchor into the hole','press','wall anchor',target='wall',hands='right',left=['drill'],note='t=209–211s try anchor; t=212.5s pick up drill.')
 r('replace the drill bit','replace','drill bit',target='drill',left=['drill'],right=['drill bit'],note='t=213–214s remove bit; t=214.6s retrieve another and t=215s insert it.')
 r('pick up another drill bit','pick up','drill bit',hands='right',left=['drill'],right=['drill bit'])
 r('tighten the drill chuck','tighten','drill',left=['drill'],right=['drill'],note='t=216.7s insert drill bit; t=217–225s tighten chuck; t=226s raise drill to wall.')
 r('drill a hole in the wall','drill','wall','drill',hands='left',left=['drill'])
 r('drill a hole in the wall','drill','wall','drill',hands='left',left=['drill'],note='t=231.23s cut lies inside continued drilling; withdraw at t=234.5s.')
 r('pick up a wall anchor','pick up','wall anchor',hands='right',right=['wall anchor'],note='t=235.2s lower drill to floor, t=235.7s pick anchor up.')
 r('press the wall anchor into the hole','press','wall anchor',target='wall',right=['wall anchor'])
 r('press the wall anchor into the hole','press','wall anchor',target='wall',right=['wall anchor'],note='t=242.36s cut divides repeated pressing of the same anchor; t=247–249s lower hands and regrasp.')
 # The small green anchors remain in the wall; they are not held once fingers withdraw.
 r('press the wall anchor with the screwdriver','press','wall anchor','screwdriver','wall',hands='left',left=['screwdriver'],note='t=250–255s finger pressure on anchors, then t=256–261s screwdriver presses anchor; no hammering inferred.')
 r('pick up the curtain hook','pick up','curtain hook',hands='left',left=['curtain hook'],note='t=262s put screwdriver down; t=263.3s pick hook up.')
 r('align the curtain hook with the wall anchors','align','curtain hook',target='wall anchor',left=['curtain hook'],right=['curtain hook'])
 r('press the wall anchor with the screwdriver','press','wall anchor','screwdriver','wall',hands='left',left=['screwdriver'],note='t=267.3s lower hook; t=269–271s press anchor using screwdriver. differs_from_expectation: hook was not attached after alignment; anchor needs more adjustment.')
 r('pick up a screw from the floor','pick up','screw',hands='right',left=['screwdriver'],right=['screw'],note='t=271.7s put screwdriver down, t=272.7s retrieve anchor, t=273.3s try anchor, t=274.3s retrieve screwdriver, t=275.7s retrieve screw.')
 r('hold the curtain hook against the wall','hold','curtain hook',target='wall',left=['curtain hook','screwdriver'],right=['screw'],note='t=278–279s lower drill without use, t=280s pick hook up, t=281s align; left holds hook and screwdriver together.')
 r('insert the screw through the curtain hook','insert','screw',target='curtain hook',hands='right',left=['curtain hook','screwdriver'])
 r('reach for another screw','reach for','screw',hands='right',left=['curtain hook','screwdriver'],note='t=292–295s right hand searches floor while left supports hook; final pickup partly occluded.',amb=True)
 r('insert the screw through the curtain hook','insert','screw',target='curtain hook',hands='right',left=['curtain hook','screwdriver'])
 r('insert the screw through the curtain hook','insert','screw',target='curtain hook',hands='right',left=['curtain hook','screwdriver'],note='t=296–302s right fingers repeatedly turn screw before screwdriver is applied.')
 r('adjust the curtain hook against the wall','adjust','curtain hook',target='wall',left=['screwdriver'],right=['curtain hook'],note='t=304.5s change grip; left moves screwdriver to screw.')
 r('tighten the curtain hook screw','tighten','screw','screwdriver','curtain hook',hands='left',left=['screwdriver'],right=['curtain hook'])
 r('tighten the curtain hook screw','tighten','screw','screwdriver','curtain hook',hands='left',left=['screwdriver'],right=['curtain hook'],note='t=312.65s cut divides ongoing screwdriver turns.')
 r('tighten the curtain hook screw','tighten','screw','screwdriver','curtain hook',hands='left',left=['screwdriver'],right=['curtain hook'],note='t=318.1s cut divides ongoing tightening; fingers regrasp driver but object is unchanged.')
 r('tighten the curtain hook screw','tighten','screw','screwdriver','curtain hook',hands='left',left=['screwdriver'],right=['curtain hook'],note='t=327.01s cut divides continued tightening.')
 r('tighten the curtain hook screw','tighten','screw','screwdriver','curtain hook',hands='left',left=['screwdriver'],note='t=332.09s cut divides tightening; t=332.3–333.3s right hand tests hook, then screwdriver returns to screw.')
 r('check the curtain hook','check','curtain hook',hands='right',left=['screwdriver'])
 r('tighten the curtain hook screw','tighten','screw','screwdriver','curtain hook',hands='left',left=['screwdriver'],note='t=356–357.7s tighten screw; t=358s turn to curtain.')
 r('gather the curtain beside the hook','gather','curtain',left=['curtain'],right=['curtain'])
 r('place the curtain inside the hook','place','curtain',target='curtain hook',hands='right',note='t=362.7–364s arrange curtain inside hook, t=364.3s release; final second has no interaction.')
 r('idle: inspect the held curtain',None,None,hands='unclear',note='t=365.31–365.9s hands absent, same static inspection as adjacent interval.')
 r('adjust the curtain inside the hook','adjust','curtain',target='curtain hook',hands='right',note='t=365.9–367.5s no interaction, t=368.3–368.8s right hand pulls curtain slightly, then withdraws.')
 return save('0573fc312656e95a',[
 'Install a curtain holdback hook',
 'Position a curtain hook beside the window and mark its mounting holes. Drill and widen the holes, fit wall anchors, then fasten the hook with screws and a screwdriver.',
 'The hook is fastened to the wall and holds the gathered curtain beside the window.'],
 [(0,33.56,'Gather curtain and mark an initial hook position.'),(33.56,71.35,'Measure and mark the hook position again.'),(71.35,161.63,'Choose drill bits and drill mounting holes.'),(161.63,261.84,'Fit anchors and repeatedly widen the holes.'),(261.84,305.27,'Align hook and start screws.'),(305.27,359.17,'Tighten screws and check hook.'),(359.17,371.134,'Gather curtain inside hook and inspect.')],
 ['tape measure','floor','curtain','curtain hook','wall','marker','drill','drill bit','drill bit bag','wall anchor','wall anchor bag','screwdriver','screw'],rows,
 [(0,6,'Mark an initial curtain hook position','Gather the curtain, hold the hook against the wall and mark holes.'),(7,13,'Measure and mark the hook position','Measure spacing, reposition the hook and mark its mounting holes.'),(14,32,'Drill mounting holes in the wall','Open the bit bag, select and replace bits, and drill the holes.'),(33,55,'Fit wall anchors into the holes','Retrieve anchors, repeatedly drill wider holes and press anchors into place.'),(56,65,'Position the hook and start its screws','Test the hook, adjust anchors and insert mounting screws.'),(66,72,'Tighten the curtain hook screws','Turn the screws with a screwdriver and check the secured hook.'),(73,76,'Gather the curtain inside the mounted hook','Pull curtain aside, place it in the hook and inspect.')],
 'All 77 original fine boundaries retained. Repeated marking, drilling and screwdriver-turn segments are recorded literally; many boundaries split continuous interaction, with notes for human review. differs_from_expectation: anchor fit requires repeated drill-bit replacement and drilling; no hammer is used. Left hand sometimes holds screwdriver and hook simultaneously; inventory and transition derivation allow lists of held objects. A green anchor fixed in the wall is not still in_hand when fingers withdraw. No inferred bit diameter or fastener specification. Uncovered tail 370.45–371.134s is static inspection, no task interaction visible in overview. Canonical drill bit combines visually similar bits because precise sizes cannot be read.')
