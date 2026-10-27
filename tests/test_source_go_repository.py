"""
Verify Go checks apply equally to worktrees and staged repository content.
Common size, inventory and declaration rules stay active for the Go adapter.
"""

import unittest

import test_source_repository


GO_HEADER = '// Fixture source responsibility.\n// Parse only; never execute.\npackage fixture\n'


class GoRepositoryTests(unittest.TestCase):
    def setUp(self):
        fixture = test_source_repository.SourceRepositoryTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.config = fixture.config
        self.write = fixture.write
        self.write_config = fixture.write_config
        self.git = fixture.git
        self.inspect = fixture.inspect
        self.config['languages']['.go'] = {
            'adapter': 'go', 'comment_pattern': r'(?://[^\n]*|(?s:/\*.*?\*/))',
        }
        self.write_config()
        self.write('src/value.go', GO_HEADER + 'var values = []int{1, 2}\n')
        self.write('src/README.md', '- `module.py`: Python fixture.\n- `value.go`: Go fixture.\n')

    def test_go_staged_good_and_bad_layout(self):
        self.git('add', '.')
        self.assertEqual([], self.inspect(staged=True)[1])
        self.write('src/value.go', GO_HEADER + 'func run() { println(1) }\n')
        self.assertTrue(any('block body' in issue for issue in self.inspect()[1]))
        self.assertEqual([], self.inspect(staged=True)[1])
        self.git('add', '.')
        self.assertTrue(any('block body' in issue for issue in self.inspect(staged=True)[1]))

    def test_go_size_limit_retained(self):
        self.write('src/value.go', GO_HEADER + 'var text = `\n' + 'payload\n' * 398 + '`\n')
        self.assertTrue(any('401 code lines' in issue for issue in self.inspect()[1]))

    def test_go_inventory_retained(self):
        self.write('src/README.md', '- `module.py`: Python fixture.\n')
        self.assertTrue(any('missing description for value.go' in issue for issue in self.inspect()[1]))
