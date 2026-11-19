from write_editor_batch import *
v='bc336f7581b8a9ed'
goal=dict(title='Make a yarn-wrapped clothespin figure',description='Separate and align wooden clothespin pieces, secure white yarn with hot glue, and wind a thick white body around the wood. Mark and paint the exposed head, tie a short yarn piece around the figure, then glue a blue paper hat onto the top.',final_state='A white yarn-wrapped wooden figure with a marked pale face and blue paper hat lies on the table.',procedure=['Separate and align the wooden clothespin pieces.','Anchor white yarn to the wood with hot glue.','Wind yarn repeatedly around the wooden body and glue the end.','Cut excess yarn and straighten the wrapped body.','Mark the face and brush light paint onto the head.','Cut and attach a short yarn piece, then add face details.','Glue the blue paper hat to the head and display the figure.'])
inv=['clothespin','metal spring','white yarn','glue gun','scissors','marker','marker cap','paintbrush','paint pot','blue paper hat']
lines='''both hands pick up and turn wooden clothespin|turn|clothespin|||both|clothespin|clothespin
both hands separate wooden pieces and metal spring|separate|clothespin||metal spring|both|clothespin|metal spring
right hand sets metal spring down beside clothespin|set down|metal spring|||right|clothespin|
both hands align the wooden clothespin pieces|align|clothespin|||both|clothespin|
right hand pulls white yarn and wraps it around clothespin|wrap|white yarn||clothespin|both|clothespin|white yarn
both hands adjust yarn around the wooden pieces|adjust|white yarn||clothespin|both|clothespin|white yarn
right hand reaches toward glue gun while left holds clothespin|reach|glue gun|||right|clothespin|
right hand applies hot glue along wooden clothespin|apply|clothespin|glue gun||right|clothespin|
right hand presses white yarn around glued clothespin|wrap|white yarn||clothespin|both|clothespin|white yarn
right hand applies more hot glue to clothespin|apply|clothespin|glue gun||right|clothespin|
both hands press yarn and turn the wooden pieces|press|white yarn||clothespin|both|clothespin|clothespin
right hand winds white yarn around clothespin body|wind|white yarn||clothespin|both|clothespin|white yarn
right hand pulls yarn and continues winding around body|wind|white yarn||clothespin|both|clothespin|white yarn
both hands rotate clothespin while winding white yarn|wind|white yarn||clothespin|both|clothespin|white yarn
both hands tighten and smooth the wrapped yarn body|smooth|white yarn||clothespin|both|clothespin|white yarn
right hand glues the yarn end onto clothespin|glue|white yarn|glue gun|clothespin|right|clothespin|
both hands press the glued yarn against body|press|white yarn||clothespin|both|clothespin|white yarn
right hand cuts excess yarn with scissors|cut|white yarn|scissors||right|clothespin|scissors
both hands straighten white yarn around wooden body|straighten|white yarn||clothespin|both||clothespin
right hand picks up marker beside wrapped figure|pick up|marker|||right||marker
both hands remove marker cap|uncap|marker||marker cap|both|marker cap|marker
right hand draws small marks on wooden head|draw|clothespin|marker||right|clothespin|marker
right hand adds marker marks to wooden head|draw|clothespin|marker||right|clothespin|
left hand holds and examines the marked figure|hold|clothespin|||left|clothespin|
right hand sets marker down beside scissors|set down|marker|||right|clothespin|
right hand picks up paintbrush from white board|pick up|paintbrush|||right|clothespin|paintbrush
right hand brings open paint pots toward figure|move|paint pot|||right|paint pot|paintbrush
right hand dips paintbrush into light paint|dip|paintbrush||paint pot|right|paint pot|paintbrush
both hands set paint pots down and retrieve figure|pick up|clothespin|||both|clothespin|paintbrush
right hand brushes light paint onto wooden head|paint|clothespin|paintbrush||right|clothespin|paintbrush
both hands set figure down and gather loose yarn|take|white yarn|||both|white yarn|white yarn
right hand cuts a short yarn piece with scissors|cut|white yarn|scissors||right|white yarn|scissors
right hand puts scissors down beside short yarn|set down|scissors|||right|white yarn|
both hands tie short yarn around wrapped figure|tie|white yarn||clothespin|both||
left hand picks up figure while right takes paintbrush|pick up|clothespin||paintbrush|both|clothespin|paintbrush
right hand brushes small details onto the figure head|paint|clothespin|paintbrush||right|clothespin|paintbrush
right hand sets paintbrush down beside figure|set down|paintbrush|||right|clothespin|
right hand picks up blue paper hat and positions it|position|blue paper hat||clothespin|right|clothespin|blue paper hat
right hand puts blue paper hat beside figure|set down|blue paper hat|||right|clothespin|
right hand applies hot glue onto figure head|apply|clothespin|glue gun||right|clothespin|
right hand presses blue paper hat onto glued head|press|blue paper hat||clothespin|right|clothespin|
both hands display figure then place it on table|place|clothespin|||both||'''
groups=[(0,3,'Separate and align the clothespin pieces.','The wood is turned, the metal spring removed and placed on the table, and the wooden pieces brought together.','Prepare the wooden frame for the figure.'),(4,10,'Attach the first yarn wraps with hot glue.','White yarn is pulled from the ball, wrapped around the wood, and held in place while the glue gun is used twice.','Anchor the yarn securely to the wooden frame.'),(11,18,'Build and finish the white yarn body.','The wood is rotated while many yarn loops accumulate. The end is glued, excess yarn cut and the wrapping smoothed.','Cover the central body in a thick white yarn layer.'),(19,24,'Mark the wooden head.','A blue-bodied marker is uncapped and used to make small dark marks on the exposed head, then set down.','Add the initial facial marks to the figure.'),(25,29,'Paint the exposed head.','A brush and small paint pots are brought forward; the brush is dipped into light paint and worked over the exposed wooden head.','Give the head a pale painted surface.'),(30,36,'Attach a short yarn piece and finish head details.','A short piece of yarn is cut and tied onto the figure. The figure is lifted and a brush adds small head details before being set aside.','Finish the small yarn and painted decorations.'),(37,41,'Glue on the blue hat and display the figure.','The hat is fitted and set aside, hot glue applied to the head, and the blue paper hat pressed into place. The figure is held up and laid down.','Complete the hat attachment and show the finished figure.')]
fix={4:dict(boundary_note='14.09–31s includes yarn pickup followed by winding and tightening, retained source interval.'),7:dict(boundary_note='Glue gun picked up around35–37s, applied38–45s and returned around46.5s within preserved interval.'),17:dict(boundary_note='137.8–147.74s includes yarn pulling, scissors pickup, cutting about145s and scissors lowering.'),29:dict(boundary_note='196.31–210.47s includes figure pickup followed by repeated brush strokes.'),39:dict(boundary_note='249.82–255.79s includes glue gun pickup, nozzle application and return before hat placement.'),41:dict(boundary_note='263.06–275.3s contains display followed by placement around273s and yarn touching at275s.')}
write(v,goal,inv,lines,groups,'Viewed all overview sheets, all969 dense frames and all42 native endpoint frames. Fine boundaries preserved. Coarse groups rebuilt from visible assembly and decoration; no unsupported task-specific identity added. Independent predictability pending.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T224918199113Z/manifest.json'))
