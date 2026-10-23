import copy
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('director',ROOT/'scripts/director.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)

class DirectorTests(unittest.TestCase):
    def setUp(self):
        self.dna=d.read(ROOT/'assets/product-dna.json')
        self.brief=d.read(ROOT/'assets/task-brief.json')
    def test_structure_metadata_references(self):
        for name in ('README.md','SKILL.md','LICENSE','.gitignore','CHANGELOG.md','agents/openai.yaml'):
            self.assertTrue((ROOT/name).is_file(),name)
        text=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\nname: industrial-design-visual-director\ndescription: '))
        refs=re.findall(r'\]\((references/[^)]+)\)',text)
        self.assertEqual(len(refs),6)
        for ref in refs:self.assertTrue((ROOT/ref).is_file(),ref)
    def test_valid_invalid_data(self):
        self.assertEqual(d.validate_dna(self.dna),[])
        self.assertTrue(d.validate_dna(d.read(ROOT/'tests/fixtures/invalid-dna.json')))
        self.assertTrue(d.validate_dna({}))
        for field in self.dna:
            bad=copy.deepcopy(self.dna);del bad[field]
            self.assertTrue(d.validate_dna(bad),field)
    def test_hard_lock_conflicts(self):
        self.brief['allowed_changes']=[{'target':'wheel','attribute':'count','value':3}]
        self.assertTrue(d.validate_brief(self.brief,self.dna))
        self.dna['design_locks'][0]['allowed_change']='any'
        self.assertTrue(d.validate_dna(self.dna))
    def test_uncertain_hard_lock_rejected(self):
        for confidence in ('Inferred','Unknown'):
            self.dna['design_locks'][0]['confidence']=confidence
            self.assertTrue(d.validate_dna(self.dna))
    def test_conditional_authorization(self):
        lock=copy.deepcopy(self.dna['design_locks'][0]);lock.update(id='L3',attribute='cmf',level='Conditional')
        self.dna['design_locks'].append(lock)
        self.assertEqual(d.validate_brief(self.brief,self.dna),[])
        self.assertNotIn('L3',d.prompt(self.dna,self.brief).split('## Preserve')[1].split('## Allowed')[0])
        del self.brief['allowed_changes'][0]['authorization']
        self.assertTrue(d.validate_brief(self.brief,self.dna))
    def test_T01_T06_roles_and_routing(self):
        for case in d.read(ROOT/'tests/cases.json'):
            with self.subTest(case=case['id']):self.assertEqual(d.route(case['request']),case['expected_mode'])
        self.brief['reference_assets']=['A','C']
        text=d.prompt(self.dna,self.brief)
        self.assertEqual(self.dna['source_assets'][0]['role'],'target')
        self.assertEqual([a['role'] for a in self.dna['source_assets'][1:]],['cmf','scene'])
        for section in ('Target Image','Reference Images','Edit Objective','Preserve','Allowed Changes','Forbidden Changes','Output Requirements','Uncertainty'):
            self.assertIn('## '+section,text)
        self.assertIn('L1',text)
    def test_T02_scene_preserves_cmf(self):
        self.brief.update(task_type='scene_transfer',objective='仅替换背景',reference_assets=['C'],allowed_changes=[{'target':'scene','attribute':'background','value':'室内'}])
        lock=copy.deepcopy(self.dna['design_locks'][0]);lock.update(id='CMF',attribute='cmf',expected='原色')
        self.dna['design_locks'].append(lock)
        self.assertEqual(d.validate_brief(self.brief,self.dna),[])
        self.assertIn('CMF',d.prompt(self.dna,self.brief))
    def test_T03_wheel_scope(self):
        self.brief.update(task_type='local_edit',allowed_changes=[{'target':'wheel_arch','attribute':'coverage','value':'绝大部分包覆，仅露小部分'}])
        for attr,val in [('color','棕色'),('position','原位置')]:
            lock=copy.deepcopy(self.dna['design_locks'][1]);lock.update(id=attr,attribute=attr,expected=val)
            self.dna['design_locks'].append(lock)
        self.assertEqual(d.validate_brief(self.brief,self.dna),[])
        text=d.prompt(self.dna,self.brief)
        for val in ('棕色','原位置','coverage','L2'):self.assertIn(val,text)
    def test_T04_add_ports_preserve_holder(self):
        lock=copy.deepcopy(self.dna['design_locks'][1]);lock.update(id='cup',target='cup_holder',attribute='count',expected=1)
        self.dna['design_locks'].append(lock)
        self.brief.update(task_type='local_edit',allowed_changes=[{'target':'charging_port','attribute':'count','value':2}])
        self.assertEqual(d.validate_brief(self.brief,self.dna),[])
        self.assertIn('cup_holder',d.prompt(self.dna,self.brief))
        self.brief['allowed_changes'].append({'target':'cup_holder','attribute':'count','value':0})
        self.assertTrue(d.validate_brief(self.brief,self.dna))
    def test_T05_unknown_back_view(self):
        self.brief.update(task_type='view_consistency_review',uncertainty=['需补充 CAD/后视图；概念方案为非精确设计参考'])
        text=d.prompt(self.dna,self.brief)
        self.assertIn('非精确设计参考',text)
        self.assertIn('背面结构',text)
    def test_T07_fallback_outputs_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest=d.prepare(self.dna,self.brief,temp)
            self.assertFalse(manifest['actual_image_edit'])
            self.assertEqual(manifest['qa_status'],'NOT_TESTED')
            for name in manifest['files']:self.assertTrue((Path(temp)/name).exists())
            self.assertFalse((Path(temp)/'qa-report.md').exists())
            with self.assertRaises(ValueError):d.prepare(self.dna,self.brief,temp)
    def test_T08_QA_evidence_states(self):
        # This is a synthetic aggregation test, not image recognition.
        with tempfile.TemporaryDirectory() as temp:
            image=Path(temp)/'synthetic.svg';image.write_text('<svg/>')
            finding={'dimension':'components','status':'PASS','lock_id':'L2','violation':True,'reliable':True,'evidence':'SYNTHETIC: four versus three','reviewer':'unit-test'}
            self.assertEqual(d.assess(self.dna,image,[finding])['status'],'FAIL')
            finding['reliable']=False
            self.assertEqual(d.assess(self.dna,image,[finding])['status'],'REVIEW')
            finding['evidence']=''
            self.assertEqual(d.assess(self.dna,image,[finding])['status'],'NOT_TESTED')
            self.assertEqual(d.assess(self.dna,None,[finding])['status'],'NOT_TESTED')
            findings=[{'dimension':dim,'status':'PASS','reliable':True,'reviewer':'synthetic-test','evidence':'synthetic checked'} for dim in d.DIMENSIONS]
            self.assertEqual(d.assess(self.dna,image,findings)['status'],'PASS')
    def test_T09_refinement(self):
        self.brief.update(task_type='render_refinement',allowed_changes=[{'target':'image','attribute':'clarity','value':'提升'}],uncertainty=['补全细节尚未真实验证'])
        self.assertEqual(d.validate_brief(self.brief,self.dna),[])
        self.assertIn('尚未真实验证',d.prompt(self.dna,self.brief))
    def test_T10_missing_target(self):
        self.brief['target_asset']=None
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):d.prepare(self.dna,self.brief,temp)
            self.assertEqual(list(Path(temp).iterdir()),[])

if __name__=='__main__':unittest.main()
