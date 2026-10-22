"""Task V owner-transition and candidate packaging regressions.

Synthetic Git fixtures are infrastructure-only, never real research evidence.
"""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_static import validate_refs,RUNTIME_FILES
from simulate_merges import rehearse,owner_transitions
from validate_release_config import validate

class TaskVTests(unittest.TestCase):
    def fixture(self,directory,poison=False):
        root=Path(directory)
        def git(*args):
            return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',
                                            '-C',str(root),*args],stderr=subprocess.DEVNULL,text=True).strip()
        git('init','-q');git('config','user.name','W5 synthetic test');git('config','user.email','test@example.invalid')
        for path in ['specs/v2','data/v2','packages/core-v2','packages/models-v2','apps/web-v2','ops/v2']:
            (root/path).mkdir(parents=True);(root/path/'test.txt').write_text('original\n')
        git('add','.');git('commit','-qm','synthetic original');previous=git('rev-parse','HEAD')
        lock={'sources':{x:{'sha':previous} for x in ['w1','w2','w3','w4']}}
        (root/'ops/v2/integration-sources.json').write_text(json.dumps(lock));git('add','.');git('commit','-qm','synthetic base')
        base=git('rev-parse','HEAD')
        (root/'apps/web-v2/test.txt').write_text('new independent W4 source\n')
        if poison:(root/'index.html').write_text('forbidden Legacy source edit\n')
        git('add','.');git('commit','-qm','synthetic W4 owner source');source=git('rev-parse','HEAD')
        lock['sources']['w4']={'sha':source,'tree_sha':git('rev-parse',source+':apps/web-v2')}
        lock['owner_integrations']=[{'owner':'w4','previous_sha':previous,'source_sha':source,'paths':['apps/web-v2']}]
        (root/'ops/v2/integration-sources.json').write_text(json.dumps(lock));git('add','.');git('commit','-qm','synthetic W5 lock')
        return root,git,base,source,git('rev-parse','HEAD'),lock

    def test_independent_exact_w4_source_integrates_without_ref_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,git,base,source,candidate,lock=self.fixture(tmp);before=git('show-ref')
            result=rehearse(root,base,candidate)
            self.assertEqual(result['status'],'PASS');self.assertFalse(result['refs_changed'])
            self.assertFalse(result['deployment_allowed']);self.assertEqual(before,git('show-ref'))
            self.assertEqual(result['owner_trees']['apps/web-v2'],git('rev-parse',source+':apps/web-v2'))
            self.assertEqual(result['verified_owner_transitions'][0]['source_sha'],source)

    def test_w4_mutation_after_pinning_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,git,base,source,candidate,lock=self.fixture(tmp)
            (root/'apps/web-v2/test.txt').write_text('tampered\n');git('add','.');git('commit','-qm','bad edit')
            before=git('show-ref')
            with self.assertRaisesRegex(ValueError,'Owner subtree differs'):rehearse(root,base,git('rev-parse','HEAD'))
            self.assertEqual(before,git('show-ref'))

    def test_missing_duplicate_or_other_owner_declaration_is_rejected(self):
        for mutation in ['missing','duplicate','w1','wrong_path']:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as tmp:
                root,git,base,source,candidate,lock=self.fixture(tmp)
                if mutation=='missing':lock.pop('owner_integrations')
                if mutation=='duplicate':lock['owner_integrations']*=2
                if mutation=='w1':lock['owner_integrations'][0]['owner']='w1'
                if mutation=='wrong_path':lock['owner_integrations'][0]['paths']=['specs/v2']
                (root/'ops/v2/integration-sources.json').write_text(json.dumps(lock));git('add','.');git('commit','-qm','invalid lock')
                with self.assertRaises(ValueError):rehearse(root,base,git('rev-parse','HEAD'))

    def test_self_pin_and_nonisolated_owner_source_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,git,base,source,candidate,lock=self.fixture(tmp)
            lock['sources']['w4']['sha']=candidate;lock['owner_integrations'][0]['source_sha']=candidate
            with self.assertRaisesRegex(ValueError,'independent'):owner_transitions(root,base,candidate,lock)
        with tempfile.TemporaryDirectory() as tmp:
            root,git,base,source,candidate,lock=self.fixture(tmp,poison=True)
            with self.assertRaisesRegex(ValueError,'nonowner'):rehearse(root,base,candidate)

    def test_legacy_w1_w2_w3_edits_remain_forbidden(self):
        for path in ['index.html','specs/v2/test.txt','data/v2/test.txt','packages/core-v2/test.txt','packages/models-v2/test.txt']:
            with self.subTest(path=path),tempfile.TemporaryDirectory() as tmp:
                root,git,base,source,candidate,lock=self.fixture(tmp)
                (root/path).write_text('unauthorized new bytes\n');git('add','.');git('commit','-qm','nonowner mutation')
                with self.assertRaisesRegex(ValueError,'W5-only'):rehearse(root,base,git('rev-parse','HEAD'))

    def test_unrecognized_new_main_w4_tree_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,git,base,source,candidate,lock=self.fixture(tmp)
            git('checkout','--detach',base);(root/'apps/web-v2/test.txt').write_text('concurrent owner work\n')
            git('add','.');git('commit','-qm','new main owner bytes');newbase=git('rev-parse','HEAD')
            with self.assertRaisesRegex(ValueError,'neither the predecessor'):rehearse(root,newbase,candidate)

    def test_owner_ancestry_and_exact_transition_tree_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root,git,base,source,candidate,lock=self.fixture(tmp)
            wrong=copy.deepcopy(lock);wrong['sources']['w4']['tree_sha']='0'*40
            with self.assertRaisesRegex(ValueError,'tree pin mismatch'):owner_transitions(root,base,candidate,wrong)
            wrong=copy.deepcopy(lock);wrong['owner_integrations'][0]['previous_sha']=candidate
            with self.assertRaisesRegex(ValueError,'not an ancestor'):owner_transitions(root,base,candidate,wrong)

    def test_actual_runtime_closure_requires_catalog_state_file(self):
        root=Path(__file__).resolve().parents[3]
        files={name:(root/'apps/web-v2'/name).read_bytes() for name in RUNTIME_FILES}
        self.assertEqual(len(files),11);validate_refs(files)
        files.pop('catalog-state.mjs')
        with self.assertRaisesRegex(ValueError,'catalog-state.mjs'):validate_refs(files)

    def test_multiline_export_and_dynamic_dependencies_cannot_escape_package(self):
        for body in [b"import {\nvalue\n} from './missing.mjs';",b"export * from '../legacy.mjs';",b"export {value} from './missing.mjs';",b"import('./missing.mjs')",b"fetch('../legacy.json')"]:
            with self.subTest(body=body),self.assertRaises(ValueError):validate_refs({'index.html':b'<title>V2</title>','app.mjs':body})

    def test_real_workflows_are_readonly_non_deploying_and_new_manifest_complete(self):
        root=Path(__file__).resolve().parents[3];plan=json.loads((root/'ops/v2/deployment_plan.json').read_text())
        self.assertEqual(set(plan['runtime_files']),set(RUNTIME_FILES));self.assertEqual(len(plan['runtime_files']),11)
        for name,events in [('v2-integration.yml',None),('v2-release-readiness.yml',{'pull_request'}),('v2_public_preview_smoke.yml',None)]:
            flow=yaml.load((root/'.github/workflows'/name).read_text(),Loader=yaml.BaseLoader)
            result=validate(plan,flow,events);self.assertFalse(result['deployment_allowed'])

    def test_candidate_public_contract_requires_manifest_before_any_network(self):
        root=Path(__file__).resolve().parents[3];env=dict(os.environ,V2_PUBLIC_UI='forecast-home');env.pop('V2_EXPECTED_BUILD_MANIFEST',None)
        result=subprocess.run(['node','ops/v2/public_browser_smoke.mjs'],cwd=root,env=env,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('Candidate public smoke requires an exact build manifest',result.stderr)

if __name__=='__main__':unittest.main()
