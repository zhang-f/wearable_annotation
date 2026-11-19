from build_pilot import *
craft();cook();curtain()
fixes={
'e531cded0108b6c3':{3:(['tape'],['tape']),5:(['tape'],['tape']),6:(['scissors'],[]),7:(['marker cap'],['marker'])},
'3a122ee7ff513956':{4:([],[]),6:(['cheese bag'],['cheese bag']),12:(['cheese bag'],['cheese bag']),23:([],['plate']),29:(['seasoning jar'],[]),38:(['salt shaker'],['salt shaker']),39:([],['salt shaker'])},
'0573fc312656e95a':{19:(['drill bit'],[]),21:(['drill'],['drill bit']),22:(['drill'],[]),41:(['drill'],['drill bit']),57:(['curtain hook'],[]),59:(['screwdriver'],['screw']),60:(['curtain hook','screwdriver'],[]),63:(['curtain hook','screwdriver'],['screw']),65:(['screwdriver'],['curtain hook'])}}
for v,changes in fixes.items():
 p=OUT/'videos'/f'{v}.json';d=json.loads(p.read_text())
 if v.startswith('e'): d['object_inventory'].append('marker cap')
 for i,(l,r) in changes.items():d['fine'][i]['in_hand_at_end']={'left':l,'right':r}
 if v.startswith('3'):
  x=d['fine'][39];x['boundary_note']='t=110.9–112.6s shake salt; still holds salt shaker immediately before t=113s.'
  x=d['fine'][40];x.update(summary='put down the salt shaker',verb='put down',object='salt shaker',target='counter',hands='both',type='action',boundary_note='t=113.0s close or regrasp shaker; t=113.3s put down; then pause until t=114.5s.',notes='Type changed from idle because closing and placing shaker are visible at start.')
 if v.startswith('057'):
  x=d['fine'][6];x.update(summary='remove the curtain hook from the wall',verb='remove',target='wall',in_hand_at_end={'left':['curtain hook'],'right':['curtain hook']},boundary_note='t=34–38s remove and inspect hook; t=40s put marker down, hook remains held at native t=40.667s; hook is placed on floor at t=41s in next segment.')
  x=d['fine'][30];x.update(summary='adjust the drill controls',verb='adjust',object='drill',tool=None,target=None,boundary_note='t=143–146s adjust drill controls; t=147–148.8s raise and inspect drill; wall drilling begins around t=149s in next segment.')
  x=d['fine'][63];x.update(summary='pick up another screw',verb='pick up',object='screw',hands='right',target=None,boundary_note='t=292–295s right hand reaches to floor, t=295.7–296.3s brings screw toward hook.',ambiguous=False)
  x=d['fine'][62];x.update(summary='reach for another screw',verb='reach for',object='screw',target=None,boundary_note='t=289.7–291.8s right hand releases hook and lowers toward screws on floor.',ambiguous=False)
 for i,x in enumerate(d['fine']):
  held=set(sum(d['fine'][i-1]['in_hand_at_end'].values(),[])) if i else set()
  x['transition_in']=None if not i else 'NONE' if x['type']=='idle' else 'STRONG' if x['object'] in held or x['tool'] in held else 'WEAK'
 for x in d['coarse']:x['transition_in']=d['fine'][x['fine_index_range'][0]]['transition_in']
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
