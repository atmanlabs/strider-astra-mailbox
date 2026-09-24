import play,json,time
c=play.Controller(seed=73)
positions=set();actions=set()
for n in range(450):
 a,done=c.step();actions.add(a);positions.add(tuple(map(int,c.info['player_pos'])))
 if done:break
achievements={k:v for k,v in c.info['achievements'].items() if v}
print(json.dumps({'steps':n+1,'positions':len(positions),'actions':sorted(actions),'achievements':achievements}))
assert len(positions)>5,'Movement not verified'
assert achievements.get('collect_wood',0)>0,'Gathering not verified'
assert achievements.get('place_table',0)>0,'Building not verified'
assert achievements.get('make_wood_pickaxe',0)>0,'Crafting not verified'
play.remember('Verified Crafter sandbox smoke test: '+json.dumps(achievements)+' across '+str(len(positions))+' positions. These are game achievements, not real-world skills.','smoke')
print((play.OUT/'memory-receipt.json').read_text())
