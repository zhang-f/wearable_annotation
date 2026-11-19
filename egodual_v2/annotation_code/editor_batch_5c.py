from write_editor_batch import *
write('5c73bd7058462eed',dict(title='Prepare seasoned avocado cups with mashed avocado filling',description='Cut an avocado around the pit, twist the halves apart and remove the pit with the knife. Scoop the flesh into a bowl while keeping the skins as cups. Season the hollowed halves, clean a small floor spill, place the cups on a plate and mash the avocado with a fork. Spoon the mash back into the cups, smooth it and add more seasoning.',final_state='Two avocado skins on a plate hold mashed avocado topped with visible seasoning.',procedure=['Cut the avocado and separate its halves.','Remove the pit and scoop the flesh into a bowl.','Season the hollowed avocado cups and wipe the floor spill.','Arrange the cups on a plate and mash the flesh with a fork.','Fill the cups with the mashed avocado, smooth and season the filling.']),['avocado','avocado pit','knife','bowl','spoon','fork','seasoning bottle','plate','drawer','paper towel','floor','trash bin','counter','sweater'],'''
pick up the avocado|pick up|avocado|||left|avocado|knife
cut around the avocado pit|cut|avocado|knife||both|avocado|knife
put the knife on the counter|put down|knife||counter|right|avocado|
twist the avocado halves apart|twist|avocado|||both|avocado|avocado
set one avocado half on the counter|put down|avocado||counter|right|avocado|
pick up the knife|pick up|knife|||right|avocado|knife
tap the knife against the avocado pit|tap|avocado pit|knife|avocado|right|avocado|knife
tap the knife blade into the avocado pit|tap|avocado pit|knife|avocado|right|avocado|knife
twist the pit out with the knife|remove|avocado pit|knife|avocado|both|avocado|knife
set the avocado half down|put down|avocado||counter|left||knife
scrape the pit off the knife over the bin|remove|avocado pit|knife|trash bin|right||knife
put the knife down and open the drawer|open|drawer|||left|drawer|
take a spoon from the drawer|pick up|spoon|||left|spoon|
pick up an avocado half|pick up|avocado|||left|avocado|spoon
scoop avocado flesh into the bowl|scoop|avocado|spoon|bowl|both|avocado|spoon
idle: put down utensils and fetch a sweater|||||both|sweater|sweater
idle: put on the sweater|||||both||
pick up the avocado half and spoon|pick up|avocado|spoon||both|avocado|spoon
scoop avocado flesh out of the skin|scoop|avocado|spoon|bowl|both|avocado|spoon
scrape the spoon into the bowl|scrape|avocado|spoon|bowl|right|avocado|spoon
scoop flesh from the other avocado half|scoop|avocado|spoon|bowl|both|avocado|spoon
put the hollowed avocado cup down|put down|avocado||counter|left||spoon
reach toward the seasoning rack|reach|seasoning bottle|||right||seasoning bottle
take and open the seasoning bottle|open|seasoning bottle|||both|seasoning bottle|
pick up an avocado cup|pick up|avocado|||left|avocado|seasoning bottle
shake seasoning into the avocado cup|shake|seasoning bottle||avocado|right|avocado|seasoning bottle
put the seasoned avocado cup down|put down|avocado||counter|left||seasoning bottle
pick up the other avocado cup|pick up|avocado|||left|avocado|seasoning bottle
shake seasoning into the other cup|shake|seasoning bottle||avocado|right|avocado|seasoning bottle
exchange the avocado cups on the counter|pick up|avocado|||left|avocado|seasoning bottle
shake more seasoning into the avocado cup|shake|seasoning bottle||avocado|right|avocado|seasoning bottle
put the avocado cup down|put down|avocado||counter|left||seasoning bottle
close and put down the seasoning bottle|close|seasoning bottle||counter|both||
tear off a paper towel|tear|paper towel|||both|paper towel|paper towel
wipe the floor with the paper towel|wipe|floor|paper towel||right||paper towel
carry the paper towel to the bin|move|paper towel||trash bin|right||paper towel
discard the paper towel|discard|paper towel||trash bin|right||
take a plate from the cabinet|pick up|plate|||left|plate|
put the plate on the counter|put down|plate||counter|left|plate|avocado
place one avocado cup on the plate|place|avocado||plate|right|plate|avocado
place the other avocado cup on the plate|place|avocado||plate|both||
arrange the avocado cups and open the drawer|open|drawer|||left|drawer|
take a fork from the drawer|pick up|fork|||left|fork|
pick up the spoon beside the bowl|pick up|spoon|||left|spoon|fork
put the spoon beside the sink|put down|spoon|||left|bowl|fork
mash the avocado in the bowl with the fork|mash|avocado|fork|bowl|both|bowl|fork
put the fork down beside the sink|put down|fork|||right||
pick up the spoon|pick up|spoon|||right||spoon
scoop mashed avocado from the bowl|scoop|avocado|spoon|bowl|both|bowl|spoon
spoon mashed avocado into an avocado cup|fill|avocado|spoon|avocado|both|avocado|spoon
smooth the filling in the avocado cup|smooth|avocado|spoon||right|plate|spoon
scoop more mashed avocado from the bowl|scoop|avocado|spoon|bowl|both|bowl|spoon
scrape the remaining avocado into the cup|scrape|avocado|spoon|avocado|both|bowl|spoon
put the emptied bowl aside|put down|bowl||counter|left||spoon
pick up the filled avocado cup|pick up|avocado|||left|avocado|spoon
smooth the avocado filling with the spoon|smooth|avocado|spoon||both|avocado|spoon
pick up the seasoning bottle|pick up|seasoning bottle|||left|seasoning bottle|
open the seasoning bottle cap|open|seasoning bottle|||both|seasoning bottle|seasoning bottle
shake seasoning over one filled avocado cup|shake|seasoning bottle||avocado|right||seasoning bottle
shake seasoning over the other filled cup|shake|seasoning bottle||avocado|right||seasoning bottle
close the seasoning bottle|close|seasoning bottle|||both|seasoning bottle|seasoning bottle
put the seasoning bottle aside|put down|seasoning bottle||counter|right||
idle: no interaction with the plated avocado cups|||||unclear||
idle: no interaction while looking at the finished dish|||||unclear||
''',[(0,12,'Halve and pit the avocado','Cut around the avocado, separate its halves and use the knife to remove and discard the pit. Put the knife down and take a spoon.','Prepare the avocado halves for removing their flesh.'),(13,21,'Hollow the avocado cups','Scoop the flesh into the bowl, pause to put on a sweater, then finish scooping both halves. Set the hollowed skins aside.','Retain two skins as cups and collect the flesh for the filling.'),(22,32,'Season the avocado cups','Retrieve the seasoning bottle and shake seasoning into each hollowed half, revisiting the first cup before closing the bottle.','Add seasoning to the surfaces that will hold the filling.'),(33,36,'Clean the floor spill','Take a paper towel, wipe the floor beside the counter and discard the towel.','Clear the visible spill before continuing food preparation.'),(37,46,'Plate the cups and mash the filling','Fetch a plate, arrange both skins on it and obtain a fork. Put the spoon aside and mash the avocado flesh in the bowl.','Produce mashed filling and position the cups for filling.'),(47,63,'Fill and finish the avocado cups','Use the spoon to transfer the mash into the skins, scrape out the bowl and smooth the filling. Shake more seasoning over both cups and put the bottle down.','Leave two filled, seasoned avocado cups on the plate.')], 'Reviewed all 7 overview sheets, all 15 compact dense pages (941 frames) and all 4 native endpoint sheets. Actual t=44.8–58.9s sweater dressing is unrelated idle. t=141.8–163.4s shows continuous mashing; t=170–195s the mash is spooned back into preserved avocado skins, rather than discarded. No additional unseen ingredients inferred.',fix={4:{'boundary_note':'t=12.5–13.75s sets one half down and starts reaching for the knife.'},11:{'boundary_note':'t=23.7–26.6s knife put down then drawer opened; multiple object changes.'},12:{'boundary_note':'Spoon transferred between hands before t=30.3s; endpoint grip partly occluded.','confidence':'medium'},14:{'boundary_note':'t=30–40s repeated scoops from skin to bowl; no separate object change encoded for each scoop.'},15:{'boundary_note':'t=40–42s utensil/half put down; t=42–44.8s fetches unrelated sweater.'},16:{'notes':'Clothing adjustment, not food preparation.'},19:{'boundary_note':'t=69.5–74.3s spoon scraped into bowl then other avocado half taken.'},21:{'confidence':'medium'},22:{'boundary_note':'t=85–88.6s turns to rack and reaches for bottle.'},23:{'boundary_note':'Bottle retrieved and flip cap opened within one segment.'},29:{'boundary_note':'t=103.9–105.5s exchanges avocado halves; more than one pickup/release.'},32:{'boundary_note':'Cap closes and bottle released by t=110.3s.'},33:{'confidence':'medium'},37:{'confidence':'medium','boundary_note':'t=122.8–126.1s opens cabinet and retrieves plate.'},40:{'confidence':'medium','notes':'Halves rest on plate at endpoint; contact is not counted as holding.'},41:{'boundary_note':'Arranges skins before reaching into drawer at t=133s.'},44:{'boundary_note':'t=137–141.8s spoon put aside then fork brought to bowl.'},45:{'notes':'Repeated mashing strokes throughout interval; same bowl/fork interaction.'},49:{'boundary_note':'t=170.5–176.5s filling transferred repeatedly between bowl and avocado cup.'},50:{'confidence':'medium'},55:{'boundary_note':'Smooths cup filling then lowers spoon into bowl near t=194.4s.'},57:{'confidence':'medium'},62:{'notes':'Finished cups remain on plate; no hand-object interaction.'},63:{'notes':'Final view of prepared cups.'}},evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/5c73bd7058462eed/20261106T055052293911Z/manifest.json')
