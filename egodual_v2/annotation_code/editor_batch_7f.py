from write_editor_batch import *
v='7f1c64f7d0880938'
goal=dict(title='Make cucumber and hummus tortilla pinwheels',description='Spread hummus over a flour tortilla, shave lengthwise cucumber ribbons onto it with a peeler, roll the tortilla tightly and slice it into rounds for a green plate.',final_state='A green plate holds the sliced tortilla pinwheels; cucumber and hummus remain beside the cutting board.',procedure=['Remove a tortilla from its bag and lay it flat on the board.','Open the hummus tub, peel off its seal and spread hummus across the tortilla with a blue spreader.','Shave thin cucumber ribbons directly over the hummus layer.','Roll the tortilla tightly around the cucumber.','Unsheath the knife, cut the roll into rounds and transfer the pieces to a green plate.','Lift the plate to show the pinwheels.'])
inv=['tortilla bag','tortilla','cutting board','hummus tub','hummus lid','hummus seal','hummus','spreader','cucumber','peeler','knife','knife sheath','pinwheel','green plate','counter']
lines='''both hands open the tortilla bag and remove a tortilla|remove|tortilla||tortilla bag|both|tortilla|tortilla
both hands lay the tortilla flat on the cutting board|place|tortilla||cutting board|both||
right hand lifts the hummus tub lid|open|hummus lid||hummus tub|right|hummus tub|
both hands peel the seal from the hummus tub|peel|hummus seal||hummus tub|both|hummus tub|hummus seal
right hand puts the seal aside and collects the spreader|pick up|spreader|||right||spreader
left hand steadies the open hummus tub|hold|hummus tub|||left||spreader
right hand scoops hummus and spreads it onto the tortilla|spread|hummus|spreader|tortilla|right||spreader
right hand spreads another portion of hummus across the tortilla|spread|hummus|spreader|tortilla|right||spreader
right hand smooths hummus across the tortilla surface|spread|hummus|spreader|tortilla|right|cucumber|peeler
right hand shaves cucumber ribbons over the tortilla|shave|cucumber|peeler|tortilla|right|cucumber|peeler
right hand shaves another cucumber ribbon onto the tortilla|shave|cucumber|peeler|tortilla|right|cucumber|peeler
right hand pulls the peeler along the cucumber again|shave|cucumber|peeler|tortilla|right|cucumber|peeler
right hand lays more shaved cucumber onto the hummus|shave|cucumber|peeler|tortilla|right|cucumber|peeler
right hand shaves a further cucumber ribbon onto the tortilla|shave|cucumber|peeler|tortilla|right|cucumber|peeler
right hand repeats lengthwise strokes with the cucumber peeler|shave|cucumber|peeler|tortilla|right|cucumber|peeler
right hand shaves the final cucumber ribbons onto the tortilla|shave|cucumber|peeler|tortilla|right|cucumber|peeler
both hands set the cucumber and peeler aside|place|cucumber||cutting board|both||
both hands tightly roll the cucumber-filled tortilla|roll|tortilla|||both|tortilla|tortilla
left hand steadies the rolled tortilla on the board|hold|tortilla||cutting board|left|tortilla|
both hands remove the sheath from the blue-handled knife|unsheathe|knife||knife sheath|both||knife
right hand cuts the first round from the tortilla roll|cut|tortilla|knife|cutting board|right|tortilla|
right hand transfers the first pinwheel off the board|place|pinwheel||green plate|right|tortilla|
right hand cuts another round from the tortilla roll|cut|tortilla|knife|cutting board|right|tortilla|
right hand transfers another pinwheel toward the plate|place|pinwheel||green plate|right|tortilla|
right hand cuts a further pinwheel from the roll|cut|tortilla|knife|cutting board|right|tortilla|
right hand cuts and transfers the next tortilla round|cut|tortilla|knife|cutting board|right|tortilla|
right hand slices another pinwheel from the tortilla roll|cut|tortilla|knife|cutting board|right|tortilla|
right hand cuts another round and moves it aside|cut|tortilla|knife|cutting board|right|tortilla|
right hand slices and lifts another tortilla pinwheel|cut|tortilla|knife|cutting board|right|tortilla|
right hand cuts and transfers the remaining tortilla rounds|cut|tortilla|knife|cutting board|right|tortilla|
right hand moves the final cut pinwheel toward the plate|place|pinwheel||green plate|right|tortilla|
left hand lifts the green plate of pinwheels|lift|green plate|||left|green plate|
left hand holds the finished pinwheels on the plate|hold|green plate|||left|green plate|'''
groups=[(0,1,'Lay out the tortilla','The tortilla bag is opened, one tortilla is removed and laid flat on the cutting board.','Creates a flat base for the pinwheel filling.'),(2,8,'Open the hummus and coat the tortilla','The hummus lid and inner seal are removed. A blue spreader repeatedly scoops and smooths hummus over the tortilla surface.','Provides the spread layer that surrounds the cucumber in the rolled tortilla.'),(9,16,'Shave cucumber ribbons onto the hummus','One hand holds the cucumber while the other draws a peeler lengthwise, dropping successive thin ribbons across the tortilla. The cucumber and peeler are set aside.','Builds a thin cucumber layer that can roll with the tortilla.'),(17,18,'Roll the filled tortilla','Both hands curl and tuck the tortilla edge, rolling the hummus and cucumber into a tight cylinder that is steadied on the board.','Forms the cylinder whose cross-sections will become pinwheels.'),(19,30,'Slice and plate the pinwheels','The blue-handled knife is unsheathed. One hand steadies the roll while the other repeatedly cuts rounds, sets down the knife and transfers each piece toward the plate.','Divides the filled roll into individual serving pieces.'),(31,32,'Display the finished pinwheels','The green plate is lifted into view with the arranged tortilla rounds. The last source segment extends 0.1s beyond the actual video.','Shows the completed plated pinwheels.')]
fix={8:dict(boundary_note='55.65–68.2s includes finishing the hummus spread and collecting cucumber/peeler.'),17:dict(boundary_note='107.76–138.5s is prolonged rolling and tucking; source boundary retained.'),25:dict(boundary_note='169.6–177.2s includes slicing, setting down the knife and moving a pinwheel to the plate.'),29:dict(boundary_note='198.93–204.7s includes a cut and piece transfer; source boundary retained.')}
write(v,goal,inv,lines,groups,'Reviewed all overview sheets, all 747 dense sampled frames and native end frames. Pale green object is cucumber, shaved with a peeler; it is not a cheese block. Hummus label and appearance are visible. Original fine timing retained. Final fine#32 ends at212.5s versus212.4s true duration and is left undescribed under the strict overrun rule. Predictability pending independent testing.',fix=fix,evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/7f1c64f7d0880938/20261106T073125616951Z/manifest.json')
