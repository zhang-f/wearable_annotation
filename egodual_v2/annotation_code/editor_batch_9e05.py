from write_editor_batch import *
v='9e059416742fa71d'
goal=dict(title='Clean and reorganize the cutlery drawer',description='Empty the kitchen drawer onto the counter, wipe the drawer, install a gray compartment organizer, and return cooking tools, cutlery, and chopsticks in grouped compartments.',final_state='The utensils are grouped inside the gray organizer, the counter is cleared, and the drawer is closed.',procedure=['Open the drawer and remove the cooking tools, measuring utensils, cutlery, and chopsticks onto the counter.','Fold the cloth and wipe the empty drawer base and corners.','Separate, inspect, and fit the expandable organizer and its side trays into the drawer.','Return the large tools and measuring utensils, adjusting their arrangement.','Sort forks, knives, spoons, and chopsticks into separate compartments and close the drawer.'])
lines='''left hand pulls open the cutlery drawer|open|drawer|||left||
both hands lift a small utensil cup onto the counter|place|utensil cup||counter|both||
both hands move nested measuring cups onto the counter|place|measuring cups||counter|both||
both hands remove a small metal kitchen tool|remove|kitchen tool||drawer|both||kitchen tool
left hand places the mesh strainer on the counter|place|strainer||counter|left||
both hands lift the whisk from the drawer|pick up|whisk||drawer|both|whisk|whisk
both hands set the whisk beside the strainer|place|whisk||counter|both||
both hands lay cooking tools on the counter|place|kitchen tool||counter|both||
right hand places a metal spatula on the counter|place|metal spatula||counter|right||
both hands remove the peeler and can opener|remove|peeler||drawer|both|can opener|
both hands place the bench scraper on the counter|place|bench scraper||counter|both||
right hand removes the green kitchen thermometer|remove|kitchen thermometer||drawer|right||
both hands lift paddles and measuring spoons from the drawer|remove|rice paddle||drawer|both|rice paddle|measuring spoons
both hands place the paddles and spoons on the counter|place|rice paddle||counter|both||
both hands remove and place serving spoons on the counter|place|serving spoon||counter|both||
both hands gather spoons and place them on the counter|place|spoon||counter|both||
both hands gather forks and place them on the counter|place|fork||counter|both||
both hands remove the remaining forks from the drawer|remove|fork||drawer|both||
both hands gather chopsticks and place them on the counter|place|chopsticks||counter|both||
right hand wipes the empty drawer with the cloth|wipe|drawer|cloth||right|cloth|cloth
both hands fold the cloth and set it aside|fold|cloth||counter|both||
right hand brushes across the empty drawer base|brush|drawer|||right||
both hands pick up the gray cutlery organizer|pick up|organizer|||both|organizer|organizer
both hands separate the organizer and long side tray|separate|organizer||side tray|both|organizer|organizer
both hands inspect and position the organizer side trays|position|side tray||drawer|both|organizer|
right hand aligns the side tray in the drawer|align|side tray||drawer|right|organizer|
both hands lower the compartment organizer into the drawer|place|organizer||drawer|both|organizer|organizer
both hands adjust the organizer and its sliding sides|adjust|organizer||drawer|both||
right hand places the bench scraper into the organizer|place|bench scraper||organizer|right||
right hand returns a black-handled tool to the drawer|place|kitchen tool||organizer|right||
right hand returns another small kitchen tool|place|kitchen tool||organizer|right||
right hand lays long cooking tools along the drawer side|place|kitchen tool||organizer|right||
right hand returns another black-handled tool|place|kitchen tool||organizer|right||
right hand places the metal spatula into the side compartment|place|metal spatula||organizer|right||
both hands position the peeler and shift nearby utensils|position|peeler||organizer|both||peeler
left hand places nested measuring cups into the organizer|place|measuring cups||organizer|both||
left hand returns the green kitchen thermometer|place|kitchen thermometer||organizer|left||
both hands rearrange tools beside the measuring cups|arrange|kitchen tool||organizer|both||kitchen tool
both hands adjust the tools in the side compartments|adjust|kitchen tool||organizer|both||
both hands reposition the peeler beside the measuring cups|position|peeler||organizer|both|peeler|
both hands settle the peeler and adjacent tools|arrange|peeler||organizer|both||
left hand gathers wooden utensils and measuring spoons|pick up|wooden utensil||counter|left|wooden utensil;measuring spoons|
right hand arranges small measuring utensils in the organizer|arrange|measuring spoons||organizer|both|wooden utensil;measuring spoons|
both hands nest measuring spoons together in the drawer|nest|measuring spoons||organizer|both||measuring spoons
right hand reaches toward the counter utensils|reach|strainer||counter|right||
right hand places the strainer into the organizer|place|strainer||organizer|right||
both hands return and arrange the serving spoons|place|serving spoon||organizer|both|serving spoon|
both hands straighten the serving spoons in their compartment|arrange|serving spoon||organizer|both||
left hand moves a small metal kitchen tool into the drawer|place|kitchen tool||organizer|left||
both hands fit the small utensil cup into the organizer|place|utensil cup||organizer|both||
right hand adjusts the utensil cup in its compartment|adjust|utensil cup||organizer|right||
right hand shifts the cup and adjacent tools|arrange|utensil cup||organizer|right||
both hands pick up the remaining paddles and wooden utensils|pick up|rice paddle||counter|both|rice paddle|wooden utensil
both hands place the paddles and wooden utensils into compartments|place|rice paddle||organizer|both||
both hands collect and align the forks|align|fork||organizer|both|fork|fork
both hands arrange the forks in the lower compartment|arrange|fork||organizer|both||
both hands gather table knives from the counter|pick up|table knife||counter|both|table knife|
both hands align the knives in an organizer compartment|arrange|table knife||organizer|both||
both hands collect and arrange spoons in the organizer|arrange|spoon||organizer|both||spoon
both hands nest and straighten the remaining spoons|arrange|spoon||organizer|both||
both hands align the spoons before reaching for chopsticks|arrange|spoon||organizer|both|chopsticks|chopsticks
both hands straighten chopsticks inside the organizer|arrange|chopsticks||organizer|both||
both hands gather the remaining chopsticks from the counter|pick up|chopsticks||counter|both||
both hands align chopsticks and adjust neighboring utensils|arrange|chopsticks||organizer|both||
both hands push the organized drawer closed|close|drawer|||both||'''
groups=[(0,13,'Remove the cooking and measuring tools','The drawer is opened and the small utensil cup, measuring cups, strainer, whisk, cooking tools, paddles, and measuring spoons are laid on the counter.','Clears the larger items for cleaning and organizer installation.'),(14,18,'Empty the remaining cutlery','Serving spoons, table spoons, forks, and chopsticks are collected and grouped on the counter.','Leaves the drawer base empty.'),(19,21,'Wipe the drawer interior','A folded gray cloth wipes the base and corners; the cloth is folded away and the base checked with the hand.','Provides a clean surface for the organizer.'),(22,27,'Fit the compartment organizer','The gray organizer and separate long trays are examined, positioned in the drawer, and adjusted until they sit together.','Creates the compartments for systematic storage.'),(28,40,'Return the large kitchen tools','The bench scraper, black-handled tools, long utensils, metal spatula, measuring cups, thermometer, and peeler are placed and repositioned.','Allocates the larger and irregular tools to the side and deep compartments.'),(41,53,'Store measuring and serving utensils','Measuring spoons, strainer, serving utensils, small utensil cup, paddles, and wooden utensils are fitted into their compartments.','Completes storage of cooking accessories.'),(54,59,'Sort forks, knives, and spoons','Forks, knives, and spoons are gathered in turn and nested or aligned in separate compartments.','Makes the everyday cutlery easier to retrieve.'),(60,64,'Finish the chopsticks and close the drawer','The chopsticks are gathered, aligned alongside the cutlery, nearby utensils are adjusted, and the drawer is closed.','Finishes the organized drawer and clears the counter.')]
fix={3:dict(confidence='medium',ambiguous=True,notes='Small rectangular metal tool partly occluded; exact subtype not asserted.'),7:dict(confidence='medium',notes='Two cooking utensils removed together; exact subtype of one black-handled item unclear.'),18:dict(boundary_note='Includes gathering chopsticks at t=55–61s and setting them on counter around t=62–63s.'),19:dict(boundary_note='Includes cloth folding t=65–69s before wiping t=70–76s.'),44:dict(boundary_note='Very short inherited 0.08s boundary within the continuous reach for the strainer around t=166.12–166.20s; retained.'),46:dict(boundary_note='Includes touching chopsticks t=169–170s, then collecting serving spoons t=171s and placing them t=173–175s.'),50:dict(boundary_note='Continuous utensil-cup adjustment across boundaries around t=186.7–187.32s.'),60:dict(boundary_note='Begins with spoon adjustment before chopsticks are collected at t=250–253s.'),62:dict(boundary_note='Includes picking up chopsticks t=262–263s and placing/alignment t=264–266s.')}
write(v,goal,['drawer','counter','utensil cup','measuring cups','kitchen tool','strainer','whisk','metal spatula','peeler','can opener','bench scraper','kitchen thermometer','rice paddle','measuring spoons','serving spoon','spoon','fork','chopsticks','cloth','organizer','side tray','wooden utensil','table knife'],lines,groups,'Reviewed nine overview sheets, all 1088 dense frames and all 65 native endpoints. Fine boundaries preserved, including two very short continuous adjustments. Some small black-handled tool subtypes remain visually uncertain and are named conservatively. Remaining 0.314s after the last fine end shows the closed drawer.',fix=fix,evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/9e059416742fa71d/20261106T075328741525Z/manifest.json')
