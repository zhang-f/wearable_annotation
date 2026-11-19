from write_editor_batch import *
v='9186ff4997024eb1'
goal=dict(title='Make a button-flower bouquet',description='Thread and twist colored pipe cleaners through buttons to form individual flower heads, gather the stems, and wrap them in green paper.',final_state='Several button-topped stems are gathered inside a green paper sleeve and held up.',procedure=['Lay out the pipe cleaners and select buttons from the small box.','Thread buttons onto pipe-cleaner tips and bend or twist the ends to hold each head.','Repeat with red, blue, and gray stems and different button combinations.','Gather the finished stems, fan the button heads, and wrap green paper around the bundle.'])
lines='''both hands lay colored pipe cleaners on the table|place|pipe cleaner||table|both||
left hand selects buttons from the box|pick up|button||button box|left|button|
left hand places another button beside the others|place|button||table|left||
left hand adds another button to the row|place|button||table|left||
left hand arranges selected buttons on the table|arrange|button||table|left||
right hand selects more buttons from the box|pick up|button||button box|right||button
right hand places another button beside the row|place|button||table|right||
right hand finishes arranging the selected buttons|arrange|button||table|right||
right hand selects a red pipe cleaner|pick up|red pipe cleaner||table|right||red pipe cleaner
both hands bend the red pipe-cleaner tip|bend|red pipe cleaner|||both||red pipe cleaner
both hands thread buttons onto the red pipe cleaner|thread|button|red pipe cleaner||both||red pipe cleaner
both hands thread a button onto a blue pipe cleaner|thread|button|blue pipe cleaner||both|button|blue pipe cleaner
both hands secure buttons on the blue pipe cleaner|twist|blue pipe cleaner||button|both||blue pipe cleaner
both hands bend the gray pipe-cleaner tip|bend|gray pipe cleaner|||both||gray pipe cleaner
both hands secure buttons onto the gray pipe cleaner|thread|button|gray pipe cleaner||both||gray pipe cleaner
both hands thread a button onto another red pipe cleaner|thread|button|red pipe cleaner||both|button|red pipe cleaner
both hands secure the button on the red stem|twist|red pipe cleaner||button|both||red pipe cleaner
both hands thread a button onto another blue pipe cleaner|thread|button|blue pipe cleaner||both|button|blue pipe cleaner
both hands secure the button on the blue stem|twist|blue pipe cleaner||button|both||blue pipe cleaner
both hands thread buttons onto another blue pipe cleaner|thread|button|blue pipe cleaner||both|button|blue pipe cleaner
both hands twist the blue stem around its button|twist|blue pipe cleaner||button|both||blue pipe cleaner
both hands thread a button onto a gray pipe cleaner|thread|button|gray pipe cleaner||both|button|gray pipe cleaner
both hands tighten the gray stem around its button|twist|gray pipe cleaner||button|both||gray pipe cleaner
both hands thread a white button onto another blue stem|thread|button|blue pipe cleaner||both|button|blue pipe cleaner
both hands add another button onto the blue stem|thread|button|blue pipe cleaner||both|button|blue pipe cleaner
both hands twist the stem beneath the stacked buttons|twist|blue pipe cleaner||button|both||blue pipe cleaner
both hands gather the button-flower stems into a bouquet|gather|bouquet|||both||bouquet
both hands wrap green paper around the bouquet|wrap|green paper||bouquet|both|bouquet|'''
groups=[(0,8,'Lay out stems and buttons','Pipe cleaners are placed on the table; individual buttons are selected and arranged beside them.','Provides the stems and flower-head pieces.'),(9,10,'Make the first red button flower','The red stem tip is bent, threaded through buttons, and twisted to retain the head.','Produces the first assembled flower.'),(11,12,'Make a blue button flower','Buttons are threaded onto a blue stem and the tip is bent and twisted around the head.','Adds a contrasting flower to the set.'),(13,14,'Make a gray button flower','A gray stem is selected, bent, threaded through buttons, and secured.','Adds another completed stem.'),(15,19,'Assemble further red and blue flowers','More stems receive button heads, with the pipe-cleaner tips tightened before each stem is set aside.','Expands the collection for the bouquet.'),(20,25,'Finish the remaining button flowers','The remaining gray and blue stems receive buttons, including stacked light and dark heads.','Completes the individual flowers before bundling.'),(26,27,'Gather and wrap the bouquet','The finished stems are brought together, their heads spread, and green paper folded around the bundle before display.','Turns separate stems into the finished handheld bouquet.')]
write(v,goal,['pipe cleaner','red pipe cleaner','blue pipe cleaner','gray pipe cleaner','button','button box','table','green paper','bouquet'],lines,groups,'All overview, 743 dense step frames, and 28 native endpoint frames reviewed. Fine boundaries preserved. Button threading details are sometimes finger-occluded; no unseen adhesive use inferred. Predictability awaits independent past-only testing.',evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/9186ff4997024eb1/20261106T075211458339Z/manifest.json')
