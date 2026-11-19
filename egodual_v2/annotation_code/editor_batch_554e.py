from write_editor_batch import *
v='554e251921df992c'
write(v,dict(title='Clean and reinstall the range hood filter assembly',description='Disconnect the hood, remove two metal baffle filters and two round black filter covers, and carry the round covers to the sink. Wash both round covers with dish soap and a sponge, rinse and dry them, then reinstall the covers and metal filters. Reconnect power and operate the hood controls.',final_state='Both metal filters are fitted under the hood and the cord is reconnected. The final frames show the assembled hood with its illuminated display after the controls are tested.',procedure=['Disconnect the range hood power cord.','Remove both metal baffle filters and the two round filter covers.','Wash and rinse each round cover using dish soap and a sponge.','Dry the washed covers with paper towels.','Reinstall the round covers, then seat and secure the metal filters.','Reconnect the cord and test the hood controls.']),
['range hood','power cord','baffle filter','filter cover','sink','counter','faucet','sprayer','sponge','dish soap bottle','paper towel'],'''
unplug the range hood power cord|remove|power cord|||right||
idle: turn toward the range hood|||||unclear||
remove the baffle filter from the range hood|remove|baffle filter||range hood|both|baffle filter|baffle filter
put down the baffle filter on the stove|put down|baffle filter||counter|both||
remove the second baffle filter from the range hood|remove|baffle filter||range hood|both|baffle filter|baffle filter
put down the second baffle filter|put down|baffle filter||counter|right||baffle filter
unscrew the filter cover beneath the range hood|unscrew|filter cover||range hood|right||filter cover
remove the second filter cover|remove|filter cover||range hood|both|filter cover|filter cover
carry the filter covers to the sink|move|filter cover||sink|both||filter cover
pick up the sponge beside the sink|pick up|sponge|||right|filter cover|sponge
rinse the filter cover with the sprayer|rinse|filter cover|sprayer|sink|both|filter cover|sprayer
turn the faucet handle|adjust|faucet|||right|filter cover|
hold the filter cover beneath the faucet|hold|filter cover||sink|both|filter cover|filter cover
rinse the filter cover beneath running water|rinse|filter cover|sprayer|sink|both|filter cover|sprayer
place the filter cover in the sink|place|filter cover||sink|left||
pick up the sponge from its holder|pick up|sponge|||right||sponge
pick up the dish soap bottle|pick up|dish soap bottle|||left|dish soap bottle|sponge
squeeze dish soap onto the sponge|pour|dish soap bottle||sponge|left|dish soap bottle|sponge
return the dish soap bottle to the counter|put down|dish soap bottle||counter|left|dish soap bottle|sponge
pick up the filter cover from the sink|pick up|filter cover||sink|left|filter cover|sponge
scrub the filter cover with the sponge|wipe|filter cover|sponge||both|filter cover|sponge
turn the filter cover in the left hand|flip|filter cover|||left|filter cover|sponge
rinse the scrubbed filter cover with the sprayer|rinse|filter cover|sprayer|sink|both||
pick up the other filter cover|pick up|filter cover||sink|left|filter cover|sponge
pick up the dish soap bottle|pick up|dish soap bottle|||left|dish soap bottle|sponge
squeeze dish soap onto the sponge|pour|dish soap bottle||sponge|left|dish soap bottle|sponge
scrub the other filter cover with the sponge|wipe|filter cover|sponge||both|filter cover|sponge
pick up the sprayer|pick up|sprayer|||right|filter cover|sprayer
rinse the other filter cover|rinse|filter cover|sprayer|sink|both|filter cover|sprayer
turn the filter cover beneath the sprayer|flip|filter cover|sprayer|sink|left|filter cover|sprayer
rinse the remaining surface of the filter cover|rinse|filter cover|sprayer|sink|both|filter cover|sprayer
return the sprayer to its holder|place|sprayer||faucet|right||
place the washed filter covers beside the sink|place|filter cover||counter|both|filter cover|filter cover
adjust the filter covers on the counter|adjust|filter cover||counter|both|filter cover|filter cover
put down the filter covers|put down|filter cover||counter|both||
idle: turn toward the stove|||||unclear||
idle: look at the removed baffle filters|||||unclear||
reach for paper towels|reach for|paper towel|||right||
pick up the paper towels|pick up|paper towel|||both|paper towel|paper towel
carry the paper towels back to the sink|move|paper towel||sink|both||paper towel
wipe the filter cover with a paper towel|wipe|filter cover|paper towel||both|filter cover|paper towel
turn the dried filter cover|flip|filter cover|||left|filter cover|paper towel
put down the dried filter cover|put down|filter cover||counter|left||paper towel
pick up the other filter cover|pick up|filter cover|||left|filter cover|paper towel
wipe the other filter cover with the paper towel|wipe|filter cover|paper towel||both|filter cover|paper towel
turn the filter cover while drying it|flip|filter cover|paper towel||both|paper towel|filter cover
put down the dried filter cover|put down|filter cover||counter|right|paper towel|filter cover
pick up the dried filter cover again|pick up|filter cover|||right|paper towel|filter cover
wipe the counter beside the sink|wipe|counter|paper towel||left|paper towel|filter cover
carry the filter cover toward the range hood|move|filter cover||range hood|right||filter cover
raise the filter cover beneath the hood|move|filter cover||range hood|both|filter cover|filter cover
screw the filter cover back onto the hood|screw|filter cover||range hood|right||filter cover
pick up the other dried filter cover|pick up|filter cover|||left|filter cover|
screw the other filter cover onto the hood|screw|filter cover||range hood|left||
pick up the baffle filter from the stove|pick up|baffle filter|||both|baffle filter|baffle filter
insert the baffle filter into the hood|insert|baffle filter||range hood|both|baffle filter|baffle filter
secure the baffle filter beneath the hood|attach|baffle filter||range hood|both||
pick up the second baffle filter|pick up|baffle filter|||both|baffle filter|baffle filter
insert the second baffle filter into the hood|insert|baffle filter||range hood|both|baffle filter|baffle filter
secure the second baffle filter|attach|baffle filter||range hood|both||
reach for the range hood power cord|reach for|power cord|||left|power cord|
plug the range hood power cord into the outlet|insert|power cord|||both||
press the range hood control buttons|press|range hood|||right||
release the range hood control button|remove|range hood|||right||
press the range hood controls again|press|range hood|||right||
''',[(0,8,'Remove the hood filters and round covers','Disconnect the cord, release both metal filters and remove both round covers. Carry the round covers to the sink.','Expose and remove the components that will be cleaned.'),(9,22,'Wash and rinse the first round filter cover','Rinse the first cover, obtain a sponge and dish soap, scrub its surfaces and rinse away the soap. Set it back in the sink.','Remove visible residue from the first round cover.'),(23,34,'Wash and rinse the second round filter cover','Apply fresh soap to the sponge and scrub the other cover. Rinse it while turning it, then set both washed covers on the counter.','Finish washing the two removable round covers.'),(35,49,'Dry the covers and clear the sink area','Obtain paper towels, dry both covers and briefly wipe the counter. Collect a dried cover and move back toward the hood.','Prepare the washed parts for reinstallation without dripping.'),(50,59,'Reinstall the covers and metal baffle filters','Attach both round covers inside the hood and fit each metal baffle filter back into its opening. Secure their front edges.','Restore the assembled filter system.'),(60,64,'Reconnect power and check the hood controls','Reconnect the hood power cord and press several controls on the illuminated front panel.','Return the cleaned hood to use and check its controls.')],
'Overview, every dense step sheet, and native endpoint sheets reviewed from the evidence manifest. The task name suggests washing the metal filter, but the visible washing is of two round black covers; the rectangular baffle filters remain on the stove before reinstallation. Boundaries preserved. Short splits at 109.5–110.4s divide cover placement/regrasp; 173.18–173.44s divides button release. Physical stove surface is represented as counter in the common destination vocabulary. No new boundaries or tails added. Semantic predictability remains pending independent assessment.',
fix={0:{'ambiguous':True,'confidence':'medium','notes':'Cord movement is visible t=2.1s; end grip is outside the view.'},5:{'boundary_note':'t=11–12.0s lowers filter; it is still supported at the boundary before release.'},6:{'boundary_note':'t=13.3–15.4s cover removal includes a second reach; exact hand assignment partly obscured.','confidence':'medium'},9:{'boundary_note':'t=24.5s cover moves aside, t=27–29.9s right hand retrieves sponge; multiple interactions.'},10:{'boundary_note':'t=30–32s positions cover and sprayer; t=33–36s turns/rinses cover.'},14:{'confidence':'medium'},15:{'confidence':'medium'},18:{'boundary_note':'Bottle remains in left hand at t=49.867s and is released near t=50.0s.'},19:{'boundary_note':'t=50.1s reaches for cover while right holds sponge; continuation from soap return.'},21:{'boundary_note':'Continuous scrubbing/cover rotation t=56.6–57.7s, with rinsing beginning afterward.'},22:{'boundary_note':'t=58–60s rinses then t=61s sets cover down, more than one interaction.'},26:{'boundary_note':'t=66s returns bottle, then t=67–74s scrubs cover; multiple hand-object changes.'},29:{'boundary_note':'Short split within one continuous rinse/rotation t=82–83.2s.'},32:{'boundary_note':'Moves both covers to counter across t=89–91.9s; multiple grasps.'},34:{'boundary_note':'t=95.1–95.7s is continuous cover placement/moving away.'},35:{'notes':'No task-object interaction while turning toward stove.'},36:{'notes':'No hand-object interaction in this interval.'},40:{'boundary_note':'t=104–109s dries cover; t=109.4s begins setting it down.'},41:{'boundary_note':'0.1s cut divides continuing cover handling, no separate completed action.'},42:{'boundary_note':'0.35s cut falls during cover placement/release.'},43:{'boundary_note':'t=110.0–110.4s regrasp cover; wiping starts at t=110.5s.'},45:{'boundary_note':'t=116.1–117.1s includes towel reposition and cover rotation.'},47:{'boundary_note':'0.39s cut at t=118.7–119.09s splits cover regrasp.'},48:{'boundary_note':'t=119–120s wipes counter then moves towel aside; right retains cover.'},49:{'boundary_note':'0.43s slice during walking/carrying; no independent hand-object change.'},51:{'confidence':'medium','ambiguous':True,'notes':'Cover attachment t=127–132s is partly hidden by forearm; final released/held state uncertain.'},53:{'confidence':'medium','notes':'Attachment is partly hidden under hood, release visible by t=142.5s.'},54:{'boundary_note':'0.49s split during lifting the baffle filter from stove.'},63:{'boundary_note':'0.26s release slice after repeated control presses; no held object.'},64:{'boundary_note':'t=173.5–176s no interaction, t=177–180s presses controls again.'}},evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/554e251921df992c/20261106T053715577487Z/manifest.json')
