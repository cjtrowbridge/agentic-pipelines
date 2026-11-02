"""
Verify repository source, documentation and staged-snapshot gates.
Create isolated Git fixtures and invoke the installed checker/build wrapper.
No network, production repositories or candidate source execution is involved.
"""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml

from source_governance.checker import check
from source_governance.snapshot import Snapshot


FRAMEWORK = Path(__file__).resolve().parents[1]
HEADER = '"""\nModule responsibilities and interfaces.\nNo side effects.\n"""\n'


class SourceRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git('init', '-q')
        source = yaml.safe_load((FRAMEWORK / 'api.sample.yaml').read_text(encoding='utf-8'))['code']
        self.config = {
            'max_lines': 400, 'roots': ['src'],
            'languages': {'.py': source['languages']['.py']},
        }
        self.write_config()
        self.write('src/module.py', HEADER + 'value = 1\n')
        self.write('src/README.md', '# Source\n\n- `module.py`: Holds a test value.\n')

    def git(self, *args, check=True):
        return subprocess.run(
            ['git', '-C', str(self.root), *args], capture_output=True, text=True, check=check,
        )

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def write_config(self):
        self.write('api.sample.yaml', yaml.safe_dump({'code': self.config}))

    def inspect(self, staged=False):
        return check(Snapshot(self.root, staged))

    def invoke(self, script, *args):
        return subprocess.run(
            [sys.executable, str(FRAMEWORK / 'scripts' / script), '--repo-root', str(self.root), *args],
            capture_output=True, text=True, timeout=20,
        )

    def test_good_tree_and_limit_violation(self):
        self.assertEqual([], self.inspect()[1])
        self.write('src/module.py', HEADER + 'value = 1\n' * 401)
        self.assertTrue(any('401' in issue for issue in self.inspect()[1]))

    def test_source_outside_root_and_missing_language(self):
        self.write('outside.py', HEADER)
        self.write('src/other.go', 'package example\n')
        findings = '\n'.join(self.inspect()[1])
        self.assertIn('outside declared', findings)
        self.assertIn('no configured language', findings)

    def test_nested_directory_requires_inventory(self):
        self.write('src/nested/tool.py', HEADER)
        self.assertTrue(any('src/nested: missing README' in issue for issue in self.inspect()[1]))

    def test_ignored_source_inside_root_still_blocks_build(self):
        self.write('.gitignore', 'src/generated.py\n')
        self.write('src/generated.py', HEADER + 'value = 1\n' * 401)
        self.assertTrue(any('generated.py: 401' in issue for issue in self.inspect()[1]))

    def test_empty_worktree_directory_requires_readme(self):
        (self.root / 'src/empty').mkdir()
        self.assertTrue(any('src/empty: missing README' in issue for issue in self.inspect()[1]))

    def test_inventory_missing_and_stale_entries(self):
        self.write('src/README.md', '# Source\n\n- `gone.py`: Stale file.\n')
        findings = '\n'.join(self.inspect()[1])
        self.assertIn('missing description for module.py', findings)
        self.assertIn('stale inventory entry gone.py', findings)

    def test_root_escape_and_weakened_cap_fail(self):
        for root in ('../src', '.', 'src/nested'):
            self.config['roots'] = [root]
            self.write_config()
            with self.assertRaises(ValueError):
                self.inspect()
        self.config['roots'] = ['src']
        self.config['max_lines'] = 401
        self.write_config()
        with self.assertRaisesRegex(ValueError, 'must be 400'):
            self.inspect()

    def test_local_api_configuration_is_not_source_policy(self):
        self.write('api.yaml', yaml.safe_dump({'code': self.config, 'authentication': {'api_key': 'SECRET'}}))
        self.assertEqual([], self.inspect()[1])
        self.write('api.yaml', 'code: {}\n')
        self.assertEqual([], self.inspect()[1])
        self.write('source-governance.yaml', yaml.safe_dump({'code': self.config}))
        (self.root / 'api.sample.yaml').unlink()
        self.git('rm', '--cached', '--ignore-unmatch', 'api.sample.yaml')
        self.assertEqual([], self.inspect()[1])

    def test_valid_index_is_independent_of_invalid_worktree(self):
        self.git('add', '.')
        self.write('src/module.py', HEADER + 'value = 1\n' * 401)
        self.assertEqual([], self.inspect(staged=True)[1])
        self.assertTrue(self.inspect()[1])

    def test_invalid_index_cannot_be_hidden_by_valid_worktree(self):
        self.write('src/module.py', HEADER + 'value = 1\n' * 401)
        self.git('add', '.')
        self.write('src/module.py', HEADER + 'value = 1\n')
        self.assertTrue(self.inspect(staged=True)[1])
        self.assertEqual([], self.inspect()[1])

    def test_staged_symlink_is_rejected_without_following(self):
        self.git('add', '.')
        blob = self.git('hash-object', '-w', 'api.sample.yaml').stdout.strip()
        self.git('update-index', '--add', '--cacheinfo', f'120000,{blob},src/link.py')
        self.assertTrue(any('symlink' in issue for issue in self.inspect(staged=True)[1]))

    def test_invalid_source_blocks_build_command(self):
        self.write('src/module.py', HEADER + 'value = 1\n' * 401)
        marker = self.root / 'build-ran'
        result = self.invoke('governed_build.py', '--', sys.executable, '-c', 'from pathlib import Path; Path("build-ran").touch()')
        self.assertNotEqual(0, result.returncode)
        self.assertFalse(marker.exists())
        self.assertIn('blocked', result.stderr)

    def test_passing_gate_runs_build_and_preserves_failure(self):
        result = self.invoke('governed_build.py', '--', sys.executable, '-c', 'raise SystemExit(7)')
        self.assertEqual(7, result.returncode)
        self.assertIn('executing command', result.stdout)

    def test_extensionless_source_launcher_fails(self):
        self.write('src/run', '#!/bin/sh\necho run\n')
        self.assertTrue(any('source launcher needs a configured language extension' in issue for issue in self.inspect()[1]))

    def test_source_validation_does_not_require_a_pipeline(self):
        self.assertNotIn('build_pipelines', self.config)
        self.assertEqual([], self.inspect()[1])
