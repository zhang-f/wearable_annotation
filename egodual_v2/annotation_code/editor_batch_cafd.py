from write_editor_batch import *
v='cafd82c22fda743d'
goal=dict(title='Pan-fry dumplings and serve with dressing',description='Light the burner beneath a pan, add corn oil and place four prepared dumplings into the oil. Move and turn the dumplings with a red spatula as their surfaces brown, fetch a creamy dressing from the refrigerator, then plate the dumplings and add dressing at the table.',final_state='Four browned dumplings sit on a plate with a small amount of creamy dressing; a fork rests beside them.',procedure=['Turn on the burner and retrieve corn oil from the cabinet.','Pour oil into the pan and return the bottle.','Place four dumplings into the pan.','Move and turn the dumplings with a spatula while they brown.','Bring dressing from the refrigerator to the table.','Finish turning and transfer the dumplings to a plate.','Put the spatula in the sink, take a fork and carry the plate to the table.','Pour dressing beside the dumplings and handle them with the fork.'])
inv=['stove knob','oil bottle','oil cap','cabinet door','pan','dumpling','plate','spatula','refrigerator door','dressing bottle','drawer','fork','dressing cap']
lines='''right hand turns stove knob and lights burner under pan|turn|stove knob|||right||
left hand opens cabinet beneath sink|open|cabinet door|||left||
left hand retrieves corn oil bottle from cabinet|take|oil bottle|||left|oil bottle|
both hands uncap oil bottle then right pours into pan|pour|oil bottle||pan|both|oil cap|oil bottle
both hands screw cap back onto oil bottle|close|oil bottle||oil cap|both||oil bottle
left hand returns oil bottle to cabinet|place|oil bottle||cabinet door|left||
both hands close cabinet doors|close|cabinet door|||both||
idle looking toward heated pan and plate|wait||||none||
right hand reaches toward first dumpling on plate|reach|dumpling||plate|right||
right hand lifts first dumpling and places it into pan|place|dumpling||pan|right||
right hand transfers second dumpling from plate to pan|place|dumpling||pan|right||
right hand places third dumpling into pan|place|dumpling||pan|right||
right hand separates and places last dumpling into pan|place|dumpling||pan|both||
both hands rub fingertips and wipe on hanging towel|wipe|dumpling|||both||
right hand takes red spatula and slides it under dumplings|slide|dumpling|spatula|pan|right||spatula
right hand nudges dumplings apart with spatula|move|dumpling|spatula|pan|right||spatula
right hand lifts and turns dumplings with spatula|turn|dumpling|spatula|pan|right||spatula
right hand shifts dumplings around the hot pan|move|dumpling|spatula|pan|right||spatula
right hand turns dumplings then rests spatula on plate|set down|spatula||plate|right||
left hand opens refrigerator door|open|refrigerator door|||left||
right hand retrieves creamy dressing bottle from refrigerator|take|dressing bottle|||right||dressing bottle
right hand carries dressing bottle toward table|carry|dressing bottle|||right||dressing bottle
right hand places dressing bottle on table|place|dressing bottle|||right||
right hand repeatedly turns and repositions dumplings with spatula|turn|dumpling|spatula|pan|right||spatula
right hand lifts browned dumpling while left reaches for plate|lift|dumpling|spatula|pan|both||spatula
right hand transfers first dumpling onto left-held plate|place|dumpling|spatula|plate|both|plate|spatula
right hand lifts second dumpling and slides it onto plate|place|dumpling|spatula|plate|right|plate|spatula
right hand transfers third dumpling onto plate|place|dumpling|spatula|plate|right|plate|spatula
right hand lifts final dumpling and places it on plate|place|dumpling|spatula|plate|right|plate|spatula
right hand adjusts plated dumplings with spatula|adjust|dumpling|spatula|plate|right|plate|spatula
right hand lowers spatula toward empty pan|move|spatula||pan|right|plate|spatula
right hand puts spatula into sink|set down|spatula|||right|plate|
right hand opens cutlery drawer|open|drawer|||right|plate|
right hand takes fork and shuts drawer|take|fork||drawer|right|plate|fork
left hand carries plate of dumplings to table|carry|plate||dumpling|left|plate|fork
right hand sets fork beside dumplings as left lowers plate|place|fork||plate|both||
both hands open dressing bottle and right pours onto plate|pour|dressing bottle||plate|both||
right hand presses fork into dumpling on plate|press|dumpling|fork|plate|right||'''
groups=[(0,7,'Heat and oil the frying pan.','The burner is lit, corn oil retrieved from the lower cabinet, poured into the pan, recapped and returned before the cabinet closes.','Provide a hot oiled surface for frying the dumplings.'),(8,13,'Place four dumplings in the pan.','Each dumpling is lifted from the plate, adjusted by hand and placed into the oil; fingers are rubbed and wiped afterward.','Start frying all four dumplings in a single layer.'),(14,18,'Move and turn the dumplings as they fry.','The red spatula slides under the dumplings and repeatedly nudges or turns them before being placed on the empty plate.','Keep the dumplings separated and expose their surfaces to the pan.'),(19,22,'Fetch dressing for serving.','The refrigerator is opened, a creamy dressing bottle taken out and carried to the table.','Make the serving condiment available while frying continues.'),(23,24,'Finish browning and lift the first dumpling.','The spatula repeatedly turns and repositions the dumplings, revealing browned patches, then lifts one as the plate is taken.','Finish browning the dumplings before removal.'),(25,29,'Transfer all dumplings to the plate.','Four successive spatula transfers move the dumplings out of the pan and their positions on the plate are adjusted.','Collect the fried dumplings for serving.'),(30,35,'Put the spatula away and carry the plate to the table.','The spatula is put into the sink, a fork taken from the drawer, and the plate carried to the table with the fork placed beside the food.','Arrange the cooked dumplings and cutlery for eating.'),(36,37,'Add dressing and handle a dumpling with the fork.','The dressing bottle is opened and tilted over the plate, then recapped and set down; the fork presses into a dumpling.','Finish the serving with creamy dressing.')]
fix={3:dict(boundary_note='15.11–20.51s contains cap removal and oil pouring18.5–20s.'),14:dict(boundary_note='67.88–77.18s includes spatula pickup69s and subsequent pan contact74–77s.'),18:dict(boundary_note='91.49–95.42s includes turning dumplings and spatula placement94.5s.'),23:dict(boundary_note='108.03–165.33s includes return to stove, spatula pickup around110s, many individual dumpling turns and pauses142–149s; retained long source fine.'),36:dict(boundary_note='196.87–209.98s combines dressing bottle pickup/uncapping, pouring200–205s, recapping206–209s and placement. Preserved fine includes several hand-object changes.')}
write(v,goal,inv,lines,groups,'Viewed all7 overview sheets, all775 dense frames and all38 native endpoint frames. Fine boundaries retained and every description rewritten. Food described as dumplings without asserting unseen filling. Coarse divisions rebuilt around visible heating/oiling, loading, frying, dressing retrieval, plating and serving. Predictability pending independent testing.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T225117664381Z/manifest.json'))
