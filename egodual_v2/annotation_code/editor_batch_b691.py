from write_editor_batch import *
v='b6919021874d152d'
goal=dict(title='Replace a small adhesive pad on a cabinet door',description='Pick residue from the inner lower corner of an open wooden cabinet door, dampen a towel at the sink and wipe the corner, then peel a small replacement pad from its backing, press it in place and check the door.',final_state='A small pad remains at the cleaned lower inside corner of the open cabinet door; hands have withdrawn.',procedure=['Pick away the old material at the lower inner corner while steadying the cabinet door.','Dampen a towel at the sink and wipe the mounting area, then dry it.','Peel the backing from a small adhesive pad and position it on the corner.','Press and hold the pad firmly, release it and move the door to inspect the repair.'])
inv=['cabinet door','adhesive residue','towel','faucet','sink','adhesive pad','backing paper','cutting board']
lines='''left hand picks residue from cabinet door while right steadies it|pick|adhesive residue||cabinet door|both||
left hand withdraws from cabinet while right carries towel|carry|towel|||right||towel
left hand wipes cabinet corner with damp towel after wetting it|wipe|cabinet door|towel||both|towel|
left hand lowers towel after wiping cabinet corner|lower|towel||cabinet door|left||
both hands peel backing paper from small adhesive pad|peel|backing paper||adhesive pad|both|adhesive pad|backing paper
left hand takes adhesive pad toward cabinet corner|move|adhesive pad||cabinet door|left|adhesive pad|
left hand holds pad beside cabinet door corner|hold|adhesive pad||cabinet door|left|adhesive pad|
left hand positions adhesive pad on cabinet door|position|adhesive pad||cabinet door|both||
left hand presses pad while right supports door|press|adhesive pad||cabinet door|both||
both hands press around the cabinet corner pad|press|adhesive pad||cabinet door|both||
right hand shifts grip while left holds pad against door|press|adhesive pad||cabinet door|both||
left hand maintains pressure on pad beneath right-held door|press|adhesive pad||cabinet door|both||
left hand holds pad firmly against cabinet corner|press|adhesive pad||cabinet door|both||
left hand continues pressing pad while right steadies door|press|adhesive pad||cabinet door|both||
left hand holds pressure on the fitted pad|press|adhesive pad||cabinet door|both||
left hand presses pad against lower door corner|press|adhesive pad||cabinet door|both||
left hand keeps pad pressed beneath right-held door|press|adhesive pad||cabinet door|both||
left hand holds pad in place at cabinet corner|press|adhesive pad||cabinet door|both||
left hand continues holding pressure on pad|press|adhesive pad||cabinet door|both||
left hand maintains pressure beneath cabinet door corner|press|adhesive pad||cabinet door|both||
left hand presses pad while right holds door still|press|adhesive pad||cabinet door|both||
left hand holds fitted pad against door|press|adhesive pad||cabinet door|both||
left hand continues pressing pad at cabinet corner|press|adhesive pad||cabinet door|both||
left hand maintains pressure before releasing the pad|press|adhesive pad||cabinet door|both||
left hand releases pad while right steadies cabinet door|release|adhesive pad||cabinet door|both||
right hand swings cabinet door while left checks lower corner|move|cabinet door|||both||
right hand moves cabinet door back outward|move|cabinet door|||right||
right hand releases cabinet door|release|cabinet door|||right||
idle (hands withdraw while the cabinet remains open)|||||none||
idle (view of repaired open cabinet door)|||||none||
idle (no further hand interaction)|||||none||'''
groups=[(0,1,'Remove old material from the cabinet corner.','The right hand steadies the open door while the left picks and rubs at the small lower inside corner fitting, then turns toward the sink with a towel.','Expose the mounting surface for the replacement pad.'),(2,3,'Clean and dry the cabinet mounting corner.','The towel is dampened at the faucet, used repeatedly on the lower corner, then another dry portion is rubbed over the surface.','Prepare a clean contact area for the adhesive pad.'),(4,6,'Peel the replacement pad from its backing.','A tiny pad and backing are separated between the fingers and the pad brought toward the cleaned corner.','Expose the adhesive surface and position the replacement.'),(7,24,'Apply and firmly hold the pad against the door.','The small pad is positioned at the corner, then sustained finger pressure is held while the other hand supports the door until the pad is released.','Seat the pad on the cleaned cabinet corner.'),(25,30,'Check the door and withdraw hands.','The door is swung slightly and its corner inspected before both hands withdraw, leaving the cabinet open.','Check that the applied pad remains attached.')]
fix={0:dict(confidence='medium',notes='Small round corner fitting/residue is visible, but its exact material cannot be determined. No screw removal is inferred.'),2:dict(boundary_note='Includes wetting towel at faucet around16–18s, wiping cabinet corner20–28s, and drying with folded towel32–36s.'),4:dict(confidence='medium',notes='Tiny transparent/light pad and backing are partially occluded. Exact product type is not visually identifiable.'),6:dict(confidence='medium',notes='Preserved 0.1s interval shows same pad positioning motion.'),11:dict(boundary_note='53.1–70.1s consists of sustained pressure on the same pad across fine11–23, without a clear new hand-object change at each one-second source boundary. Boundaries retained as requested.'),27:dict(confidence='medium',notes='Preserved 0.1s interval around hand withdrawal.'),30:dict(notes='Source fine stops77.9s; remaining2.167s shows cabinet and no new task interaction in overview.')}
write(v,goal,inv,lines,groups,'All overview, 446 dense frames and native endpoint sheets inspected. Fine boundaries unchanged. Many source one-second intervals divide a sustained pad press; descriptions intentionally preserve the visible continuous hold rather than invent repeated distinct repairs. Exact pad product/material uncertain, so canonical adhesive pad is used. No unobserved screwdriver, glue bottle or replacement knob action added.',fix,evidence_manifest=str(OUT/'frames_v2'/v/'20261106T224818038069Z/manifest.json'))
