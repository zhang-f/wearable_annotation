from write_editor_batch import *
v='b4bac0ea2c14e92a'
goal=dict(title='Make a white yarn tassel on a pencil',description='Pull and cut a length of white yarn, form loops around fingers while holding a pink pencil, gather and tie the loops into a tassel, then cut and trim the dangling yarn. The original fine track covers only the first portion of the craft.',final_state='In the full video a trimmed white tassel hangs from the pink pencil; at the last annotated boundary trimming is still in progress.',procedure=['Pull out white yarn, cut a length and prepare a loop.','Position the yarn on the pink pencil and wrap multiple loops around left fingers.','Slide loops together, tie and tighten the yarn around the bundle.','Cut loop ends and trim the fringe, repeatedly checking the hanging tassel.'])
inv=['white yarn','yarn ball','scissors','pink pencil','yarn bundle','yarn tassel']
summaries=[
'both hands pull white yarn taut across the lap',
'right hand reaches for scissors while left holds yarn',
'right hand cuts yarn held by left hand',
'right hand sets scissors beside the yarn ball',
'both hands draw out and separate the cut yarn strand',
'both hands fold and pinch a loop in the yarn',
'both hands pull yarn ends then take the pink pencil',
'both hands loop white yarn around the pink pencil',
'right hand winds yarn around left fingers beside pencil',
'right hand pulls yarn down while left holds pencil',
'right hand brings yarn around left fingers',
'right hand draws yarn across the left palm',
'right hand pulls yarn upwards beside left-held pencil',
'right hand wraps another yarn loop around left fingers',
'right hand guides yarn down across left fingers',
'right hand wraps yarn around the growing finger loops',
'right hand pulls yarn down beside the pencil',
'right hand carries yarn over the left fingers',
'right hand guides yarn over the finger loops',
'right hand pulls yarn across the left palm',
'right hand wraps yarn beneath left fingers',
'both hands pinch the yarn loops around the pencil',
'right hand gathers loops while left holds pencil',
'both hands slide yarn loops off left fingers',
'right hand draws yarn around the gathered loop bundle',
'both hands pinch the gathered yarn beneath pencil',
'right hand tugs a yarn strand through the bundle',
'right hand pulls a yarn end from the loop bundle',
'right hand draws a loose yarn end downward',
'right hand holds the loose yarn end beside bundle',
'right hand pulls yarn taut while left steadies bundle',
'both hands pull apart yarn ends around the bundle',
'both hands tighten yarn beneath the pink pencil',
'right hand threads a yarn end around the bundle',
'right hand pinches and draws yarn through a loop',
'both hands tug yarn around the gathered bundle',
'right hand pulls a yarn end beside the pencil',
'right hand guides yarn through the gathered loops',
'right hand pinches the yarn tie beneath pencil',
'right hand pulls yarn end while left holds bundle',
'both hands tighten the yarn tie beside pencil',
'right hand threads yarn around the bundle neck',
'right hand pulls yarn strand down from the bundle',
'right hand tucks yarn into the bundle tie',
'both hands pull yarn ends against the bundle',
'right hand pulls yarn to tighten the tie',
'right hand repositions yarn end beside bundle neck',
'right hand works yarn around the gathered loops',
'right hand draws the yarn end through the tie',
'both hands pinch and tighten the gathered yarn',
'right hand pulls yarn downward from left-held bundle',
'right hand draws yarn across the bundle neck',
'both hands adjust yarn tie beside the pencil',
'right hand tugs yarn end against the bundle',
'both hands tighten yarn wrapped around bundle neck',
'right hand pulls loose strand beneath the pencil',
'right hand tightens yarn tie while left holds bundle',
'right hand tugs yarn then lifts pencil and bundle',
'both hands rotate pencil and gathered yarn bundle',
'right hand arranges yarn loops beneath the pencil',
'both hands turn and flatten the yarn bundle',
'right hand pulls loose yarn end away from bundle',
'left hand holds bundle while right briefly withdraws',
'both hands pinch the yarn tie around pencil',
'right hand tightens yarn near bundle neck',
'right hand tugs a strand from the bundle',
'right hand separates hanging yarn loops beneath pencil',
'left hand holds pencil and loop bundle over lap',
'right hand reaches for scissors while left holds bundle',
'right hand brings scissors toward the yarn loops',
'right hand positions scissors around looped yarn ends',
'right hand cuts through the yarn loops',
'right hand holds scissors at the yarn fringe',
'right hand opens scissors beside the yarn ends',
'right hand snips yarn ends held by left hand',
'left hand rotates yarn tassel while right holds scissors',
'right hand trims the rotated yarn fringe',
'right hand continues trimming yarn tassel ends']
assert len(summaries)==78,len(summaries)
rows=[]
for i,s in enumerate(summaries):
 if i==0:r=[s,'pull','white yarn','','','both','white yarn','white yarn']
 elif i==1:r=[s,'reach','scissors','','white yarn','both','white yarn','scissors']
 elif i==2:r=[s,'cut','white yarn','scissors','','both','white yarn','scissors']
 elif i==3:r=[s,'set down','scissors','','yarn ball','right','white yarn','']
 elif i<6:r=[s,'fold' if i==5 else 'separate','white yarn','','','both','white yarn','white yarn']
 elif i==6:r=[s,'take','pink pencil','','white yarn','both','pink pencil;white yarn','white yarn']
 elif i<=20:r=[s,'wrap' if i not in [9,12,16,19,20] else 'pull','white yarn','','pink pencil','both','pink pencil;white yarn','white yarn']
 elif i<=67:r=[s,'tighten' if i in [30,31,32,35,39,40,44,45,49,50,54,56,57,60,61,64,65] else 'adjust','yarn bundle','','pink pencil','both','pink pencil;yarn bundle','white yarn' if i not in [62,67] else '']
 elif i<=70:r=[s,'reach' if i==68 else 'position','scissors','','yarn bundle','both','pink pencil;yarn bundle','scissors']
 else:r=[s,'rotate' if i==75 else 'trim','yarn tassel','scissors','','both','pink pencil;yarn tassel','scissors']
 rows.append('|'.join(r))
groups=[(0,6,'Cut and prepare a length of yarn.','Yarn is pulled from the ball, cut with scissors, folded and pinched into a loop before the pink pencil is picked up.','Prepare the strand and support used to make the tassel.'),(7,20,'Wrap loops of yarn around the fingers beside the pencil.','The pencil is held horizontally while repeated passes of white yarn form a bundle around the left fingers.','Build multiple similarly sized loops that will become the fringe.'),(21,32,'Gather the loops and tighten the yarn bundle.','Hands pinch the loops, remove them from the fingers and pull yarn around the gathered bundle near the pencil.','Secure the loop bundle together around its top.'),(33,67,'Work and tighten the yarn tie around the bundle neck.','The short preserved segments show repeated threading, pulling, pinching and tightening of yarn, then rotating the pencil and spreading the hanging loops.','Hold the loop bundle firmly in the tassel shape.'),(68,77,'Begin cutting and trimming the tassel fringe.','Scissors are picked up, positioned around loops and used to snip yarn ends while the left hand rotates the bundle. Trimming continues beyond the source fine track.','Open loop ends and begin shaping the fringe; this source coverage ends before finishing.')]
fix={6:dict(boundary_note='Includes manipulating yarn, reaching for pencil near 19–20s and taking it; preserved interval retained.'),18:dict(confidence='medium',notes='0.1s preserved interval is part of the same visible yarn winding motion.'),29:dict(confidence='medium',notes='0.1s preserved interval shows holding/pulling the same yarn end.'),67:dict(confidence='medium',notes='0.1s preserved hold interval.'),69:dict(confidence='medium',notes='0.1s preserved scissors positioning interval.'),72:dict(confidence='medium',notes='0.1s preserved scissors hold interval.'),73:dict(confidence='medium',notes='0.1s preserved scissors adjustment interval.'),77:dict(boundary_note='Fine track ends at 98.6s although the 183.4s video continues trimming, inspecting and adjusting the tassel. Missing tail requires new human boundaries, not extension by inference.')}
write(v,goal,inv,'\n'.join(rows),groups,'Complete overview including unannotated tail inspected, plus every 794 dense frame and native step endpoint. All fine boundaries retained. CRITICAL COVERAGE GAP: original fine ends at 98.6s, real duration183.4s. Tail includes trimming around100–117s, display119–126s, further trimming130–142s and153–162s, displaying and adjusting tassel through181s. These task actions need new human-approved fine boundaries. Coarse deliberately covers only provided fine, not invented tail. Fine intervals within33–88s subdivide repeated tie manipulation; summaries describe visible fingers/yarn motion without asserting exact knot types.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T224745248348Z/manifest.json'))
