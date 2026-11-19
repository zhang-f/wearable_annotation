from write_editor_batch import *
v='7d641f52d47eaf74'
goal=dict(title='Make seasoned mashed-avocado bread',description='Halve and pit an avocado, scoop its flesh onto a board, mash it with seasoning and bottled citrus juice, then spread it onto bread and add two shaker seasonings.',final_state='Bread slices are covered with mashed avocado and visible seasoning flakes.',procedure=['Cut around the avocado and twist its halves apart.','Remove the pit and scrape flesh from both skins onto the board with a spoon.','Collect a fork and seasoning, then mash the avocado on the board.','Squeeze bottled citrus juice over the mash and mix it through.','Bring bread from the toaster, spread the avocado over it and shake seasonings over the top.'])
inv=['avocado','avocado pit','avocado peel','knife','spoon','fork','cutting board','seasoning jar','seasoning lid','citrus juice bottle','bread','toaster','dark shaker','flake seasoning bottle','counter']
lines='''right hand cuts around the avocado with a knife|cut|avocado|knife|cutting board|right|avocado|knife
both hands twist the avocado halves apart|twist|avocado|||both|avocado|avocado
right fingers try to loosen the avocado pit|loosen|avocado pit||avocado|right|avocado|
left hand holds the pitted avocado half|hold|avocado|||left|avocado|
right hand levers the pit out with the knife|remove|avocado pit|knife|avocado|right||knife
right hand picks up the spoon|pick up|spoon|||right|avocado|spoon
right hand scoops avocado flesh onto the board|scoop|avocado|spoon|cutting board|right||spoon
right hand scrapes flesh from the other avocado half|scrape|avocado|spoon|cutting board|right|avocado|spoon
right hand scrapes remaining avocado flesh from the peel|scrape|avocado|spoon|cutting board|right|avocado peel|spoon
right hand clears the last avocado flesh from the skin|scrape|avocado|spoon|cutting board|right|avocado peel|spoon
both hands put the emptied avocado skins aside|place|avocado peel||counter|both||spoon
both hands clear the spoon and nearby utensils|place|spoon||counter|both||
right hand retrieves a fork from the drawer|pick up|fork|||right||fork
right hand positions the fork beside the avocado|position|fork||cutting board|right||fork
both hands open a small seasoning jar|open|seasoning jar|||both|seasoning jar|seasoning lid
left hand places the seasoning jar beside the board|place|seasoning jar||counter|left||fork
right hand repeatedly mashes avocado with the fork|mash|avocado|fork|cutting board|right||fork
right hand retrieves the citrus juice bottle|pick up|citrus juice bottle|||right||citrus juice bottle
right hand mashes the avocado further with the fork|mash|avocado|fork|cutting board|right||fork
right hand squeezes citrus juice over the mashed avocado|squeeze|citrus juice bottle||avocado|right||fork
right hand mixes the citrus juice into the avocado|mix|avocado|fork|cutting board|right||fork
right hand spreads mashed avocado over the bread|spread|avocado|fork|bread|right|bread|fork
right hand shakes seasoning over the avocado bread|sprinkle|dark shaker||bread|right|bread|dark shaker
right hand adds flake seasoning to the avocado bread|sprinkle|flake seasoning bottle||bread|right|bread|'''
groups=[(0,4,'Halve the avocado and remove its pit','A knife cuts around the avocado, both hands twist it apart, and the pit is loosened and removed with the knife.','Opens the avocado so its flesh can be extracted.'),(5,10,'Scoop the avocado flesh onto the board','A spoon scrapes flesh from both halves onto the cutting board; the skins are repeatedly scraped clean and put aside.','Collects the edible avocado in one place for mashing.'),(11,16,'Collect a fork and mash the avocado','Utensils are cleared, a fork is retrieved from a drawer, and a small seasoning jar is opened. The fork repeatedly presses and breaks up the avocado on the board.','Produces a spreadable avocado mash.'),(17,20,'Add bottled citrus juice and mix','A green citrus-juice bottle is retrieved; after further mashing its contents are squeezed over the avocado and stirred through with the fork.','Distributes the added liquid through the mashed avocado.'),(21,23,'Spread avocado onto bread and season','Bread is lifted from the toaster area and covered with forkfuls of avocado. A dark shaker and then a white-capped flake-seasoning bottle are shaken over the bread.','Finishes the avocado-covered bread with visible seasoning.')]
fix={3:dict(confidence='medium',notes='12.37–15s hands reposition the half and reach for the knife; source split preserved.'),11:dict(confidence='medium',notes='60.57–67.36s spoon/nearby utensil handling is partly below the frame.'),14:dict(confidence='medium',notes='86.12–93.44s seasoning container is handled, but exact contents are unreadable.'),16:dict(boundary_note='94.42–130.46s is one sustained mashing sequence; original long segment preserved.'),21:dict(boundary_note='158.83–176.53s includes bread retrieval and repeated mash transfer/spreading; original boundary preserved.'),23:dict(boundary_note='191.03–210.31s includes changing from the dark shaker to the flake-seasoning bottle; original boundary preserved.')}
write(v,goal,inv,lines,groups,'Reviewed all overview, 728 dense sampled frames and native end frames. Seasoning identities are not inferred from unreadable labels; green bottle described as bottled citrus juice. Bread is already in toaster area; insertion/toasting is not shown. Original fine endpoints retained. Final 3.29s shows holding/displaying the prepared bread outside the source fine coverage.',fix=fix,evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/7d641f52d47eaf74/20261106T073021401522Z/manifest.json')
