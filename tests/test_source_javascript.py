"""Regress JavaScript syntax boundaries using data-only parser inspection.
Literal syntax must pass while executable actions and physical size stay visible.
"""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from source_governance.javascript_source import inspect_javascript


HEADER = '// Governed JavaScript fixture.\n// Parse only; never execute inspected code.\n'
PATTERN = r'(?://[^\n]*|(?s:/\*.*?\*/))'


class JavaScriptSourceTests(unittest.TestCase):
    def inspect(self, body):
        return inspect_javascript(HEADER + body, PATTERN)

    def test_regex_template_arrow_and_object_are_valid(self):
        body = 'const pattern = /^artifact:\\/\\/sha256\\/[a-f0-9]{64}$/;\n'
        body += 'const mime = /^image\\/(png|jpeg)(;|$)/i;\n'
        body += 'const text = `${value} artifacts${count > 1 ? ` page ${count}` : ""}`;\n'
        body += 'const invalid = ids.some(id => typeof id !== "string");\n'
        body += 'const object = {first: 1, second: {value: 2}};\n'
        _, issues = self.inspect(body)
        self.assertEqual([], issues)

    def test_optional_chaining_and_loop_grammar_pass(self):
        body = 'const value = options.signal?.aborted;\nfor (let i = 0; i < 2; i++) {\ncall(i);\n}\n'
        self.assertEqual([], self.inspect(body)[1])

    def test_module_imports_and_exports_are_parsed_without_execution(self):
        body = 'import {value} from "./unavailable.js";\nexport function read() {\nreturn value;\n}\n'
        self.assertEqual([], self.inspect(body)[1])

    def test_multiple_statements_and_inline_body_fail(self):
        for body in ['a(); b();\n', 'if (ready) call();\n', 'const f = () => { call(); };\n']:
            self.assertTrue(self.inspect(body)[1], body)

    def test_embedded_assignments_fail(self):
        for body in ['if (ready = probe()) {\ncall();\n}\n', 'a = b = 1;\n', 'const value = (other = 2);\n']:
            self.assertTrue(any('assignment' in issue for issue in self.inspect(body)[1]))

    def test_template_actions_cannot_hide(self):
        _, issues = self.inspect('const value = `${(() => { a(); b(); })()}`;\n')
        self.assertTrue(issues)

    def test_literal_lines_count_and_comments_do_not(self):
        count, issues = self.inspect('const text = `\n' + '// literal data\n' * 399 + '`;\n')
        self.assertEqual(401, count)
        self.assertEqual([], issues)
        self.assertEqual(1, self.inspect('/*\ncomment\n*/\nconst text = 1;\n')[0])

    def test_header_and_syntax_fail_closed(self):
        self.assertTrue(inspect_javascript('const x = 1;\n', PATTERN)[1])
        with self.assertRaisesRegex(ValueError, 'parse failed'):
            self.inspect('const broken = ;\n')

    def test_missing_parser_fails_closed(self):
        with patch('source_governance.javascript_source.subprocess.run', side_effect=FileNotFoundError):
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                self.inspect('const x = 1;\n')

    def test_inspected_source_is_never_executed(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'must-not-exist'
            body = f'imports.gi.GLib.file_set_contents({str(target)!r}, "unsafe");\n'
            self.assertEqual([], self.inspect(body)[1])
            self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
