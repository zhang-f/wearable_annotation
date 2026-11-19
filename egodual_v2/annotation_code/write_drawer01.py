from batch01_builder import *
v='0af87fb5405568e9';H='drawer handle';D='drawer';S='drawer handle screw';K='black screwdriver';B='blue screwdriver'
r=[
row('pull the drawer open','open',D,hands='right',right=[H]),
row('turn the drawer handle screw with the left fingers','turn',S,hands='left',right=[H]),
row('turn the drawer handle screw with the left fingers','turn',S,hands='left',right=[H],note='t=3–11s repeated finger turning; cut at6.86s interrupts the same fastener adjustment.'),
row('reach for the black screwdriver','reach for',K,hands='right',right=[K]),
row('pick up the black screwdriver','pick up',K,hands='right',right=[K]),
row('turn the drawer handle screw with the black screwdriver','turn',S,tool=K,left=[K],right=[K]),
row('move the black screwdriver onto the desk','move',K,target='desk',hands='right',right=[K]),
row('put down the black screwdriver on the desk','put down',K,target='desk',hands='right',right=[B],note='t=25.6–26.2s release black screwdriver; t=26.267s grasp blue screwdriver. Tool change crosses this short interval.'),
row('pick up the blue screwdriver','pick up',B,hands='right',right=[B]),
row('position the blue screwdriver against the drawer handle screw','position',B,target=S,left=[B],right=[B]),
row('turn the drawer handle screw with the blue screwdriver','turn',S,tool=B,hands='left',left=[B]),
row('reposition the blue screwdriver at the drawer handle screw','position',B,target=S,hands='left',left=[B]),
row('turn the drawer handle screw with the blue screwdriver','turn',S,tool=B,hands='left',left=[B],right=[H]),
row('withdraw the blue screwdriver from the drawer handle screw','remove',B,target=S,hands='left',left=[B],right=[H]),
row('transfer the blue screwdriver to the right hand','transfer',B,hands='both',right=[B]),
row('turn the drawer handle screw with the blue screwdriver','turn',S,tool=B,hands='right',right=[B]),
row('put down the blue screwdriver on the desk','put down',B,target='desk',hands='right',note='t=60.6–61.3s withdraw screwdriver; t=61.8–62.3s place on desk. Both motions retained in human interval.'),
row('push the drawer closed by its handle','close',D,hands='right',right=[H]),
row('pull the drawer open by its handle','open',D,hands='right',right=[H]),
row('push the drawer closed by its handle','close',D,hands='right',right=[H]),
row('pull the drawer open by its handle','open',D,hands='right',right=[H]),
row('push the drawer closed by its handle','close',D,hands='right',right=[H]),
row('pull the drawer open by its handle','open',D,hands='right',right=[H]),
row('push the drawer closed by its handle','close',D,hands='right',right=[H]),
row('pull the drawer open by its handle','open',D,hands='right',right=[H]),
row('push the drawer closed by its handle','close',D,hands='right',right=[H]),
row('pull the drawer open by its handle','open',D,hands='right',right=[H],note='t=77.8s pull open; t=78.8–80s drawer remains open while right hand holds knob.'),
row('push and pull the drawer by its handle','move',D,hands='right',right=[H],note='t=81.3–81.8s push closed; t=83.6–84.2s pull open. Interval contains both drawer directions.'),
row('turn the drawer handle screw with the left fingers','turn',S,hands='left',right=[H]),
row('push the drawer closed by its handle','close',D,hands='right',right=[H]),
row('release the drawer handle','release',H,hands='right')]
p=[(0,11.1,'Pull the desk drawer outward. Hold the outside handle with the right hand while reaching inside with the left and repeatedly turning the inside fastener with fingertips.'),(11.1,26.35,'Reach onto the desk for a black-handled screwdriver, carry it to the open drawer, seat its tip against the inner handle screw and rotate it using both hands. Withdraw it and return it to the desktop.'),(26.35,62.78,'Pick up the slimmer blue-handled screwdriver and position it at the same inside drawer-front fastener. Rotate it repeatedly with the left hand while stabilizing it, briefly withdraw and reposition it, transfer it into the right hand and continue turning. Withdraw the tool and set it on the desk.'),(62.78,89.6,'Grip the outer knob with the right hand and repeatedly push the drawer closed and pull it open, leaving it open briefly between trials. Reach inside with the left hand for a final fingertip turn on the handle screw while the right holds the knob. Close the drawer and release it.')]
g=[(0,2,'Inspect and adjust the drawer handle by hand','Open the drawer, hold the outside handle and repeatedly turn its inside fastener using the left fingers.','Exposes the loose handle attachment and makes an initial manual adjustment.'),(3,7,'Tighten the handle screw with the black screwdriver','Fetch the black-handled screwdriver, seat it against the inside handle screw, turn it using both hands, then withdraw it and return it to the desk.','Adjusts the screw securing the handle to the drawer front.'),(8,16,'Adjust the screw with the blue screwdriver','Pick up the blue screwdriver, align it against the fastener, turn it repeatedly with the left hand, reposition and change hands, continue turning with the right, then return the tool to the desk.','Continues fastening with a different screwdriver until the tool work is finished.'),(17,30,'Check drawer movement and handle stability','Repeatedly close and open the drawer by the knob, hold it open for a final fingertip adjustment inside, close it and release the knob.','Checks whether the adjusted handle remains attached during repeated drawer movement.')]
finish(v,['Tighten and check a desk drawer handle','Open a desk drawer, adjust the inner handle fastener by hand and with two screwdrivers, then repeatedly operate the drawer by the knob and make a final fingertip adjustment.','The drawer is closed and the hands have released the knob. The handle remains attached throughout repeated opening and closing; its actual fastening torque cannot be measured visually.'],p,[H,D,S,K,B,'desk'],r,g,'Only human fine boundaries retained. All descriptions and coarse groupings independently rewritten from frames. Left and right gray-sleeved hands belong to the wearer; the large foreground left hand is not treated as another person. The same screw area is worked repeatedly; the obscured tip prevents a reliable clockwise/counterclockwise or second-screw assertion, so descriptions say turn. Drawer handle is recorded held only while gripped; no detached screws are inferred. Native PTS burnt before resampling. All dense pages and31 native end frames inspected.')
