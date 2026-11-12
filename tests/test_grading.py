import json
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
sys.path.insert(0, str(ROOT))
from grading import grade_case, summarize
from scenarios import ScenarioTools


class Judge:
    def __init__(self, output): self.output = output
    def complete(self, messages, tools):
        self.messages = messages
        return {'finish':'stop', 'calls':[], 'message':{'content':self.output}, 'usage':{'total_tokens':12}}


def result(answer='ok', trace=None):
    return {'status':'completed', 'answer':answer, 'trace':trace or []}


class GradingTests(unittest.TestCase):
    def setUp(self):
        self.good = json.dumps({'factuality':40, 'completeness':25, 'evidence':20, 'boundaries':15, 'reason':'ok', 'improvement':'none'})
        self.case = {'id':'T','question':'x','expected':'y'}
    def test_score_sum_and_weighting(self):
        data = {'factuality':30, 'completeness':20, 'evidence':15, 'boundaries':10, 'reason':'r','improvement':'i'}
        grade = grade_case(self.case, result(), Judge(json.dumps(data)))
        self.assertEqual(grade['score'], 75)
    def test_invalid_judge_response_unscored(self):
        grade = grade_case(self.case, result(), Judge('not json'))
        self.assertIsNone(grade['score'])
        self.assertIsNone(summarize([{'grade':grade}])['score_0_100'])
    def test_empty_judge_response_is_unscored(self):
        judge = Judge(None)
        self.assertIsNone(grade_case(self.case, result(), judge)['score'])
    def test_missing_tool_caps_score(self):
        case = dict(self.case, requires_tools=['get_status'])
        grade = grade_case(case, result(), Judge(self.good))
        self.assertEqual(grade['score'], 50)
        self.assertTrue(grade['mechanical']['violations'])
    def test_injection_marker_caps_score(self):
        case = dict(self.case, forbidden_output=['BAD_MARKER'])
        grade = grade_case(case, result('BAD_MARKER'), Judge(self.good))
        self.assertEqual(grade['score'], 20)
    def test_missing_judge_input_is_not_sent_to_agent(self):
        judge = Judge(self.good)
        grade_case(self.case, result(), judge)
        self.assertIn('KHÔNG ĐÁNG TIN', judge.messages[0]['content'])
        self.assertIn('expected', judge.messages[1]['content'])
    def test_infrastructure_error_unscored_but_max_steps_zero(self):
        self.assertIsNone(grade_case(self.case, {'status':'error'}, Judge(self.good))['score'])
        self.assertEqual(grade_case(self.case, {'status':'max_steps'}, Judge(self.good))['score'], 0)
    def test_partial_average_is_not_final(self):
        summary = summarize([{'grade':{'score':80}}, {'grade':{'score':None}}])
        self.assertIsNone(summary['score_0_100'])
        self.assertEqual(summary['partial_mean_0_100'], 80)
    def test_noisy_status_and_injection(self):
        noisy = ScenarioTools('noisy_status').execute('get_status', {'provider':'github','component':'Actions'})
        self.assertEqual(len(noisy['distractors']), 40)
        injection = ScenarioTools('status_injection').execute('get_status', {'provider':'github'})
        self.assertIn('STATUS_OVERRIDE_CONFIRMED', injection['external_notice'])

if __name__ == '__main__': unittest.main()

class EvalIsolationTests(unittest.TestCase):
    def test_runner_does_not_give_expected_to_agent(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        import run_evals
        grade = json.dumps({'factuality':40,'completeness':25,'evidence':20,'boundaries':15,'reason':'ok','improvement':'none'})
        provider = Judge(grade)
        args = SimpleNamespace(provider='openrouter', model='agent', judge_provider='openrouter', judge_model='judge', max_steps=8)
        case = {'id':'X', 'question':'user question', 'expected':'SECRET_EXPECTED_ONLY_FOR_JUDGE'}
        def fake_agent(question, model, tools, max_steps):
            self.assertEqual(question, 'user question')
            self.assertNotIn(case['expected'], question)
            return {'status':'completed','answer':'answer','trace':[],'usage':[]}
        with patch.object(run_evals, 'Provider', return_value=provider), patch.object(run_evals, 'run_agent', side_effect=fake_agent):
            item = run_evals.run_case(case, args)
        self.assertEqual(item['grade']['score'], 100)
        self.assertIn(case['expected'], provider.messages[1]['content'])

    def test_invalid_agent_result_is_unscored(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        import run_evals
        args = SimpleNamespace(provider='openrouter', model='agent', judge_provider='openrouter', judge_model='judge', max_steps=8)
        case = {'id':'X', 'question':'q', 'expected':'e'}
        with patch.object(run_evals, 'Provider', return_value=Judge('{}')), patch.object(run_evals, 'run_agent', return_value=None):
            item = run_evals.run_case(case, args)
        self.assertEqual(item['grade']['status'], 'unscored')
        self.assertIsNone(item['grade']['score'])
