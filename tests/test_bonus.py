import sys
import io
import contextlib
import unittest
from pathlib import Path
from unittest.mock import patch
import urllib.error
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'evals'))
from bonus.tools import BonusTools, HOSTS, SCHEMAS
from grading import bonus_points, mechanical_checks

class BonusToolsTests(unittest.TestCase):
    def test_five_distinct_apis_and_six_tools(self):
        self.assertEqual(len(HOSTS), 5)
        self.assertEqual(len(set(HOSTS.values())), 5)
        self.assertEqual(len(SCHEMAS), 6)
        t=BonusTools()
        for provider in HOSTS:
            response=t.execute(f'get_{provider}_status',{})
            self.assertEqual(response['provider'],provider)
            self.assertIn('indicator',response['overall'])
    def test_pagination_preserves_timeline(self):
        t=BonusTools()
        first=t.execute('get_incident_details',{'provider':'vercel','incident_id':'sps6n39gm4sg'})
        second=t.execute('get_incident_details',{'provider':'vercel','incident_id':'sps6n39gm4sg','offset':first['next_offset']})
        self.assertEqual(first['total_updates'],7)
        self.assertEqual(first['next_offset'],2)
        self.assertTrue(any('93njd414rpbx' in x['body'] for x in second['updates']))
        self.assertTrue(set(x['created_at'] for x in first['updates']).isdisjoint(x['created_at'] for x in second['updates']))
    def test_bad_arguments_do_not_crash(self):
        t=BonusTools()
        for args in ({'provider':'vercel','incident_id':'x','offset':'one'}, {'provider':'vercel','incident_id':'x','limit':4}, {'provider':'vercel','incident_id':'x','offset':True}):
            self.assertEqual(t.execute('get_incident_details',args)['error'],'INVALID_ARGUMENTS')
        self.assertEqual(t.execute('get_npm_status',{'unexpected':'x'})['error'],'INVALID_ARGUMENTS')
    def test_transient_and_persistent_429(self):
        t=BonusTools(scenario='rate_limit_once')
        self.assertEqual(t.execute('get_vercel_status',{})['http_status'],429)
        self.assertEqual(t.execute('get_vercel_status',{})['provider'],'vercel')
        t=BonusTools(scenario='rate_limit_always')
        self.assertTrue(all(t.execute('get_vercel_status',{})['error']=='RATE_LIMITED' for _ in range(4)))
    def test_live_http_429_is_not_an_outage(self):
        err=urllib.error.HTTPError('https://example.invalid',429,'rate limited',{'Retry-After':'2'},io.BytesIO(b''))
        with patch('bonus.tools.urllib.request.urlopen',side_effect=err):
            result=BonusTools(mode='live').execute('get_npm_status',{})
        self.assertEqual(result['error'],'RATE_LIMITED')
        self.assertEqual(result['retry_after'],'2')
        err.close()
    def test_format_once_and_context_noise(self):
        t=BonusTools(scenario='format_once')
        args={'provider':'npm','incident_id':'cc0t2r4403sy'}
        self.assertEqual(t.execute('get_incident_details',args)['error'],'INVALID_ARGUMENTS')
        self.assertTrue(t.execute('get_incident_details',args)['ok'])
        self.assertEqual(len(BonusTools(scenario='noisy').execute('get_vercel_status',{})['distractors']),160)
    def test_min_max_calls_and_bonus_conversion(self):
        trace=[{'event':'tool','name':'get_vercel_status','step':i} for i in range(1,5)]
        checks=mechanical_checks({'max_calls':{'get_vercel_status':3}}, {'trace':trace,'answer':''})
        self.assertEqual(checks['score_cap'],50)
        self.assertEqual(bonus_points(80,True),12)
        self.assertIsNone(bonus_points(80,False))
        self.assertIsNone(bonus_points(None,True))

class BonusRunnerTests(unittest.TestCase):
    def test_bonus_points_only_for_full_run(self):
        import json, tempfile
        import run_evals
        from pathlib import Path
        def fake(case,args):
            return {'id':case['id'],'grade':{'score':80,'status':'scored'}}
        with tempfile.TemporaryDirectory() as td:
            outfile=str(Path(td)/'result.json')
            with patch.object(run_evals,'run_case',side_effect=fake), patch.object(sys,'argv',['run_evals.py','--bonus','--model','test','--output',outfile]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_evals.main(),0)
            report=json.loads(Path(outfile).read_text())
            self.assertEqual(report['summary']['bonus_points_0_15'],12)
            self.assertEqual(report['config']['dataset'],'bonus')
            with patch.object(run_evals,'run_case',side_effect=fake), patch.object(sys,'argv',['run_evals.py','--bonus','--case','B1','--model','test','--output',outfile]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_evals.main(),0)
            report=json.loads(Path(outfile).read_text())
            self.assertIsNone(report['summary']['bonus_points_0_15'])
    def test_main_dataset_remains_independent(self):
        import json, tempfile
        import run_evals
        from pathlib import Path
        with tempfile.TemporaryDirectory() as td:
            outfile=str(Path(td)/'result.json')
            with patch.object(run_evals,'run_case',return_value={'id':'E1','grade':{'score':90,'status':'scored'}}), patch.object(sys,'argv',['run_evals.py','--case','E1','--model','test','--output',outfile]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_evals.main(),0)
            report=json.loads(Path(outfile).read_text())
            self.assertEqual(report['config']['dataset'],'core')
            self.assertNotIn('bonus_points_0_15',report['summary'])

if __name__=='__main__': unittest.main()
