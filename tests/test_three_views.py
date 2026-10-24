import copy
import tempfile
from test_director import d, ROOT
import unittest


class ThreeViewTests(unittest.TestCase):
    def setUp(self):
        self.dna=d.read(ROOT/'assets/product-dna.json')
        self.brief=d.read(ROOT/'assets/three-view-brief.json')

    def test_single_image_is_conceptual(self):
        self.assertEqual(d.validate_brief(self.brief,self.dna),[])
        self.brief['view_plan']['accuracy']='source_constrained'
        self.assertTrue(d.validate_brief(self.brief,self.dna))

    def test_views_bound_to_structure_not_cmf(self):
        self.brief['view_plan']['views'][1]['target_asset']='A'
        self.assertTrue(d.validate_brief(self.brief,self.dna))

    def test_provided_views_require_distinct_assets(self):
        plan=self.brief['view_plan']
        plan.update(mode='provided_views',accuracy='source_constrained')
        self.assertTrue(d.validate_brief(self.brief,self.dna))
        for i,view in enumerate(plan['views']):
            source=copy.deepcopy(self.dna['source_assets'][0]);source.update(id='V'+str(i),path='synthetic/view'+str(i)+'.svg')
            self.dna['source_assets'].append(source)
            view['target_asset']=source['id']
        self.assertEqual(d.validate_brief(self.brief,self.dna),[])

    def test_cad_requires_cad_source_and_orthographic(self):
        plan=self.brief['view_plan'];plan.update(mode='cad_projection',accuracy='source_constrained')
        self.assertTrue(d.validate_brief(self.brief,self.dna))
        self.dna['source_assets'].append({'id':'MODEL','path':'synthetic/model.blend','role':'cad','source':'synthetic declared source; not executed'})
        self.brief['target_asset']='MODEL'
        for view in plan['views']:view['target_asset']='MODEL'
        self.assertEqual(d.validate_brief(self.brief,self.dna),[])
        plan['views'][0]['projection']='perspective'
        self.assertTrue(d.validate_brief(self.brief,self.dna))

    def test_missing_duplicate_and_malformed_views(self):
        for mutation in ('missing','duplicate','malformed'):
            brief=copy.deepcopy(self.brief)
            if mutation=='missing':brief['view_plan']['views'].pop()
            if mutation=='duplicate':brief['view_plan']['views'][1]['view']='front'
            if mutation=='malformed':brief['view_plan']['views'][1]=None
            self.assertTrue(d.validate_brief(brief,self.dna),mutation)

    def test_plan_preserved_without_false_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest=d.prepare(self.dna,self.brief,temp)
            self.assertEqual(manifest['view_plan'],self.brief['view_plan'])
            self.assertEqual(manifest['skill_version'],'1.1.0')
            self.assertFalse(manifest['actual_image_edit'])
            self.assertEqual(manifest['qa_status'],'NOT_TESTED')
            self.assertIn('顶部完整结构未确认',manifest['unverified'])
            self.assertIn('concept_reference',d.prompt(self.dna,self.brief))

    def test_simple_language_route(self):
        for request in ('做一套三视图','做正视、右侧视和俯视','给三视图白模统一上材质'):
            self.assertEqual(d.route(request),'view_consistency_review')


if __name__=='__main__':unittest.main()
