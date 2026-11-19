from write_editor_batch import *
v='c271543bd097924a'
goal=dict(title='Roll a pink paper bead and secure its thread',description='Position triangular paper and thread, roll the pink strip tightly into an elongated bead, glue down its tip and repeatedly loop and tighten thread beside the bead. The video continues with trimming and displaying the small threaded paper ornament after the source fine coverage ends.',final_state='A narrow pink rolled-paper bead hangs from a small thread loop; excess thread is trimmed and the ornament displayed after258.4s.',procedure=['Arrange the pink and teal triangular paper pieces and thread.','Roll the pink triangle into a narrow bead around the thread.','Apply glue and press the paper tip closed.','Adjust the thread and form successive loops beside the bead.','Pull the thread taut and tighten the small looped join.','Trim excess thread with scissors and display the ornament; this tail lacks source fine segments.'])
inv=['pink paper','teal paper','thread','glue bottle','paper bead']
lines='''both hands smooth triangular paper pieces on table|smooth|pink paper||teal paper|both||
right hand lifts thread then adjusts pink paper|adjust|thread||pink paper|both||
both hands align thread against pink paper edge|align|thread||pink paper|both||
both hands tightly roll pink paper around thread|roll|pink paper||thread|both|paper bead|paper bead
right hand picks up glue bottle beside paper bead|pick up|glue bottle|||right|paper bead|glue bottle
right hand applies glue to paper tip and lowers bottle|apply|paper bead|glue bottle||right|paper bead|
both hands press and roll glued paper tip closed|press|paper bead|||both|paper bead|paper bead
both hands release bead then rub fingertips together|rub|thread|||both||
left hand retrieves thread beside pink bead|take|thread|||left|thread|
both hands pinch thread beside the paper bead|pinch|thread||paper bead|both|paper bead|thread
both hands turn small thread loop beside bead|turn|thread||paper bead|both|paper bead|thread
left hand pinches thread while right steadies bead|pinch|thread||paper bead|both|thread|paper bead
left hand pulls thread end away from bead|pull|thread||paper bead|left|thread|paper bead
left hand lowers thread end then returns toward bead|move|thread||paper bead|left|thread|paper bead
both hands loop thread alongside paper bead|loop|thread||paper bead|both|thread|paper bead
both hands pinch and twist thread near bead|twist|thread||paper bead|both|paper bead|thread
right hand pulls thread end while left holds bead|pull|thread||paper bead|right|paper bead|thread
right hand brings thread end back toward bead|move|thread||paper bead|right|paper bead|thread
both hands pinch thread crossing beside bead|pinch|thread||paper bead|both|paper bead|thread
both hands wrap thread around the small crossing|wrap|thread||paper bead|both|paper bead|thread
both hands tighten thread loop beside paper bead|tighten|thread||paper bead|both|paper bead|thread
left hand pinches loop while right draws thread through|pull|thread||paper bead|both|thread|paper bead
right hand slides paper bead along the thread|slide|paper bead||thread|right|thread|paper bead
both hands pull thread ends around bead|pull|thread||paper bead|both|thread|paper bead
both hands stretch thread and lower paper bead|stretch|thread||paper bead|both|thread|thread
both hands spread long thread across the table|spread|thread|||both|thread|thread
right hand draws thread across tabletop|pull|thread|||right|thread|thread
right hand stretches thread while left pinches its end|stretch|thread|||both|thread|thread
left hand holds thread as right reaches back toward it|hold|thread|||both|thread|
both hands pinch thread ends together above table|pinch|thread|||both|thread|thread
right hand pulls thread upward through fingers|pull|thread|||right|thread|thread
both hands stretch thread with bead resting below|stretch|thread||paper bead|both|thread|thread
right hand draws thread taut across table|pull|thread|||right|thread|thread
right hand releases and returns toward thread|release|thread|||right|thread|
both hands adjust thread crossing on tabletop|adjust|thread|||both|thread|thread
both hands lay thread down then gather its loop|gather|thread|||both||thread
right hand lifts thread loop from table|lift|thread|||right||thread
both hands bring thread and paper bead upward|lift|thread||paper bead|both|paper bead|thread
both hands pinch thread crossing beside bead|pinch|thread||paper bead|both|paper bead|thread
right hand draws thread through loop beside bead|pull|thread||paper bead|right|paper bead|thread
right hand pulls thread upward while left holds bead|pull|thread||paper bead|right|paper bead|thread
both hands pinch and adjust thread loop|adjust|thread||paper bead|both|paper bead|thread
right hand threads loose end around loop|loop|thread||paper bead|right|paper bead|thread
both hands tighten small thread crossing near bead|tighten|thread||paper bead|both|paper bead|thread
both hands work thread through loop beside pink bead|pull|thread||paper bead|both|paper bead|thread
right hand pulls thread outward while left pinches join|pull|thread||paper bead|both|paper bead|thread
right hand returns loose thread end toward bead|move|thread||paper bead|right|paper bead|thread
both hands pinch and twist thread at bead end|twist|thread||paper bead|both|paper bead|thread
right hand draws thread through small loop|pull|thread||paper bead|right|paper bead|thread
right hand pulls thread away from paper bead|pull|thread||paper bead|right|paper bead|thread
left hand holds paper bead while right reaches aside|hold|paper bead|||left|paper bead|'''
groups=[(0,2,'Arrange paper and thread.','The two colored paper triangles are smoothed and thread brought across the pink paper edge.','Align the materials before rolling a threaded paper bead.'),(3,3,'Roll the pink paper into a bead.','Both hands repeatedly pinch and turn the pink triangle, winding it into a narrow tapered roll around the thread.','Form the pink paper body of the ornament.'),(4,6,'Glue and press the paper tip closed.','The glue bottle is picked up and used at the narrow paper tip; fingers press and roll the glued end.','Keep the rolled paper bead from unwinding.'),(7,24,'Adjust the thread and form a loop beside the bead.','Fingertips are rubbed, then the thread and bead repeatedly pinched, crossed, drawn through and tightened. The bead is lowered as the thread is stretched.','Secure and position the thread next to the paper bead.'),(25,36,'Spread and gather the long thread.','The thread is drawn across the table, its ends aligned, and a loose loop gathered and lifted again.','Arrange the remaining thread for the small looped attachment.'),(37,50,'Tighten the small thread loops beside the bead.','The bead is held up while thread ends pass around the crossing and are pulled repeatedly. The last annotated interval ends as the right hand reaches aside.','Finish tightening the threaded join; trimming and final display remain outside fine coverage.')]
fix={3:dict(boundary_note='18.8–135.8s is a long sustained roll of the pink triangle, with repeated regrips and thread adjustments; fine retained.'),5:dict(boundary_note='137.6–148.5s includes glue application around139–141s and145s, bottle placement around147s and return to paper.'),7:dict(boundary_note='166.4–170.2s includes release of bead, rubbing fingertips and return toward thread.'),50:dict(boundary_note='Fine ends258.4s before actual video end. Visible missing task tail: scissors cut thread around260–271s; bead/loop displayed273–280s and placed down282s. Requires additional fine coverage, not boundary stretching.')}
write(v,goal,inv,lines,groups,'Viewed all9 overview sheets, all1017 dense frames and all51 native endpoints. Only fine boundaries retained. Paper rolling and detailed thread manipulation described from images; exact knot topology is not asserted because fingertips obscure it. Fine coverage ends258.4s; task-related scissors trimming260–271s and final display273–280s remain unannotated. Predictability pending independent testing.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T224953732736Z/manifest.json'))
