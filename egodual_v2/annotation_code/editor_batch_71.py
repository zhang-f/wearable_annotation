from write_editor_batch import *
write('71da88e7ebab3c49',dict(title='Make a gold paper bookmark with floral decoration',description='Flatten a strip of gold paper over a notebook and fold its ends to size it. Cut away the excess with scissors, fold both long edges inward and crease the strip flat. Sketch a flower and curved stem in pencil, then trace them with a blue marker. Peel several small floral stickers from their clear backing and press them along the stem. Lay the decorated strip on the notebook, cover it with overlapping pieces of wide transparent tape and smooth the surface. Trim excess tape around the strip with scissors, lift the finished bookmark and set it down.',final_state='A narrow gold bookmark with a blue flower outline and small floral stickers lies on the notebook beneath a shiny transparent covering.',procedure=['Size and cut a rectangular gold paper strip.','Fold its long edges inward and flatten the bookmark blank.','Sketch and trace a flower and stem.','Peel and attach small floral stickers.','Cover the decorated strip with transparent tape.','Trim the excess tape and set down the finished bookmark.']),['gold paper','scissors','notebook','pencil','marker','marker cap','sticker sheet','floral sticker','tape roll','transparent tape','bookmark'],'''
idle: look over the craft materials|||||none||
flatten and fold the upper end of the gold paper|fold|gold paper|||both|gold paper|gold paper
fold the lower end of the gold paper|fold|gold paper|||both||gold paper
cut across the folded gold paper end|cut|gold paper|scissors||both|gold paper|scissors
trim the other end of the gold paper|cut|gold paper|scissors||both|gold paper|scissors
move the paper scraps aside|move|gold paper|||both|gold paper|
lay the gold paper strip flat|place|gold paper|||both||
turn the paper strip over on the table|turn|gold paper|||both||
fold one long paper edge inward|fold|gold paper|||both||
fold the other long edge inward and crease it|fold|gold paper|||both||
turn and flatten the folded gold strip|flatten|gold paper|||both||
pinch the short ends and smooth the paper folds|fold|gold paper|||both||
sketch a flower on the gold strip with pencil|draw|gold paper|pencil||right||pencil
finish the pencil stem and put down the pencil|draw|gold paper|pencil||right||
trace the flower and stem with the blue marker|draw|gold paper|marker||right|marker cap|marker
cap the marker and put it aside|close|marker|||both||
pick up the floral sticker sheet|pick up|sticker sheet|||both|sticker sheet|sticker sheet
peel a floral sticker and press it onto the strip|attach|floral sticker||gold paper|both||
peel and attach another small floral sticker|attach|floral sticker||gold paper|both||
peel more floral stickers and press them along the stem|attach|floral sticker||gold paper|both||
position the bookmark and pull out transparent tape|pull|transparent tape||tape roll|both|transparent tape|tape roll
lay transparent tape lengthwise over the bookmark|cover|bookmark|transparent tape||both|transparent tape|tape roll
cut the tape and smooth it onto the bookmark|cut|transparent tape|scissors|bookmark|both|tape roll|tape roll
pull another tape strip and press it over the bookmark|cover|bookmark|transparent tape||both|transparent tape|tape roll
pull out another length of tape|pull|transparent tape||tape roll|both|transparent tape|tape roll
cut the tape and smooth down the covered bookmark|cover|bookmark|transparent tape||both||
trim excess transparent tape along one bookmark edge|cut|transparent tape|scissors|bookmark|both|notebook|scissors
put the scissors down beside the notebook|put down|scissors|||right|notebook|
rotate the bookmark and trim another taped edge|cut|transparent tape|scissors|bookmark|both|notebook|scissors
finish trimming the tape around the bookmark|cut|transparent tape|scissors|bookmark|both|notebook|scissors
lift the finished bookmark and put it on the notebook|place|bookmark||notebook|both||
idle: move hands away from the finished bookmark|||||none||
''',[(0,5,'Size and trim the gold paper.','Flatten the gold strip over the notebook, fold its short ends to mark the length, cut away both excess ends and move the scraps aside.','Produce a rectangular paper blank for the bookmark.'),(6,11,'Fold and flatten the bookmark blank.','Turn the paper strip over, fold both long edges inward and pinch and smooth its ends and creases.','Make a narrower folded gold strip with neater edges.'),(12,15,'Draw the flower and stem.','Sketch the floral shape with pencil, then trace a blue flower outline and long curved stem with the marker before recapping it.','Create the large drawn decoration on the bookmark.'),(16,19,'Add small floral stickers.','Pick up a clear-backed sticker sheet and repeatedly peel small flower clusters, press them onto the gold strip and smooth their edges.','Add colored floral decoration around the drawn stem.'),(20,25,'Cover the decorated strip with transparent tape.','Position the strip on the notebook, pull lengths of wide transparent tape, cut them and press overlapping strips over the decorated paper.','Cover and hold the paper decoration beneath a transparent surface.'),(26,31,'Trim the tape and finish the bookmark.','Rotate and lift the work over the notebook, cut projecting tape around its edges and set the finished bookmark down.','Leave the decorated bookmark trimmed around its outline.')], 'Viewed all seven overview sheets, eleven dense contact sheets (697 frames) and two native endpoint sheets. At t=12–26s scissors trim paper ends; t=31–58s folds are creased; t=62–70s pencil sketch precedes blue tracing t=73–86s; t=94–132s floral stickers are peeled and pressed; t=137–168s tape is applied; t=172–191s tape edges are trimmed. Long source intervals combine peeling and placing stickers or drawing and changing tools; boundaries retained. The notebook serves as a support; the finished decorated strip is visibly lifted at t=191s.',fix={11:dict(boundary_note='The segment includes several end-fold and smoothing motions between 46.31s and 60.28s.'),17:dict(boundary_note='Peeling the sticker and placing it are both visible between 93.9s and 104.18s.'),18:dict(boundary_note='This interval includes peeling and attaching more than one small floral piece.'),19:dict(boundary_note='Several sticker peel-and-press cycles occur between 114.16s and 132.25s.'),20:dict(boundary_note='The interval changes from sticker smoothing to notebook positioning and tape retrieval.'),22:dict(ambiguous=True,confidence='medium',notes='The scissors are used near 150–151s, then released; final fingers appear to hold the tape roll.'),25:dict(boundary_note='The interval includes cutting tape, returning the roll and smoothing the covering.')} ,evidence_manifest=str(OUT/'frames_v2/71da88e7ebab3c49/20261106T060006026938Z/manifest.json'))
