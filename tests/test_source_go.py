"""
Regress Go parser boundaries without executing inspected source.
Valid literals and loop grammar pass; compressed statements, invalid syntax,
missing headers and executable multiline data remain governed.
"""

import subprocess
import unittest
from unittest.mock import patch

from source_governance.go_source import inspect_go, parser_binary


HEADER = '// Explain this fixture.\n// No execution is authorized.\n'
PATTERN = r'(?://[^\n]*|(?s:/\*.*?\*/))'


class GoSourceTests(unittest.TestCase):
    def inspect(self, body):
        return inspect_go(HEADER + 'package fixture\n' + body, PATTERN)

    def test_failed_framework_gate_prevents_helper_compilation(self):
        rejected = subprocess.CompletedProcess([], 1, '', '')
        with patch('source_governance.go_source.subprocess.run', return_value=rejected) as commands:
            with self.assertRaisesRegex(ValueError, 'blocked by framework source gate'):
                parser_binary.__wrapped__()
        self.assertEqual(1, commands.call_count)
        self.assertIn('check_source_governance.py', str(commands.call_args))

    def test_composite_literals_are_data(self):
        count, issues = self.inspect('var values = []int{1, 2}\nvar empty = struct{}{}\n')
        self.assertEqual(3, count)
        self.assertEqual([], issues)

    def test_loop_clause_separators_are_grammar(self):
        _, issues = self.inspect('func run() {\nfor i := 0; i < 3; i++ {\nprintln(i)\n}\n}\n')
        self.assertEqual([], issues)

    def test_inline_function_body_fails(self):
        _, issues = self.inspect('func run() { println(1) }\n')
        self.assertTrue(any('block body' in issue for issue in issues))

    def test_two_statements_on_one_line_fail(self):
        _, issues = self.inspect('func run() {\nprintln(1); println(2)\n}\n')
        self.assertTrue(any('multiple statements' in issue for issue in issues))

    def test_if_initializer_remains_two_actions(self):
        _, issues = self.inspect('func run() {\nif ok := true; ok {\nprintln(ok)\n}\n}\n')
        self.assertTrue(any('multiple statements' in issue for issue in issues))

    def test_type_switch_binding_is_grammar(self):
        _, issues = self.inspect('func run(value any) {\nswitch typed := value.(type) {\ncase string:\nprintln(typed)\n}\n}\n')
        self.assertEqual([], issues)

    def test_raw_backslash_does_not_escape_delimiter(self):
        count, issues = self.inspect('var text = `\\`\nvar next = 1\n')
        self.assertEqual(3, count)
        self.assertEqual([], issues)

    def test_multiline_raw_string_counts_comment_lookalikes(self):
        count, issues = self.inspect('var text = `\n// literal data\n/* still data */\n`\n')
        self.assertEqual(5, count)
        self.assertEqual([], issues)

    def test_nonmatching_comments_remain_counted(self):
        count, _ = inspect_go(HEADER + 'package fixture\n', r'/\*.*?\*/')
        self.assertEqual(3, count)

    def test_missing_header_fails(self):
        _, issues = inspect_go('package fixture\n', PATTERN)
        self.assertTrue(any('header' in issue for issue in issues))

    def test_invalid_go_fails_without_partial_certification(self):
        with self.assertRaises(ValueError):
            self.inspect('var value = [\n')

    def test_line_directives_cannot_hide_physical_lines(self):
        count, _ = self.inspect('//line fabricated.go:1\nvar first = 1\n//line fabricated.go:1\nvar second = 2\n')
        self.assertEqual(3, count)

    def test_top_level_declarations_on_one_line_fail(self):
        _, issues = self.inspect('var first = 1; var second = 2\n')
        self.assertTrue(any('multiple statements' in issue for issue in issues))

    def test_package_and_declaration_on_one_line_fail(self):
        _, issues = inspect_go(HEADER + 'package fixture; var value = 1\n', PATTERN)
        self.assertTrue(any('multiple statements' in issue for issue in issues))

    def test_two_imports_on_one_line_fail(self):
        _, issues = self.inspect('import "fmt"; import "os"\n')
        self.assertTrue(any('multiple statements' in issue for issue in issues))

    def test_local_declaration_is_one_statement(self):
        _, issues = self.inspect('func run() {\nvar first = 1\nprintln(first)\n}\n')
        self.assertEqual([], issues)

    def test_init_is_parsed_never_executed(self):
        _, issues = self.inspect('func init() {\npanic("must never run")\n}\n')
        self.assertEqual([], issues)

    def test_401_line_executable_payload_is_counted(self):
        count, _ = self.inspect('var text = `\n' + 'payload\n' * 398 + '`\n')
        self.assertEqual(401, count)


if __name__ == '__main__':
    unittest.main()
