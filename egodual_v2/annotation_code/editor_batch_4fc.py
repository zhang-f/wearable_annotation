from write_editor_batch import *
write('4fc1922db3df47c4',dict(title='Replace the sealing washer in a garden hose coupling',description='Set tools and a yellow cloth beside an outdoor faucet, loosen and disconnect the hose, and briefly test the spray nozzle. Work the old rubber washer out of the brass hose coupling using pliers and a screwdriver, then press a replacement washer into the coupling. Reconnect the hose, wipe the faucet area and test the spray again.',final_state='The hose has been reattached to the outdoor faucet and water is sprayed through its nozzle after the washer work. Small removed washers and tools remain near the bucket.',procedure=['Place the cloth and tools beside the outdoor faucet.','Loosen the hose connection and check water flow through the nozzle.','Disconnect the hose and expose the washer in the brass coupling.','Use pliers and a screwdriver to free and remove the old washer.','Press a replacement washer into the coupling and check its seating.','Reconnect the hose, wipe the connection area and test the spray nozzle.']),['garden hose','hose coupling','faucet','spray nozzle','pliers','screwdriver','washer','cloth','bucket','ground'],'''
place the cloth beside the garden hose|place|cloth||ground|right||cloth
put down the pliers beside the hose|put down|pliers||ground|right||
turn the outdoor faucet handle|adjust|faucet|||right||
pick up the pliers|pick up|pliers|||right||pliers
loosen the hose coupling with the pliers|unscrew|hose coupling|pliers|faucet|both||pliers
put down the pliers|put down|pliers||ground|right||
turn the hose coupling by hand|unscrew|hose coupling||faucet|both|hose coupling|hose coupling
turn the faucet handle|adjust|faucet|||right||
pick up the spray nozzle|pick up|spray nozzle|||right||spray nozzle
raise the spray nozzle toward the garden|move|spray nozzle|||both||spray nozzle
squeeze the spray nozzle trigger|press|spray nozzle|||right||spray nozzle
turn the outdoor faucet handle|adjust|faucet|||right||
unscrew the hose coupling from the faucet|unscrew|hose coupling||faucet|both|hose coupling|
inspect the open hose coupling|inspect|hose coupling|||both|hose coupling|
pick up the yellow cloth|pick up|cloth|||right||cloth
spread the cloth on the ground|place|cloth||ground|both||
pick up the garden hose end|pick up|hose coupling|||right||hose coupling
hold the hose end beside the bucket|hold|hose coupling||bucket|right||hose coupling
pick up the pliers beside the hose|pick up|pliers|||right|hose coupling|pliers
insert the plier tips into the hose coupling|insert|pliers||hose coupling|right|hose coupling|pliers
pull at the washer with the pliers|remove|washer|pliers|hose coupling|right|hose coupling|pliers
turn the pliers in the right hand|adjust|pliers|||right|hose coupling|pliers
reposition the pliers near the hose coupling|move|pliers||hose coupling|right|hose coupling|pliers
pry inside the hose coupling with the pliers|remove|washer|pliers|hose coupling|right|hose coupling|pliers
set down the pliers beside the hose|put down|pliers||ground|right|hose coupling|
work the washer loose with the screwdriver|remove|washer|screwdriver|hose coupling|right|hose coupling|screwdriver
turn the hose coupling to inspect its opening|inspect|hose coupling|||left|hose coupling|
pry the washer with the pliers|remove|washer|pliers|hose coupling|right|hose coupling|pliers
put down the pliers on the ground|put down|pliers||ground|right|hose coupling|
reach for the loose washer|reach for|washer||ground|right|hose coupling|
remove the loosened washer with the fingertips|remove|washer||hose coupling|right|hose coupling|washer
pick up a washer from the ground|pick up|washer||ground|right|hose coupling|washer
insert the washer into the hose coupling|insert|washer||hose coupling|both|hose coupling|
press the washer into its seat|press|washer||hose coupling|right|hose coupling|
put down the screwdriver beside the hose|put down|screwdriver||ground|right|hose coupling|
press around the washer inside the coupling|press|washer||hose coupling|right|hose coupling|
raise the hose coupling toward the faucet|move|hose coupling||faucet|both||hose coupling
screw the hose coupling back onto the faucet|screw|hose coupling||faucet|both||hose coupling
pick up the screwdriver|pick up|screwdriver|||right||screwdriver
put down the screwdriver beside the loose washers|put down|screwdriver||ground|right||
pick up the yellow cloth|pick up|cloth|||right||cloth
wipe around the outdoor faucet with the cloth|wipe|faucet|cloth||right||cloth
pick up and raise the spray nozzle|pick up|spray nozzle|||right||spray nozzle
squeeze the nozzle trigger to spray water|press|spray nozzle|||right||spray nozzle
''',[(0,6,'Prepare tools and loosen the hose coupling','Set down the cloth and tools, turn the faucet handle and loosen the attached hose coupling with pliers and fingers.','Make the hose connection accessible for servicing.'),(7,12,'Check the spray and disconnect the hose','Operate the faucet and spray nozzle briefly, then return to the tap and unscrew the hose connection.','Expose the hose coupling and verify the water path before replacing its seal.'),(13,31,'Remove the washer from the hose coupling','Inspect the brass opening, arrange the cloth and hose, and repeatedly pry the washer with pliers and a screwdriver. Remove the loosened washer and pick up a replacement.','Clear the old seal and obtain the washer needed for the repair.'),(32,35,'Seat the replacement washer inside the coupling','Insert the washer and press around its edge with the fingertips. Set the tool aside and check that the ring lies within the coupling.','Restore the sealing surface at the hose connection.'),(36,43,'Reconnect the hose and test water flow','Carry the coupling back to the tap, thread it on, put tools down and wipe the faucet area. Raise and squeeze the spray nozzle to test the connected hose.','Return the hose to operation after the seal replacement.')],
'All overview, dense 3/15fps frames and native endpoints reviewed. Several long steps contain repeated tool repositioning; exact old/new washer identity is visually difficult because several small rings lie on the pavement. Descriptions use washer consistently and confidence is reduced where the precise manipulation or endpoint grip is occluded. No fine boundary changed. Prompt task name is not used to infer unseen plumbing work. Beyond/tail handling follows measured inventory duration.',fix={0:{'boundary_note':'t=2.1–3.4s moves cloth and tools toward the ground; cloth still held at boundary.'},3:{'boundary_note':'t=9.4–10.5s picks pliers up then raises them toward coupling.'},4:{'boundary_note':'t=11–21.7s repeated gripping, turning and releasing with pliers; compound segment.'},6:{'confidence':'medium','notes':'Coupling held at faucet; exact final degree of loosening is not visible.'},7:{'boundary_note':'t=28–29.9s faucet operation follows coupling handling.'},8:{'boundary_note':'t=30–31.6s right hand leaves faucet and collects spray nozzle.'},9:{'boundary_note':'Short boundary slice within raising the nozzle; spray begins afterward.'},11:{'boundary_note':'Returns toward faucet while holding nozzle, then turns handle near t=37s.'},12:{'boundary_note':'Long sequence t=37.5–50.2s turns and removes coupling, with repeated regrips.'},13:{'confidence':'medium','notes':'Small ring/object near coupling is partially hidden in the fingers.'},18:{'boundary_note':'t=62–63s transfers hose end to left and retrieves pliers.'},20:{'ambiguous':True,'confidence':'medium','notes':'Pliers enter coupling; small rubber component is obscured.'},21:{'confidence':'medium'},22:{'confidence':'medium'},23:{'confidence':'medium','ambiguous':True,'notes':'Tool tips and internal washer partly occluded; visible action is prying inside coupling.'},24:{'boundary_note':'t=71s puts tool down; t=72s points at coupling opening.'},25:{'boundary_note':'t=74–82s retrieves and repositions screwdriver, prying at washer.','confidence':'medium'},26:{'boundary_note':'t=83–84s inspects coupling; right moves toward another tool afterward.'},27:{'confidence':'medium','notes':'Pliers grip inside coupling; ring partly hidden.'},28:{'boundary_note':'End remains in tool-to-ground movement; release near t=88.4s.'},29:{'boundary_note':'0.83s cut divides reaching down and returning fingers toward coupling.','confidence':'medium'},30:{'confidence':'medium','ambiguous':True,'notes':'Fingers pull a small ring from coupling area; cannot positively identify whether it is the entire old seal.'},31:{'confidence':'medium','notes':'Picks up a black washer t=93s; old/new identity not visually certain.'},32:{'boundary_note':'t=95–103s inserts and repeatedly presses washer; fingers briefly pull it back for adjustment.','confidence':'medium'},33:{'confidence':'medium'},34:{'boundary_note':'t=106–107.5s sets tool down after seal manipulation.','confidence':'medium'},35:{'boundary_note':'t=108–110s presses/checks the ring, then releases the small piece.'},37:{'boundary_note':'t=112–125s multiple screw turns and regrips while reconnecting; extra handle touches.','confidence':'medium'},38:{'confidence':'medium'},42:{'boundary_note':'t=134.3–136s withdraws cloth, t=137s collects nozzle; contains two interactions.'},43:{'notes':'Spray visible t=139–142s, then nozzle is lowered; endpoint hand partly below the view.','confidence':'medium'}},evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/4fc1922db3df47c4/20261106T053808440081Z/manifest.json')
