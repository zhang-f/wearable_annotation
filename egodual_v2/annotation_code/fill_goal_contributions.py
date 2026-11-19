"""Add only missing procedure/contribution fields to reviewed derived annotations."""
import json,pathlib,tempfile,os,copy,hashlib
B=pathlib.Path(__file__).resolve().parent
D={
'0573fc312656e95a':(
'Gather the curtain and mark an initial hook position.|Measure the spacing, reposition the hook, and mark its mounting holes again.|Select drill bits and drill the marked wall holes.|Repeatedly widen the holes and press wall anchors into them.|Align the hook with the anchors and start the mounting screws.|Tighten the screws and check the hook by hand.|Gather the curtain inside the mounted hook.',
['Establishes an initial mounting position beside the curtain.','Refines the hook location and marks the holes to drill.','Creates holes for the hook mounting hardware.','Seats anchors that will receive the mounting screws.','Connects the hook to the wall anchors.','Secures the hook and checks its attachment.','Uses the installed hook to hold the curtain aside.']),
'3a122ee7ff513956':(
'Fetch a plate and spread tortilla chips across it.|Open the shredded-cheese bag and pour cheese over the chips.|Put the plate in the microwave and heat it.|Remove the plate, sample a chip, add seasoning and salt, and use a fork on the chips.',
['Provides the chip base on a plate for the cheese topping.','Adds the cheese that will melt over the chips.','Heats the cheese-covered chips.','Checks the heated chips and adds the final seasonings.']),
'57d901c4644ef3d8':(
'Retrieve a bowl and bring it to the ingredients on the counter.|Open the cocoa package and add cocoa and the visible pale dry ingredient to the bowl.|Add milk and stir, adding more milk while mixing.|Carry the mixture to the microwave and heat it.|Remove the bowl and stir the heated brown mixture at the counter.',
['Provides the mixing vessel beside the ingredients.','Combines the dry ingredients with liquid to begin the mixture.','Blends the ingredients before heating.','Heats the mixed ingredients in the bowl.','Mixes the heated pudding mixture for its final consistency.']),
'58911a11f1e276bc':(
'Put a bread slice into the toaster, lower the lever, and wait.|Remove the toast and spread cream cheese with repeated knife strokes.|Shake the reddish seasoning over the toast and finish spreading and sprinkling.',
['Prepares the toasted bread base.','Covers the toast with its cream cheese topping.','Adds the final seasoning over the cream cheese.']),
'6ad710d3e252678a':(
'Arrange the soapy-water bowl, brush, cloth, and sneaker.|Dip the brush and scrub the sneaker, with a brief phone interruption.|Re-dip the brush and continue scrubbing different areas of the sneaker.|Wipe the sneaker with the yellow cloth.',
['Places the shoe and cleaning supplies within reach.','Starts removing dirt from the sneaker with the wet brush.','Continues cleaning the shoe surface through repeated brush passes.','Wipes moisture and residue from the scrubbed sneaker.']),
'aac31709beff7418':(
'Wipe the surface near the furniture corner.|Peel adhesive backing and inspect the small clear pieces.|Press the first adhesive pieces into position along the furniture edges.|Continue peeling and pressing additional pieces at successive positions.|Press the remaining pieces into place and check their contact with the surface.',
['Prepares the receiving surface for adhesive contact.','Exposes adhesive and readies a piece for placement.','Begins attaching the protective pieces to the furniture edges.','Extends the adhesive protection to additional edge positions.','Continues securing the remaining pieces; the track ends during the final application.']),
'af57359bc6056d66':(
'Turn the furniture upside down and take a disposable wipe.|Wipe the exposed wooden legs with wipes and a cloth.|Peel felt pads from the backing sheet and press them onto leg ends.|Continue applying and adjusting pads on the other leg ends.|Rotate the furniture and press or inspect the fitted pads.',
['Exposes the leg ends and provides a cleaning wipe.','Cleans the leg surfaces before applying adhesive pads.','Adds protective felt to the first leg ends.','Adds protective felt to further leg ends.','Checks and seats the pads on the furniture legs.']),
'b10afe8715607c52':(
'Place the split English muffin in the toaster oven and toast it.|Remove the halves and arrange them on a baking tray.|Drizzle oil over the muffin halves and fetch a spoon.|Spread pizza sauce and shredded cheese over both halves.|Open the pepperoni package and arrange slices over the cheese.|Put the topped muffin halves back in the toaster oven.|Check the pizzas while they bake and remove the tray.',
['Toasts the muffin bases before adding wet toppings.','Arranges the bases on a tray for topping and baking.','Adds oil and prepares a utensil for spreading sauce.','Builds the sauce and cheese layers of the muffin pizzas.','Adds the pepperoni topping.','Heats the assembled pizzas in the toaster oven.','Checks the baking pizzas and retrieves the tray.']),
'b72e49ddb2816af6':(
'Crack an egg and transfer its contents into a glass.|Open the salsa jar, add salsa, and stir.|Fetch the hot sauce, pour some into the glass, and stir again.|Place the glass in the microwave and start heating.|Open the microwave to inspect the contents and set more cooking time.|Remove the hot glass with a towel and add more sauce.|Carry the glass to the table and eat with a spoon.',
['Provides the egg base in its cooking vessel.','Combines salsa with the egg.','Adds and mixes the hot-sauce seasoning.','Begins cooking the egg mixture.','Checks the egg and resumes heating.','Retrieves the heated mixture and adds finishing sauce.','Serves and eats the prepared egg mixture.']),
'cfeb935f46cb7112':(
'Cut the cardboard center and notch opposing edges to make a loom.|Wind orange yarn through the notches to form the warp.|Pass blue yarn over and under the orange strands and pull the rows together.|Trim loose yarn and projecting cardboard tabs.|Cut the woven square free of the frame and place it on the table.',
['Creates a notched frame to support the yarn.','Establishes the warp strands for weaving.','Interlaces the blue weft through the orange warp to form the woven square.','Tidies the surrounding loose material before release.','Releases the woven square from the temporary loom.']),
'd09110ca079693c3':(
'Open the wallet and empty coins onto the table.|Empty the bag of thread spools and sewing pins beside the coins.|Sort the mixed objects into piles by type.|Move the objects into counted groups and write counts on the notepad.',
['Makes the objects available for sorting and counting.','Separates the object categories before counting them.','Records the quantities after grouping and counting each category.']),
'd1b4bd88ef655ac6':(
'Feel along the bifold door edge and inspect its fit.|Work at the bottom hinge, briefly moving a basket aside.|Swing the door open and closed to test the fit.|Return to the lower hinge, make further adjustments, and test the door again.',
['Inspects the fit and begins working on the lower hinge; the tool is obscured.','Tests the door movement after the initial hinge work.','Continues adjusting and retesting the door fit.']),
'd2037e676003fddb':(
'Circle organisms on the food-web diagram and label primary consumers.|Add producer and secondary-consumer labels.|Draw connections and add tertiary-consumer labels.|Write the ten-percent energy-transfer note and sketch a pyramid beside the food web.|Label the pyramid tiers and point to corresponding organisms.|Point to examples on the annotated food web.',
['Identifies the plants and the organisms feeding on them.','Adds more trophic-level labels to the food web.','Connects organisms and labels the upper consumer level.','Adds a visual explanation of reduced energy at successive levels.','Maps the food-web organisms onto the pyramid levels.','Reviews the annotated relationships using examples on the diagram.']),
'd5a737cf7eacb871':(
'Inspect the drawer knob and remove its loose screw.|Search the storage drawer and parts container for a suitable screw.|Position a replacement screw in the knob attachment.|Turn the screwdriver repeatedly to seat the screw.|Open and close the drawer to check the knob.|Work on the screw again and finish the adjustment.|Push the drawer closed.',
['Exposes the loose fastener for replacement.','Finds a candidate replacement fastener.','Positions the replacement for attachment.','Works the screw into the knob attachment.','Checks the knob while operating the drawer.','Resumes securing the knob after the fit test.','Returns the drawer to its closed position.']),
'd68b4e58600a7f11':(
'Wipe the pot and cover the work surface.|Open and pour black paint, then prepare the foam brush.|Rotate the pot and brush on the black base coat.|Use a smaller brush to add colored decorative strokes.|Add and mix more paint on the palette.|Continue the colored pattern around the pot and put it down.',
['Prepares the pot and protects the surrounding work surface.','Readies the base-coat paint and applicator.','Creates the black background for the colored decoration.','Adds the colored decorative pattern over the base coat.','Provides mixed colors for the remaining pattern.','Extends the decoration around the pot and finishes the visible painting.']),
'd6cb618bb700b7c0':(
'Handle the needle and white thread, cutting and threading the working length.|Lay the plaid shirt on the mat and position the button area.|Pass the needle repeatedly through the button and fabric, pulling the thread through.|Continue stitching while holding the fabric and button in position.|Finish the visible needle and thread work and inspect the shirt area.',
['Prepares the needle and thread for attaching the button.','Positions the shirt and starts joining the button to the fabric.','Adds further stitches through the button and fabric.','Continues the button attachment through the final visible stitching.']),
'e15723e58a5486d3':(
'Unscrew the flashlight cap and remove the batteries and holder.|Try inserting and seating replacement batteries in the holder and body.|Press the battery assembly into position and screw the cap on.|Reopen the cap to recheck the battery, then close it again.|Switch on the flashlight to test its beam and set it down.',
['Opens the battery compartment and removes the old cells.','Attempts to fit the replacement cells into the flashlight assembly.','Seats the assembly and closes the battery compartment.','Rechecks the assembly and verifies that the flashlight produces a beam.']),
'e243dd75d82b5ef5':(
'Lift the toilet seat and access its hinge fasteners.|Retrieve the screwdriver and repeatedly turn the seat fastener.|Switch to pliers to work on the fastener from another angle.|Return to the screwdriver for further tightening.|Set the tools on the lowered seat and step away.',
['Exposes the hinge fastening and prepares the screwdriver.','Works the loose seat fastening with the screwdriver.','Uses pliers for the part of the fastening reached from another angle.','Completes the visible adjustment and puts the tools down.']),
'e531cded0108b6c3':(
'Spread the protective plastic sheet and place white paper on it.|Position the heart-shaped mask on the paper.|Pull and cut tape to secure the mask.|Spray gold paint around the mask and lift the mask away.|Trace around the heart with the purple marker and add the small writing below it.',
['Arranges the protected paper surface and heart mask.','Secures the mask and applies the surrounding paint; marker work continues beyond the retained fine track.'])}
report=[]
for v,(procedure,contributions) in D.items():
 p=B/'videos'/f'{v}.json';d=json.loads(p.read_text());before=copy.deepcopy(d);assert len(contributions)==len(d['coarse']),v
 assert not d['goal'].get('procedure'),v
 d['goal']['procedure']=procedure.split('|')
 for c,value in zip(d['coarse'],contributions):assert not c.get('goal_contribution');c['goal_contribution']=value
 stripped=copy.deepcopy(d);stripped['goal'].pop('procedure')
 for c in stripped['coarse']:c.pop('goal_contribution')
 assert stripped==before,(v,'unexpected existing-field change')
 # Read again immediately before atomic replace to detect a concurrent edit.
 assert json.loads(p.read_text())==before,(v,'concurrent modification')
 fd,tmp=tempfile.mkstemp(dir=p.parent)
 with os.fdopen(fd,'w')as f:json.dump(d,f,indent=2,ensure_ascii=False);f.write('\n')
 os.replace(tmp,p)
 rec=dict(video_id=v,procedure_items=len(d['goal']['procedure']),contributions_added=len(contributions),only_two_requested_fields_changed=True)
 report.append(rec)
 with open(B/'goal_contribution_completion.jsonl','a')as f:f.write(json.dumps(rec)+'\n')
 print(v,'saved',flush=True)
(B/'goal_contribution_completion_report.json').write_text(json.dumps(report,indent=2)+'\n')
