"""Integration infrastructure regressions; these are not W2 research evidence."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_integration import parse_node, run_group, verified_copy


class RunnerTests(unittest.TestCase):
    def test_node_counts_are_test_cases(self):
        self.assertEqual(parse_node('# tests 22\n# pass 22\n# fail 0\n# skipped 0\n'),
                         {'tests': 22, 'pass': 22, 'fail': 0, 'skip': 0})

    def test_missing_or_duplicate_counts_fail(self):
        for text in ['ok 1 - file\n', '# tests 1\n# tests 2\n# pass 1\n# fail 0\n# skipped 0\n']:
            with self.assertRaises(ValueError):
                parse_node(text)

    def run_fixture(self, content, expected):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tests').mkdir()
            (root / 'logs').mkdir()
            (root / 'tests/test_sample.py').write_text(content)
            return run_group('regression', ['tests', 'test_sample.py'], root, root / 'logs',
                             dict(os.environ), expected, python=True)

    def test_skipped_suite_fails_even_with_exit_zero(self):
        result = self.run_fixture('import unittest\nclass T(unittest.TestCase):\n @unittest.skip("tool missing")\n def test_skipped(self): pass\n', 1)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['counts']['skip'], 1)
        self.assertEqual(result['counts']['pass'], 0)

    def test_empty_discovery_fails(self):
        result = self.run_fixture('import unittest\n', 0)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['counts']['tests'], 0)

    def test_failing_suite_preserves_count_and_log(self):
        result = self.run_fixture('import unittest\nclass T(unittest.TestCase):\n def test_failure(self): self.fail("deliberate infrastructure regression")\n', 1)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['counts']['fail'], 1)
        self.assertEqual(result['counts']['pass'], 0)

    def test_missing_or_modified_checkout_cannot_be_copied(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.mkdir()
            def git(*args):
                subprocess.run(['git', '-C', str(source), *args], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            git('init', '-q')
            git('config', 'user.name', 'Infrastructure regression')
            git('config', 'user.email', 'test@example.invalid')
            (source / 'input.txt').write_text('original infrastructure input\n')
            git('add', 'input.txt')
            git('commit', '-qm', 'test input')
            verified_copy(source, root / 'destination', 'input.txt')
            (source / 'input.txt').write_text('modified\n')
            with self.assertRaises(ValueError):
                verified_copy(source, root / 'destination', 'input.txt')
            (source / 'input.txt').unlink()
            with self.assertRaises(ValueError):
                verified_copy(source, root / 'destination', 'input.txt')


if __name__ == '__main__':
    unittest.main()
