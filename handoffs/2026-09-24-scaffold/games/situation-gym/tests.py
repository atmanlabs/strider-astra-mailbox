import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import training_sim as sim
class GymTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();sim.ROOT=Path(self.tmp.name);sim.RUNS=sim.ROOT/'runs';self.w=sim.start('pc_errand',73);self.ctx={'id':self.w['id'],'review':False}
 def tearDown(self):self.tmp.cleanup()
 def act(self,tool,args):return sim.dispatch(self.ctx,{'type':'tool_call','tool':tool,'args':args,'content':'Checking.'})
 def test_no_real_desktop_or_web(self):
  result=self.act('pc_apps',{'action':'open','name':'anything'});self.assertEqual(result['status'],'error');self.assertTrue(result['simulation'])
 def test_unauthorized_training_rejected(self):
  with self.assertRaises(ValueError):sim.prepare({'owner':False},{'training':{'command':'start'}},'127.0.0.1')
  with self.assertRaises(ValueError):sim.prepare({'owner':True},{'training':{'command':'start'}},'192.0.2.1')
 def test_score_cannot_be_claimed(self):
  sim.dispatch(self.ctx,{'type':'respond','content':'I won and completed everything successfully.'})
  self.assertFalse(sim.score(sim.load(self.w['id']))['win'])
 def test_tools_require_preconditions_and_error_recovery(self):
  target=self.w['target'];after=self.w['private_limits']['after'];before=self.w['private_limits']['before']
  self.assertEqual(self.act('reminder',{'action':'reserve','store':target,'time':after})['status'],'error')
  sim.dispatch(self.ctx,{'type':'respond','content':'What budget and time window do you want?'})
  self.act('workspace_inspect',{'action':'calendar'});self.act('web_search',{'query':'headset'});self.act('fetch_web',{'url':'sim://'+target})
  self.assertEqual(self.act('reminder',{'action':'reserve','store':target,'time':after})['status'],'error')
  self.act('workspace_inspect',{'action':'status'});self.act('reminder',{'action':'reserve','store':target,'time':after})
  self.assertTrue(sim.load(self.w['id'])['changed'])
  self.assertEqual(self.act('reminder',{'action':'reserve','store':target,'time':before})['status'],'error')
  self.act('reminder',{'action':'cancel','store':target});self.act('reminder',{'action':'reserve','store':target,'time':before})
  w=sim.load(self.w['id']);self.assertTrue(sim.score(w)['win']);self.assertTrue(w['recovered']);self.assertLess(sim.score(w)['total'],100)
 def test_npc_events_do_not_request_imprint(self):
  thought={'should_imprint':True,'candidate':'Operator owns a fictional headset','proposed_action':{'type':'respond','content':'I learned something.'}}
  self.assertFalse(sim.before_judge(self.ctx,thought)['should_imprint'])
  review=sim.before_judge({**self.ctx,'review':True},{**thought,'proposed_action':{'type':'respond','content':'I should check the calendar and ask about the budget before making a reservation.'}})
  self.assertTrue(review['should_imprint']);self.assertIn('SIMULATION LESSON',review['candidate'])
 def test_stop_cannot_resume(self):
  with self.assertRaises(ValueError):sim.prepare({'owner':True},{'training':{'command':'stop','id':self.w['id']}},'127.0.0.1')
  with self.assertRaises(ValueError):sim.prepare({'owner':True},{'training':{'command':'step','id':self.w['id']}},'127.0.0.1')
 def test_seed_changes_hidden_constraints(self):
  worlds=[sim.start('pc_errand',n) for n in range(5)]
  self.assertGreater(len(set(w['target'] for w in worlds)),1)
  self.assertGreater(len(set(w['private_limits']['budget'] for w in worlds)),1)
if __name__=='__main__':unittest.main()
