from write_editor_batch import *
v='ed3bb632400de4bf'
goal=dict(title='Adjust the mailbox mounting fasteners',description='Open a roadside mailbox and select a screwdriver bit from tools stored inside. Use a screwdriver and pliers around the lower side and underside mounting hardware, repeatedly changing grip and position through the hedge, then check the mailbox front and door.',final_state='The mailbox remains on its rusty metal support after its mounting fasteners are worked; the door is opened at the end.',procedure=['Open the mailbox and select a screwdriver bit.','Fit the bit to the screwdriver and close the mailbox door.','Work the first side mounting fastener with screwdriver and pliers.','Move to the opposite side and repeatedly turn the lower fastener.','Adjust underside mounting hardware with both tools.','Return to the side fastener, then check the mailbox door.'])
inv=['mailbox door','mailbox','bit holder','driver bit','screwdriver','pliers','mounting fastener']
lines='''both hands open mailbox and reach toward stored tools|open|mailbox door|||both||
right hand adjusts tools inside mailbox while left steadies rim|adjust|screwdriver|||both||
right hand selects a driver bit from holder|take|driver bit||bit holder|right||driver bit
both hands adjust driver bit beside open mailbox|adjust|driver bit||bit holder|both||driver bit
right hand lifts screwdriver from mailbox|take|screwdriver|||right||screwdriver
right hand brings screwdriver to side mounting fastener|position|mounting fastener|screwdriver||right||screwdriver
both hands select and fit another screwdriver bit|fit|driver bit||screwdriver|both||screwdriver
both hands seat driver bit in screwdriver shaft|fit|driver bit||screwdriver|both||screwdriver
right hand returns tools inside then closes mailbox door|close|mailbox door|||right||screwdriver
both hands take pliers and move to mailbox side|take|pliers|||both|pliers|screwdriver
both hands position screwdriver and pliers at mounting hardware|position|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
right hand turns screwdriver while left braces mounting fastener|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
both hands briefly hold tools at mailbox mounting point|hold|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
both hands regrip pliers beside mailbox support|regrip|pliers||mounting fastener|both|pliers|screwdriver
right hand turns screwdriver at side mounting fastener|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
both hands readjust tools under mailbox edge|adjust|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
both hands move tools around front toward opposite side|move|screwdriver||pliers|both|pliers|screwdriver
both hands place tools against opposite lower mounting point|position|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
right hand rotates screwdriver while left holds mounting hardware|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
right hand regrips and turns screwdriver at mounting point|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
right hand continues rotating screwdriver against braced fastener|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
both hands reposition tools around the mailbox edge|position|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
right hand resumes turning screwdriver at lower mounting point|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
right hand turns screwdriver through repeated short rotations|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
left hand braces hardware while right turns screwdriver again|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
right hand withdraws screwdriver as both hands change position|withdraw|screwdriver|||both|pliers|screwdriver
both hands move tools beneath mailbox beside rusty support|move|screwdriver||pliers|both|pliers|screwdriver
both hands work screwdriver and pliers at underside mounting hardware|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
right hand turns screwdriver at side while left braces hardware|turn|mounting fastener|screwdriver|pliers|both|pliers|screwdriver
both hands withdraw tools and regrip them beneath mailbox|regrip|pliers||screwdriver|both|screwdriver|pliers
both hands place tools at underside fastener near support|position|mounting fastener|screwdriver|pliers|both|screwdriver|pliers
both hands turn and regrip tools beneath mailbox|turn|mounting fastener|screwdriver|pliers|both|screwdriver|pliers
left hand turns screwdriver while right braces hardware with pliers|turn|mounting fastener|screwdriver|pliers|both|screwdriver|pliers
both hands withdraw tools and touch mailbox front|touch|mailbox|||both|screwdriver|pliers
both hands hold tools beside mailbox door before opening it|hold|mailbox door|||both|screwdriver|pliers'''
groups=[(0,9,'Select tools and fit the screwdriver bit.','The mailbox door opens, tools and driver bits are handled inside, a bit fitted to the screwdriver, and pliers taken before the door closes.','Prepare the tools for the mailbox mounting hardware.'),(10,16,'Work the first side mounting point.','The screwdriver and pliers are held against opposite sides of a mounting fastener, with repeated turns and regrips before changing position.','Adjust the accessible fastener on the first side of the mailbox.'),(17,25,'Work the opposite lower side mounting point.','The tools move around the mailbox edge and the screwdriver makes many short rotations while the other hand braces the hardware.','Adjust mounting hardware reached from the opposite side.'),(26,32,'Work underside hardware and revisit the side.','Both tools are repositioned under the mailbox near the rusty support, then moved along the side and back beneath the box, with vegetation obscuring parts of the contact.','Continue adjustment around the underside and remaining mounting points.'),(33,34,'Check the mailbox front and door.','The tools are withdrawn, both hands touch the mailbox front and the door starts to open just after source fine coverage.','Check the mailbox body and door after working the mounting hardware.')]
fix={6:dict(boundary_note='16.7–23.7s includes holder pickup, bit selection and return/bit fitting.'),12:dict(boundary_note='41.8–41.83s is shorter than one15fps frame; native endpoint41.8s repeats the same tool contact, no independent change visible.',confidence='low',ambiguous=True),17:dict(confidence='medium',notes='Mailbox body occludes tool contact during much of57–61s; tool regrip and return to visible lower hardware are clear.'),32:dict(confidence='medium',notes='Dense leaves obscure exact fastener during141–152s. Visible screwdriver rotation and opposing pliers grip support generic hardware action only.'),34:dict(boundary_note='Fine ends155.37s; door opens155.5–156s and both hands continue touching/adjusting front through159s. Task-related tail lacks source fine coverage.',confidence='medium')}
write(v,goal,inv,lines,groups,'Viewed all5 overview sheets, all602 dense frames and all35 native endpoints. Fine times retained. Screwdriver/pliers rotations are visible but thread direction and successful tightening versus loosening cannot be established, so description says adjustment. Significant body/leaf occlusion recorded locally. Last source fine ends155.37s before visible door opening and front handling through159s. Independent predictability pending.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T225145411714Z/manifest.json'))
