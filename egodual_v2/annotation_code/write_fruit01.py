from batch01_builder import *
v='35b4bd14afb42109';B='banana';K='kiwi';S='strawberry';N='knife';P='plate';W='wooden skewer';F='faucet';BP='banana peel'
r=[
row('hold the banana above the sink','hold',B,hands='left',left=[B],right=[S]),
row('rinse the banana and strawberries under the faucet','rinse',B,target=F,left=[B],note='t=0.4–1.8s operate faucet, t=2.1–3.8s rinse fruit, then set strawberries on plate at 4.3–5.3s; compound interval retained.'),
row('turn off the faucet','turn',F,hands='right',left=[B]),
row('grip the banana stem with both hands','grip',B,left=[B],right=[B],note='t=6.8–7.4s arrange strawberries before gripping banana stem.'),
row('pull down the banana peel','peel',B,left=[B],right=[BP]),
row('adjust the grip on the banana','grip',B,left=[B],right=[B]),
row('pull another strip of banana peel down','peel',B,left=[B],right=[N],note='t=14.47s right hand retrieves knife after pulling peel.'),
row('cut the banana skin with the knife','cut',B,tool=N,hands='right',left=[B],right=[N]),
row('pull the banana peel down by hand','peel',B,left=[B],right=[B]),
row('remove the banana peel and set the banana down','peel',B,target=P,left=[BP],note='t=18.1–21.5s remove peel; t=22.1–23.1s place exposed banana on plate.'),
row('set the banana peel aside and pick up the kiwi','pick up',K,left=[K],note='t=23.6s right hand retrieves kiwi; t=24.1–24.8s left hand lowers peel; kiwi transfers to left.'),
row('pare the kiwi skin with the knife','peel',K,tool=N,hands='right',left=[K],right=[N]),
row('pare another strip of kiwi skin','peel',K,tool=N,hands='right',left=[K],right=[N]),
row('shave the remaining kiwi skin','peel',K,tool=N,hands='right',left=[K],right=[N]),
row('trim small patches of kiwi skin','peel',K,tool=N,hands='right',left=[K],right=[N]),
row('set the peeled kiwi on the plate','place',K,target=P,left=[K],right=[N],note='t=58.1s final skin trimming precedes placing kiwi at 58.6s; then align knife.'),
row('slice the kiwi on the plate','slice',K,tool=N,hands='right',right=[N]),
row('slice the banana into chunks','slice',B,tool=N,hands='right',right=[N],note='t=68.9s lift and reposition banana before cutting at 70–75s.'),
row('reposition the banana beside the kiwi slices','move',B,hands='left',right=[N]),
row('cut more banana chunks','slice',B,tool=N,hands='right',left=[B],right=[N]),
row('slice the remaining banana','slice',B,tool=N,hands='right',right=[N]),
row('finish slicing the banana and reach for a strawberry','slice',B,tool=N,hands='right',right=[N],note='t=86.2–88.1s finish cuts; t=88.3–89.1s left hand reaches for strawberries.'),
row('cut the leafy top off a strawberry','cut',S,tool=N,hands='right',right=[N]),
row('cut the leafy top off another strawberry','cut',S,tool=N,hands='right',left=[S],right=[N]),
row('trim the top off the third strawberry','cut',S,tool=N,hands='right',left=[S],right=[N]),
row('halve a hulled strawberry','cut',S,tool=N,hands='right',left=[S],right=[N]),
row('halve another hulled strawberry','cut',S,tool=N,hands='right',left=[S],right=[N]),
row('cut the remaining strawberry in half','cut',S,tool=N,hands='right',right=[N]),
row('rearrange the fruit pieces on the plate','move',B,hands='left',right=[N]),
row('thread a banana chunk onto the wooden skewer','thread',B,tool=W,left=[B],right=[W],note='t=116.1s set knife aside; t=117.8–121.2s retrieve skewer and pierce banana.'),
row('thread a strawberry half onto the skewer','thread',S,tool=W,left=[S],right=[W]),
row('thread a kiwi slice onto the skewer','thread',K,tool=W,right=[W]),
row('thread another banana chunk onto the skewer','thread',B,tool=W,left=[B],right=[W]),
row('thread another strawberry half onto the skewer','thread',S,tool=W,right=[W]),
row('thread another banana piece onto the skewer','thread',B,tool=W,left=[B],right=[W]),
row('thread another kiwi slice onto the skewer','thread',K,tool=W,right=[W]),
row('thread a strawberry half onto the fruit skewer','thread',S,tool=W,left=[S],right=[W]),
row('thread banana onto the skewer and set it aside','thread',B,tool=W,hands='both',note='t=153.5–161.8s select and push banana onto skewer; t=162.1–164s place completed skewer at counter right.'),
row('thread a banana chunk onto a second skewer','thread',B,tool=W,left=[B],right=[W])]
proc=[(0,6.6,'Carry a banana and strawberries over the sink, operate the faucet and hold the fruit under running water. Put the strawberries on the amber plate and turn the faucet off.'),(6.6,25,'Snap and pull the banana skin downward, briefly use the knife on the skin, then pull away the remaining peel. Put the peeled banana on the plate and move the peel aside while retrieving a kiwi.'),(25,60.72,'Hold and rotate the kiwi while paring away long strips of brown skin with the knife. Repeatedly shave the remaining patches, then lower the peeled fruit to the plate.'),(60.72,89.15,'Slice the kiwi into thick green rounds. Reposition the banana, crosscut it into chunks and rearrange pieces as cutting progresses.'),(89.15,115.62,'Pick up the strawberries individually, cut off their leafy tops and move the caps aside. Halve the hulled berries and rearrange the prepared fruit on the plate.'),(115.62,164.22,'Set the knife aside and retrieve a long wooden skewer. Alternately pierce banana chunks, strawberry halves and kiwi slices, sliding each down the stick. Finish loading the first skewer and place it to the right of the plate.'),(164.22,169.6,'Retrieve another skewer and pierce a banana chunk, beginning the second fruit skewer. The supplied human fine divisions stop during this operation.'),(169.6,205,'In the uncovered tail, slide the banana down the second stick, add kiwi, strawberry, more banana and further fruit pieces, and lay this second loaded skewer on the plate.'),(205,218.4,'Retrieve the first skewer from the right, add a remaining banana piece, then lay both loaded fruit skewers side by side on the plate and adjust their arrangement.')]
groups=[(0,10,'Rinse the fruit and peel the banana','Rinse banana and strawberries, put berries on the plate, stop the water, peel the banana by hand with brief knife assistance, set it down and move the peel aside while retrieving kiwi.','Cleans the fruit and exposes the banana flesh for cutting.'),(11,15,'Peel the kiwi','Rotate the kiwi while paring long skin strips and shaving remaining patches, then place the peeled fruit on the plate.','Removes the kiwi skin before slicing it into skewer pieces.'),(16,28,'Cut the fruit into skewer pieces','Slice the kiwi and banana, reposition pieces, trim all three strawberry tops, halve the berries and rearrange the cut fruit.','Produces the separate fruit pieces that will be threaded onto sticks.'),(29,37,'Assemble and set aside the first fruit skewer','Retrieve a skewer after setting down the knife, alternately thread banana, strawberry and kiwi pieces, finish loading it and place it on the right side.','Combines prepared fruit into the first assembled serving.'),(38,38,'Begin the second fruit skewer','Pick up a second wooden skewer and push a banana chunk onto it; coverage stops before the next fruit is added.','Starts the second serving, whose continuation is visible in the uncovered tail.')]
d=finish(v,['Make banana kiwi and strawberry skewers','Rinse and prepare banana, kiwi and strawberries, cut the fruit into chunks and slices, and alternate the pieces on two long wooden skewers.','Two loaded fruit skewers lie side by side on the amber plate at the end of the video.'],proc,[B,K,S,N,P,W,F,BP,'kiwi peel','strawberry top'],r,groups,'All 39 human fine boundaries preserved. True duration 218.4s but fine stops at 169.6s: the 48.8s tail contains continued assembly of the second skewer, placement, adding one remaining banana piece to the first skewer and presentation of two skewers. Tail is described in goal.procedure but no invented fine interval is appended. All dense step pages, native end states, overview and 3fps tail reviewed. Coarse final partial subtask necessarily ends at last human fine boundary; it does not imply task completion at 169.6s.')
d['annotation_provenance']['evidence_directory']='frames_v2/35b4bd14afb42109/20261106T225132533455Z'
(OUT/'videos'/f'{v}.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(v,len(r),'validated')
