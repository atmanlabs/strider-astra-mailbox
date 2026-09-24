import sys,unittest,json
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,r'/REDACTED_LOCAL_PATH')
import semantic_practice as s
from conversation_policy import self_knowledge_action
from epistemic_dialogue import recall
class Tests(unittest.TestCase):
 def test_wrapped_note_is_decoded(self):
  self.assertEqual(s.clean_note('[remembered; supplied provenance=verified; sender=x] '+json.dumps('A blue mug.')),'A blue mug.')
 def test_negative_game_counts_not_claimed(self):
  text=s.clean_note('Crafter game experience only: '+json.dumps({'achievements':{'collect_wood':2,'make_iron_sword':0}}))
  self.assertIn('collected wood',text);self.assertNotIn('iron sword',text);self.assertNotIn('{',text)
 def test_metadata_never_fallback(self):
  with patch.object(s,'generate',side_effect=TimeoutError()):
   answer=s.synthesize('What happened?',['[remembered; sender=x] {"foo":1}'],'known')
  self.assertNotIn('sender',answer);self.assertNotIn('{',answer)
 def test_unsupported_summary_rejected(self):
  with patch.object(s,'generate',side_effect=[{'reply':'I became smarter.'},{'supported':False}]):
   self.assertNotIn('became smarter',s.synthesize('What changed?',['collected wood'],'known'))
 def test_missing_read_distinguished(self):
  result=recall(Path('no-such-memory-file.json'),{'query':'mug'})
  self.assertFalse(result['success']);self.assertEqual(result['data']['dialogue_act'],'inability')
 def test_partial_and_conflict_preserved(self):
  for state in ['partial','uncertain']:
   with patch.object(s,'generate',side_effect=[{'reply':"The note says blue, but I am not sure of the rest."},{'supported':True}]) as gen:
    result=recall(Path('unused'),{'query':'mug','question':'Color and size?'},records=[{'memory':'The mug is blue.'}],selector=lambda *args:(state,('The mug is blue.',)))
    self.assertEqual(result['data']['dialogue_act'],state)
    self.assertEqual(gen.call_args_list[0].args[1]['state'],state)
 def test_disclosure_rejects_false_history(self):
  with patch.object(s,'generate',side_effect=[{'reply':'You told me this yesterday.'},{'valid':False}]):
   self.assertNotIn('yesterday',s.acknowledge('I like painting.'))
 def test_structured_game_does_not_invent_chronology(self):
  with patch.object(s,'generate',side_effect=AssertionError('No creative filling of game logs')):
   answer=s.synthesize('What happened?',['The Crafter game log records that I collected wood, made a wooden pickaxe, woke up.'],'known')
  self.assertIn('wooden pickaxe',answer);self.assertNotIn('before',answer);self.assertNotIn('you collected',answer)
 def test_legacy_game_format(self):
  text=s.clean_note('Crafter game experience only: Verified Crafter sandbox smoke test: {"collect_wood":34,"make_wood_pickaxe":1} across 93 positions.')
  self.assertIn('made a wooden pickaxe',text);self.assertNotIn('{',text)
 def test_learning_overview_is_partial_not_proven_learning(self):
  result=recall(Path('unused'),{'query':'Crafter','question':'What did you learn?','recall_mode':'learning'},records=[{'memory':'Crafter game experience only: {"achievements":{"collect_wood":1}}'}])
  self.assertEqual(result['data']['dialogue_act'],'partial');self.assertIn('do not establish',result['output'])
 def test_self_knowledge_handoff_retains_learning_mode(self):
  action=self_knowledge_action({'conversation_intent':'self_knowledge','self_topic':'memory_search','query':'Crafter','recall_mode':'learning'},'Explain what you learned')
  self.assertEqual(action['args']['recall_mode'],'learning')
if __name__=='__main__':unittest.main()
