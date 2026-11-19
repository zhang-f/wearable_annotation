from write_editor_batch import *
write('7343f3bdddacab20',dict(title='Make pan-toasted garlic bread',description='Slice a short bread roll into two pieces and set them aside. Crush, slice and repeatedly mince a garlic clove on the board. Put butter in a small bowl, scrape the minced garlic into it and mash and stir the mixture with a spoon. Wipe the board, spread the garlic butter over the cut surfaces of both bread pieces and heat a frying pan on the gas burner. Lay both pieces buttered side down in the pan, wait while adjusting the burner and checking a piece with a spatula, then lift the browned pieces onto a plate and move the pan away.',final_state='Two garlic-buttered bread pieces with browned toasted faces lie on a white plate on the cutting board. No eating is shown.',procedure=['Cut the bread roll into two pieces.','Crush and mince the garlic.','Combine the garlic and butter in a small bowl.','Spread the garlic butter on both bread pieces.','Heat the pan and place the coated bread faces against it.','Toast, check and transfer the browned bread to a plate.']),['bread','knife','garlic','cutting board','butter','spoon','small bowl','butter dish','garlic butter','paper towel','frying pan','burner knob','spatula','plate','drawer'],'''
slice the bread roll into two pieces|cut|bread|knife|cutting board|both|bread|knife
set the two bread pieces aside|place|bread||cutting board|both||knife
crush the garlic beneath the flat knife blade|crush|garlic|knife|cutting board|both|garlic|knife
slice and chop the garlic on the board|chop|garlic|knife|cutting board|both|garlic|knife
gather the garlic pieces with the knife|gather|garlic|knife|cutting board|both|garlic|knife
continue mincing the garlic with the knife|mince|garlic|knife|cutting board|both||knife
put butter into the small bowl with a spoon|scoop|butter|spoon|small bowl|both|small bowl|spoon
cut another butter portion into the bowl|cut|butter|knife|small bowl|both|small bowl|
scrape garlic onto the knife and into the bowl|transfer|garlic|knife|small bowl|both|small bowl|knife
scrape more minced garlic into the butter bowl|transfer|garlic|knife|small bowl|both|small bowl|knife
gather the remaining garlic and scrape it into the bowl|transfer|garlic|knife|small bowl|both|small bowl|spoon
mash and stir the garlic and butter with the spoon|mix|garlic butter|spoon|small bowl|both|small bowl|spoon
put the bowl and spoon beside the plate|put down|small bowl||plate|both||
put down the knife and open the drawer|open|drawer|||right||
tear a paper towel sheet from the roll|tear|paper towel|||both|paper towel|paper towel
wipe the cutting board with the paper towel|wipe|cutting board|paper towel||left||
spread garlic butter across the first bread piece|spread|garlic butter|knife|bread|both|bread|knife
set down the first piece and coat the second|spread|garlic butter|knife|bread|both|bread|knife
smooth garlic butter across the second bread piece|spread|garlic butter|knife|bread|both||knife
put down the coated bread and spreading knife|put down|knife|||right||
move the pan onto the burner and ignite it|heat|frying pan||burner knob|both||
place the first bread piece buttered side down|place|bread||frying pan|left||
place the second bread piece buttered side down|place|bread||frying pan|left||
idle: watch the bread start toasting|||||none||
pick up the spatula and put it beside the pan|move|spatula||cutting board|left||
adjust the burner and wait beside the toasting bread|adjust|burner knob|||right||
set the plate on the board beside the pan|place|plate||cutting board|right||
idle: wait while the bread toasts in the pan|||||none||
lift a bread edge with the spatula to check it|check|bread|spatula|frying pan|both||
adjust the burner and continue waiting|adjust|burner knob|||right||
pick up the spatula beside the plate|pick up|spatula|||left||spatula
lift the first toasted bread piece onto the plate|transfer|bread|spatula|plate|both||spatula
lift the second toasted bread piece onto the plate|transfer|bread|spatula|plate|both||spatula
move the frying pan away from the burner|move|frying pan|||left||spatula
put down the spatula and reposition the finished plate|move|plate||cutting board|both||
''',[(0,1,'Slice and set aside the bread.','Cut the short roll into two pieces and move both to the upper side of the board.','Prepare the bread surfaces that will receive garlic butter.'),(2,5,'Crush and mince the garlic.','Press the garlic under the knife, cut it smaller, gather it and repeatedly mince it.','Prepare small garlic pieces to distribute through the butter.'),(6,11,'Mix the garlic butter.','Put butter portions into the small bowl, scrape in the minced garlic and mash and stir them with a spoon.','Produce the garlic-butter mixture for coating the bread.'),(12,19,'Clean the board and coat both bread pieces.','Set utensils aside, tear a paper towel and wipe the board, then spread garlic butter across the cut face of each piece.','Leave both bread pieces evenly coated for pan toasting.'),(20,29,'Toast the coated bread in the pan.','Move and heat the frying pan, place both pieces coated side down, wait, adjust the burner and lift an edge to check the toasting.','Brown the garlic-buttered faces of the bread.'),(30,34,'Plate the toasted garlic bread.','Use the spatula and a supporting hand to move each browned piece onto the plate, move the pan away and reposition the plate.','Leave two finished toasted bread pieces on the serving plate.')], 'Viewed all 11 overview, 18 dense sheets (1101 frames) and 3 native endpoint sheets. Anchors: bread sliced t=2–9s; garlic crushed t=14s and minced t=17–68s; butter added t=71–77s; garlic scraped into bowl t=79–94s; mixing t=95–128s; bread coated t=144–184s; burner ignited t=189s; bread laid coated face down t=199–202s; underside checked t=278–282s; browned pieces plated t=316–322s. The bread is toasted as two separate pieces rather than closed into a sandwich. Source long intervals include multiple knife/spoon pickups and hand-object changes, retained without changing boundaries.',fix={6:dict(boundary_note='Interval includes bowl retrieval, spoon pickup and transfer of the first butter portion.'),7:dict(boundary_note='Spoon-to-knife change and cutting butter are both inside this interval.'),10:dict(boundary_note='Garlic scraping finishes, knife is set down and spoon is picked up near 93s.'),13:dict(boundary_note='Knife release and opening the utensil drawer both occur inside the interval.'),16:dict(boundary_note='Paper towel and spoon are released, then bread and knife are picked up before spreading.'),17:dict(boundary_note='First bread is set down, more mixture retrieved and the second bread picked up.'),20:dict(boundary_note='This segment combines moving the pan, igniting/adjusting the burner and briefly holding a hand above the pan.'),25:dict(boundary_note='Interval contains waiting, paper-towel hand wiping near 217s and burner adjustments near 225s.'),28:dict(boundary_note='Spatula pickup, lifting/checking a bread edge and spatula release occur within this interval.'),30:dict(ambiguous=True,confidence='medium',notes='Spatula changes hands before the lifting action; right hand holds it at the endpoint.')},evidence_manifest=str(OUT/'frames_v2/7343f3bdddacab20/20261106T060106772972Z/manifest.json'))
