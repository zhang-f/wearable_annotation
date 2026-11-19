from write_editor_batch import *
v='b7a97c9f635d686c'
goal=dict(title='Finger-paint small orange flowers on paper',description='Prepare orange, green and brown paint in separate dishes, dilute it with a brush, then use fingertips to stamp orange petal clusters, brown centers and green leaf marks on textured paper. Clean fingertips and a paint dish while adding final green marks.',final_state='The paper carries several orange flowers with brown centers and green leaves; the brown paint dish is mostly wiped clean.',procedure=['Place paper and dispense orange paint onto a plastic palette.','Wet a brush and test the paint, then wipe the palette and set out three small dishes.','Dispense orange, green and brown paints into separate dishes and mix each with water.','Dip fingertips into orange paint and stamp petal clusters across the paper.','Add brown flower centers and green leaf marks with fingertips, wiping fingers between colors.','Wipe out the brown paint dish and add finishing green marks to the picture.'])
inv=['paper','plastic palette','orange paint tube','green paint tube','brown paint tube','paint cap','orange paint','green paint','brown paint','paintbrush','water tray','tissue','orange paint dish','green paint dish','brown paint dish']
lines='''both hands lay textured paper on the table|lay|paper|||both||
both hands take and open orange paint tube|open|orange paint tube||paint cap|both|paint cap|orange paint tube
both hands adjust open orange paint tube|adjust|orange paint tube|||both|paint cap|orange paint tube
right hand squeezes orange paint onto plastic palette|squeeze|orange paint tube||plastic palette|right|paint cap|orange paint tube
both hands recap orange paint tube and set it down|close|orange paint tube||paint cap|both||
left hand picks up paintbrush and dips it in water tray|dip|paintbrush||water tray|left|paintbrush|
left hand brushes water across plastic palette|brush|plastic palette|paintbrush||left|paintbrush|
left hand mixes orange paint on palette with wet brush|mix|orange paint|paintbrush|plastic palette|left|paintbrush|
left hand rinses orange paintbrush in water tray|rinse|paintbrush||water tray|left||
left hand wipes paint from plastic palette with tissue|wipe|plastic palette|tissue||left|tissue|
right hand moves cleaned palette aside while left holds tissue|move|plastic palette|||both|tissue|
right hand places first small paint dish on table|place|orange paint dish|||right||
right hand sets second small paint dish beside first|place|green paint dish|||right||
right hand lays third small paint dish below others|place|brown paint dish|||right||
both hands open orange tube and dispense paint into dish|squeeze|orange paint tube||orange paint dish|both|paint cap|orange paint tube
both hands close orange paint tube|close|orange paint tube||paint cap|both||orange paint tube
both hands set orange tube aside and open green tube|open|green paint tube||paint cap|both|paint cap|green paint tube
right hand dispenses green paint then recaps tube|squeeze|green paint tube||green paint dish|both||green paint tube
both hands set green tube aside and open brown tube|open|brown paint tube||paint cap|both|paint cap|brown paint tube
right hand dispenses brown paint and recaps tube|squeeze|brown paint tube||brown paint dish|both||
left hand mixes orange paint with water using brush|mix|orange paint|paintbrush|orange paint dish|left|paintbrush|
left hand stirs green paint with wet paintbrush|stir|green paint|paintbrush|green paint dish|left|paintbrush|
left hand rinses brush then returns to green paint|rinse|paintbrush||water tray|left|paintbrush|
left hand mixes green paint in dish|mix|green paint|paintbrush|green paint dish|left|paintbrush|
left hand swirls paintbrush through water tray|rinse|paintbrush||water tray|left|paintbrush|
left hand stirs brown paint while right steadies dish|stir|brown paint|paintbrush|brown paint dish|both|paintbrush|brown paint dish
left hand rinses brush then mixes brown paint again|mix|brown paint|paintbrush|brown paint dish|both|paintbrush|brown paint dish
left hand rinses brown paintbrush in water tray|rinse|paintbrush||water tray|left|paintbrush|brown paint dish
left hand rests paintbrush across tray while right lowers dish|set down|paintbrush||water tray|both||
right hand dips fingertip in orange paint|dip|orange paint||orange paint dish|right||
right hand stamps orange petal marks on paper|stamp|orange paint||paper|right||
both hands add orange paint to dish then close tube|squeeze|orange paint tube||orange paint dish|both||
right hand repeatedly stamps orange flower clusters on paper|stamp|orange paint||paper|right||
both hands add brown paint to dish and recap tube|squeeze|brown paint tube||brown paint dish|both||
right hand stamps brown flower centers and wipes fingertip|stamp|brown paint||paper|right||
both hands add green paint to dish and recap tube|squeeze|green paint tube||green paint dish|both||
right hand stamps green leaf marks between orange flowers|stamp|green paint||paper|right||
both hands inspect paper then take stained tissue|take|tissue||paper|both|tissue|
right hand moves painting aside while left holds tissue|move|paper|||both|tissue|
right hand lifts brown paint dish while left holds tissue|lift|brown paint dish|||both|tissue|brown paint dish
right hand wets fingertips then wipes them on tissue|wipe|green paint|tissue||both|tissue|
right hand picks up brown paint dish|pick up|brown paint dish|||right|tissue|brown paint dish
left hand wipes brown paint from dish with tissue|wipe|brown paint dish|tissue||both|tissue|brown paint dish
both hands refold stained tissue beside cleaned dish|fold|tissue|||both|tissue|
both hands take clean tissue and wipe fingertips|wipe|green paint|tissue||both|tissue|
right hand puts cleaned brown paint dish down|set down|brown paint dish|||right|tissue|
right hand shifts green and orange paint dishes|move|green paint dish||orange paint dish|right|tissue|
right hand slides painting back toward center|slide|paper|||right|tissue|
right hand adds green fingertip marks near top flowers|stamp|green paint||paper|right|tissue|
right hand lifts and tilts painting to inspect marks|lift|paper|||right|tissue|paper
right hand dips fingertip in green paint and adds final marks|stamp|green paint||paper|right|tissue|
both hands wipe paint from fingertips with tissue|wipe|green paint|tissue||both|tissue|'''
groups=[(0,10,'Prepare paper and test orange paint on the palette.','Paper is positioned, orange paint dispensed, and a wetted brush used on a plastic palette before the palette is wiped clean and moved aside.','Set up the working surface and test the paint consistency.'),(11,19,'Dispense three colors into separate dishes.','Three small dishes are set out and orange, green and brown paints squeezed into them, with tubes recapped after each color.','Keep the petal, leaf and center colors separately available.'),(20,28,'Dilute and mix each paint with a brush.','The brush alternates between the water tray and orange, green and brown dishes, stirring the paint before being rested across the tray.','Prepare fluid paint for fingertip stamping.'),(29,32,'Stamp orange petal clusters.','A fingertip is dipped in orange paint and pressed repeatedly onto paper; more orange is added before several groups of petal marks are built.','Create the flower shapes distributed over the paper.'),(33,34,'Add brown flower centers.','Brown paint is replenished and a fingertip touches the centers of orange petal groups, with wiping between dabs.','Give the orange clusters defined flower centers.'),(35,38,'Stamp green leaves and inspect the picture.','Green paint is replenished, fingertip marks added between the flowers and near their edges, and the painting briefly lifted and moved aside.','Complete the green leaf accents around the flowers.'),(39,46,'Clean fingers and wipe out the brown paint dish.','A tissue is wetted and used on fingertips, then repeatedly rubbed inside the brown dish. Cleaner tissue is taken and dishes repositioned.','Clear paint from the hands and the used brown mixing dish.'),(47,51,'Inspect the painting and add final green marks.','The paper is brought forward, green marks added, the sheet lifted for inspection and fingertips wiped again.','Finish the green accents and leave the floral picture on the table.')]
fix={20:dict(boundary_note='Includes brush pickup and several alternating dips between water tray and orange dish during74.54–83.83s.'),32:dict(boundary_note='119.56–159.65s contains repeated fingertip dipping/stamping and tissue pickup/wiping near144–148s and157–159s. Several hand-object changes lie within preserved fine.'),34:dict(boundary_note='168.94–194.6s alternates brown dipping/center stamping and wiping near183–186s and190s.'),36:dict(boundary_note='203.65–249.06s alternates green dipping/stamping, tissue rinse/wipe near219–222s and paper lifting near229–231s. Original long fine retained.'),51:dict(notes='Source end300.07s exceeds ffprobe300.067s by0.003s; helper keeps prescribed strict beyond-end null description rule.')}
write(v,goal,inv,lines,groups,'Viewed all ten overview sheets, all1103 dense frames and all native endpoint sheets. Fine boundaries untouched; coarse groups rewritten to match visible material preparation, petal stamping, centers, leaves and cleanup. The three long painting intervals have multiple material interactions recorded in boundary notes. Transitions remain endpoint-object-derived; independent predictability pending.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T224831863721Z/manifest.json'))
