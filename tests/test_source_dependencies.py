"""Verify pinned upstream distributions without weakening authored-source checks.
Exercise exact identities, inventory, unlisted code and staged bytes in Git fixtures.
"""

import hashlib
import json
import unittest

import test_source_repository


class DependencySourceTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_source_repository.SourceRepositoryTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.payload = 'third_party=1; packed=2\n' * 401
        self.record = {
            'name': 'Upstream fixture', 'version': '1.2.3',
            'source': 'https://example.org/upstream/releases/1.2.3',
            'distribution': 'https://example.org/upstream/1.2.3/dist',
            'license': 'MIT',
            'files': {'bundle.py': 'sha256:' + hashlib.sha256(self.payload.encode()).hexdigest()},
        }
        self.fixture.config['vendored_dependencies'] = ['src/vendor/manifest.json']
        self.fixture.write_config()
        self.fixture.write('src/vendor/bundle.py', self.payload)
        self.fixture.write('src/vendor/README.md', '- `bundle.py`: Pinned upstream fixture distribution.\n')
        self.write_manifest()

    def write_manifest(self):
        self.fixture.write('src/vendor/manifest.json', json.dumps(self.record))

    def test_matching_distribution_passes_with_inventory(self):
        self.assertEqual([], self.fixture.inspect()[1])
        self.fixture.write('src/vendor/README.md', '# Vendor\n')
        self.assertTrue(any('missing description' in issue for issue in self.fixture.inspect()[1]))

    def test_changed_dependency_fails(self):
        self.fixture.write('src/vendor/bundle.py', self.payload + '# drift\n')
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            self.fixture.inspect()

    def test_unlisted_vendor_source_keeps_all_checks(self):
        self.fixture.write('src/vendor/owned.py', 'one=1; two=2\n' * 401)
        issues = '\n'.join(self.fixture.inspect()[1])
        self.assertIn('401', issues)
        self.assertIn('header', issues)
        self.assertIn('semicolon', issues)
        self.assertIn('missing description', issues)

    def test_bom_is_part_of_exact_identity(self):
        self.fixture.write('src/vendor/bundle.py', '\ufeff' + self.payload)
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            self.fixture.inspect()

    def test_staged_identity_is_independent_of_worktree(self):
        self.fixture.git('add', '.')
        self.fixture.write('src/vendor/bundle.py', 'changed\n')
        self.assertEqual([], self.fixture.inspect(staged=True)[1])
        self.fixture.git('add', '.')
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            self.fixture.inspect(staged=True)

    def test_missing_provenance_and_unsafe_paths_fail(self):
        del self.record['license']
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'license'):
            self.fixture.inspect()
        self.record['license'] = 'MIT'
        self.record['files'] = {'../module.py': 'sha256:' + '0' * 64}
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'stay beside'):
            self.fixture.inspect()

    def test_duplicate_or_malformed_manifest_selection_fails(self):
        for value in [['src/vendor/manifest.json'] * 2, [{}], 'src/vendor/manifest.json']:
            self.fixture.config['vendored_dependencies'] = value
            self.fixture.write_config()
            with self.assertRaises(ValueError):
                self.fixture.inspect()


if __name__ == '__main__':
    unittest.main()
