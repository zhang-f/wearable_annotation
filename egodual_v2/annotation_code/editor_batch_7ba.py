from write_editor_batch import *
v='7ba0ff671b9b7693'
goal=dict(title='Decorate a metal tumbler with three stickers',description='Rinse and repeatedly wipe a rose-gold tumbler, then peel and attach three precut quotation stickers around its exterior, smoothing each with fingers and a spoon.',final_state='Three stickers are pressed onto separate sides of the tumbler, which is inspected and set on the table.',procedure=['Rinse the tumbler under the faucet and dry its exterior with paper towels.','Handle the clear-liquid containers and wet a fresh towel before wiping the tumbler again.','Carry the tumbler to the craft table, select the first sticker, peel its backing and press it onto the cup.','Rub the first sticker with a spoon, then position, peel and apply the second sticker.','Apply the third purple sticker, smooth it with fingers and a spoon, and rotate the finished cup for inspection.'])
inv=['tumbler','faucet','paper towel','clear liquid jug','second jug','jug cap','small plastic cup','first sticker','second sticker','third sticker','sticker backing','spoon','table','counter']
lines='''left hand carries the tumbler to the sink|carry|tumbler||faucet|left|tumbler|
right hand turns on the faucet|turn on|faucet|||right|tumbler|
both hands rotate the tumbler under running water|rinse|tumbler||faucet|both|tumbler|
right hand closes the faucet and carries the tumbler aside|turn off|faucet|||right||
both hands tear paper towel from the roll|tear|paper towel|||both|paper towel|paper towel
right hand separates and folds the paper towel|fold|paper towel|||right||paper towel
right hand wipes the tumbler with paper towel|wipe|tumbler|paper towel||right||paper towel
both hands take fresh towel and wipe the tumbler|wipe|tumbler|paper towel||both|paper towel|
both hands open and reposition the clear-liquid jugs|open|clear liquid jug||second jug|both|clear liquid jug|jug cap
right hand tears a fresh paper towel|tear|paper towel|||right||paper towel
both hands wet and fold the paper towel|wet|paper towel||small plastic cup|both|paper towel|paper towel
right hand wipes the tumbler while left hand rotates it|wipe|tumbler|paper towel||right|tumbler|
right hand takes fresh towel and wipes the tumbler|wipe|tumbler|paper towel||right||paper towel
left hand wipes the tumbler base with paper towel|wipe|tumbler|paper towel||left|paper towel|tumbler
right hand carries the cleaned tumbler to the table|carry|tumbler||table|right||tumbler
right hand places the tumbler beside the stickers|place|tumbler||table|right||
both hands compare a sticker against the tumbler|position|first sticker||tumbler|both|first sticker|tumbler
both hands peel and press the first sticker onto the tumbler|attach|first sticker||tumbler|both|tumbler|
right hand rubs the first sticker with a spoon|rub|first sticker|spoon|tumbler|right|tumbler|spoon
right hand sets the spoon on the table|place|spoon||table|right|tumbler|
right hand reaches for the second sticker|pick up|second sticker|||right||
both hands compare the second sticker against the tumbler|position|second sticker||tumbler|both|tumbler|second sticker
both hands rotate the tumbler and test the second sticker placement|position|second sticker||tumbler|both|tumbler|second sticker
both hands peel backing from the second sticker|peel|second sticker||sticker backing|both|second sticker|second sticker
both hands attach and smooth the second sticker|attach|second sticker||tumbler|both|tumbler|
right hand smooths the second sticker with the spoon|rub|second sticker|spoon|tumbler|right|tumbler|
both hands rotate the tumbler and reach for another sticker|rotate|tumbler|||both||tumbler
both hands peel and attach the third purple sticker|attach|third sticker||tumbler|both|tumbler|
right hand rubs the third sticker with the spoon|rub|third sticker|spoon|tumbler|right|tumbler|spoon
both hands inspect the decorated tumbler and set it down|inspect|tumbler||table|both||'''
groups=[(0,7,'Rinse and dry the tumbler','The tumbler is carried to the sink, rotated under running water and repeatedly wiped with paper towels.','Provides a visibly rinsed and dried surface for decoration.'),(8,13,'Wipe the tumbler again with fresh towel','The clear-liquid containers are opened and handled; fresh paper towel is wetted, folded and used to wipe the tumbler body and base.','Completes surface preparation before stickers are applied.'),(14,18,'Apply and smooth the first sticker','The cleaned tumbler is returned to the table. A precut quotation sticker is compared with the cup, peeled, pressed onto its side and rubbed with a spoon.','Attaches the first decorative quotation to the tumbler.'),(19,25,'Apply and smooth the second sticker','The spoon is set aside while another sticker is selected and its position tested. Its backing is peeled, the sticker is pressed onto another side, and a spoon smooths it down.','Adds a second securely pressed quotation without covering the first.'),(26,29,'Apply the third sticker and inspect the cup','The cup is rotated, the purple sticker is peeled and attached, and fingers and a spoon smooth it. The decorated cup is rotated for inspection and set down.','Completes the three-sticker decoration and checks the final appearance.')]
fix={8:dict(ambiguous=True,confidence='medium',notes='At 55–68s two clear-liquid jugs/caps are handled beside a small cup; exact liquid identity and transfer are not reliably visible.'),7:dict(boundary_note='25.55–48.01s includes obtaining another towel and repeated wiping; source boundary preserved.'),17:dict(boundary_note='132.31–158.73s includes backing removal, positioning and finger smoothing; source boundary preserved.'),27:dict(boundary_note='227.01–259.91s includes sticker selection, backing removal, positioning and smoothing; source boundary preserved.')}
write(v,goal,inv,lines,groups,'Reviewed all overview, all 941 dense sampled frames and native end frames. One tumbler is repeatedly rotated, not multiple cups. Chemical identity is not inferred from jug appearance. Original fine boundaries retained; final 1.71s is unsegmented and shows the cup stationary on the table. Predictability awaits independent past-only testing.',fix=fix,evidence_manifest='/home/fan/google/review_run/annotation_v2/frames_v2/7ba0ff671b9b7693/20261106T060228067323Z/manifest.json')
