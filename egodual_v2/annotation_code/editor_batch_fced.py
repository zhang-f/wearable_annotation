from write_editor_batch import *
v='fced96b0f5b0dbf1'
goal=dict(title='Make a microwave tortilla pizza with cheese and olives',description='Set a tortilla on a plate, spread red sauce over it, add cheese strips and black olive pieces, microwave the topped tortilla, then move it to a cutting board, cut into quarters and return pieces to the plate.',final_state='Four small pizza quarters are arranged on the green plate.',procedure=['Place tortilla on plate and open sauce jar.','Spoon sauce onto tortilla and spread it evenly.','Scatter cheese strips and black olive pieces across sauce.','Microwave the topped tortilla, retrieve the hot plate using a pot holder and let it rest.','Transfer pizza from plate to cutting board, cut it into quarters and arrange pieces back on plate.'])
inv=['tortilla','green plate','sauce jar','jar lid','spoon','red sauce','cheese','cheese container','olive container','container lid','black olives','pizza','microwave','microwave keypad','pot holder','cutting board','knife']
lines='''both hands center tortilla on the green plate|center|tortilla||green plate|both||
right hand takes spoon while left reaches sauce jar|take|spoon||sauce jar|both||spoon
left hand removes sauce jar lid|remove|jar lid||sauce jar|left|jar lid|spoon
left hand sets lid down then lifts sauce jar|lift|sauce jar|||left|sauce jar|spoon
right hand spoons sauce from jar onto tortilla|spoon|red sauce|spoon|tortilla|both|sauce jar|spoon
right hand adds another spoonful of sauce to tortilla|spoon|red sauce|spoon|tortilla|both|sauce jar|spoon
right hand scrapes spoon at jar mouth while left lowers jar|scrape|spoon||sauce jar|both|sauce jar|spoon
right hand spreads sauce across tortilla using spoon|spread|red sauce|spoon|tortilla|right||spoon
right hand lifts spoon toward cutting board|lift|spoon||cutting board|right||spoon
right hand sets spoon down and takes cheese|take|cheese||cheese container|right||cheese
both hands break apart and scatter cheese over tortilla|scatter|cheese||tortilla|both||cheese
right hand takes more cheese from container|take|cheese||cheese container|right||cheese
right hand scatters remaining cheese across tortilla|scatter|cheese||tortilla|right||
both hands open the olive container|open|olive container||container lid|both||container lid
right hand picks olives from the open container|pick up|black olives||olive container|right||black olives
right hand scatters olive pieces over cheese|scatter|black olives||pizza|right||black olives
right hand takes another pinch of olives|take|black olives||olive container|right||black olives
right hand distributes olives across the pizza|distribute|black olives||pizza|right||
both hands grip plate holding the topped tortilla|grip|green plate||pizza|both|green plate|green plate
right hand carries plate while left reaches microwave controls|carry|green plate||microwave|both||green plate
left hand opens microwave while right holds plate|open|microwave|||both||green plate
right hand places pizza plate inside microwave|place|green plate||microwave|right||
right hand closes microwave door|close|microwave|||right||
right hand presses microwave keypad to start heating|press|microwave keypad||microwave|right||
idle (waiting for pizza heating, briefly handling pot holder)|||||none||pot holder
left hand opens microwave while right holds pot holder|open|microwave|||both||pot holder
right hand lifts hot pizza plate using pot holder|lift|green plate|pot holder|microwave|right||green plate;pot holder
left hand closes microwave while right holds hot plate|close|microwave|||both||green plate;pot holder
right hand carries hot pizza plate back to counter|carry|green plate|pot holder||right||green plate;pot holder
left hand touches pizza while right sets down hot plate|touch|pizza||green plate|both||pot holder
left hand moves cutting board while right holds pot holder|move|cutting board|||both||pot holder
both hands lift cutting board toward front of counter|lift|cutting board|||both|cutting board|cutting board
both hands place cutting board beside pizza plate|place|cutting board|||both||
right hand picks up sauce jar lid|pick up|jar lid||sauce jar|right||jar lid
both hands twist lid onto sauce jar|twist|jar lid||sauce jar|both||
both hands place lid on olive container|close|olive container||container lid|both||
left hand presses olive container lid closed|press|container lid||olive container|left||
idle (waiting beside the pizza before cutting)|||||none||
both hands pick up and unfold pot holder|unfold|pot holder|||both|pot holder|pot holder
left hand holds pot holder while right touches plate rim|touch|green plate|pot holder||both|pot holder|
right hand loosens pizza edge while left steadies hot plate|loosen|pizza|pot holder|green plate|both|pot holder|pizza
right hand slides pizza from plate onto cutting board|slide|pizza|pot holder|cutting board|both|pot holder|
right hand moves empty plate above cutting board|move|green plate||cutting board|right||
right hand picks up knife beside cutting board|pick up|knife||cutting board|right||knife
right hand cuts pizza while left steadies cutting board|cut|pizza|knife|cutting board|both||knife
right hand turns cutting board and cuts pizza again|cut|pizza|knife|cutting board|both||knife
right hand sets knife beside cutting board|set down|knife||cutting board|right||
both hands separate pizza quarters and lift two pieces|separate|pizza||cutting board|both|pizza|pizza
both hands place pizza pieces onto green plate|place|pizza||green plate|both||
both hands pick up another pizza quarter|pick up|pizza||cutting board|both|pizza|pizza
both hands place pizza quarter on plate|place|pizza||green plate|both||
both hands lift the final pizza piece from board|lift|pizza||cutting board|both|pizza|pizza
both hands place final pizza piece on plate|place|pizza||green plate|both||
right hand gathers loose topping from cutting board|gather|black olives||cutting board|right||black olives
right hand moves plate while left shifts cutting board|move|green plate||cutting board|both|cutting board|green plate
right hand places plate beside cutting board|place|green plate||cutting board|right||
idle (hands withdraw from the plated pizza quarters)|||||none||'''
groups=[(0,8,'Place tortilla on a plate and spread sauce.','The tortilla is centered, the sauce jar opened and several spoonfuls spread over its surface with the back of the spoon.','Create the sauced pizza base.'),(9,12,'Cover the sauced tortilla with cheese.','Cheese strips are taken from the small container, separated and scattered across the tortilla.','Add the cheese topping before heating.'),(13,18,'Add black olive pieces.','The olive container is opened, pieces pinched and spread over the cheese, and the plate gripped for carrying.','Complete the visible pizza toppings.'),(19,24,'Put the pizza in the microwave and heat it.','The plate is carried to the microwave, inserted, the door closed and heating started; the wearer waits and readies a pot holder.','Heat the topped tortilla and melt the cheese.'),(25,32,'Retrieve the hot pizza and set out a cutting board.','The hot plate is removed with a pot holder, carried back to the counter and set down; the cutting board is brought forward.','Make the heated pizza accessible for cutting.'),(33,37,'Close ingredient containers and let the pizza rest.','The sauce jar lid is screwed back on and olive container closed, followed by a wait beside the pizza.','Clear loose ingredients while the hot pizza rests.'),(38,46,'Move pizza to board and cut into quarters.','A pot holder steadies the plate while pizza is loosened and slid to the cutting board; a knife cuts it in crossing directions.','Divide the heated pizza into serving pieces.'),(47,56,'Return the pizza quarters to the plate.','Hands separate quarters and place them on the green plate, collect loose topping and move the plate beside the cutting board.','Leave the prepared pizza pieces ready to serve.')]
fix={24:dict(boundary_note='Long preserved interval mostly waiting at 66.43–111.8s; pot holder is briefly handled near 103–104s and held by the end.',confidence='medium'),37:dict(boundary_note='Mostly waiting at 135.12–149.68s; brief hand withdrawal after closing containers occurs at the start.'),45:dict(boundary_note='Includes rotating the cutting board near 166–167s followed by a second knife cut through 170s.'),53:dict(confidence='medium',notes='Small dark topping gathered from board; exact piece is difficult to distinguish. Canonical black olives used from visible topping set.')}
write(v,goal,inv,lines,groups,'Every overview, dense 3/15fps step frame and native endpoint sheet inspected. Original fine boundaries retained. Source objects named from visible round thin flatbread, sauce, pale cheese strips and recognizable sliced black olives. Short leftover tail under 0.3s does not show a new action.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T095943238138Z/manifest.json'))
