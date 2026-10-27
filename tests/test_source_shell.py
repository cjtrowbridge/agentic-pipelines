"""Exercise shell data boundaries while retaining source enforcement.
All inputs are parsed as text; no submitted shell command is executed.
"""

import unittest

from source_governance.text_source import inspect_text

HEADER = "# Observe shell structure.\n# Keep data counted and commands separated.\n"


def inspect(body):
    return inspect_text(HEADER + body, "shell", r"#[^\n]*")


class ShellTests(unittest.TestCase):
    def test_quoted_payload_is_counted_not_interpreted(self):
        count, issues = inspect("cat <<'END'\n# literal, not a comment\nx = 1 << 20; print(x)\nEND\n")
        self.assertEqual(count, 4)
        self.assertEqual(issues, [])

    def test_multiple_and_tab_stripped_bodies(self):
        count, issues = inspect('cat <<ONE <<-"TWO"\na\nONE\n\tb\n\tTWO\n')
        self.assertEqual((count, issues), (5, []))

    def test_missing_delimiter_fails(self):
        for source in ("cat <<'END'\nbody\n", "cat <<END", "cat <<END\n"):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    inspect(source)

    def test_heredoc_cannot_hide_following_commands(self):
        _, issues = inspect("cat <<END\ndata\nEND\necho one; echo two\n")
        self.assertTrue(any("6: split shell actions" in issue for issue in issues))

    def test_here_string_is_not_a_body(self):
        self.assertEqual(inspect('read -r value <<<"$input"\n'), (1, []))

    def test_case_terminators_are_grammar_only(self):
        for token in (";;", ";&", ";;&"):
            self.assertEqual(inspect(token + "\n"), (1, []))
            self.assertTrue(inspect("echo one " + token + " echo two\n")[1])

    def test_unsupported_delimiter_still_fails_closed(self):
        self.assertTrue(inspect("cat <<'END-DATA'\n")[1])

    def test_unquoted_executable_substitution_is_rejected(self):
        for expression in ("$(echo one; echo two)", "`echo one`"):
            with self.assertRaises(ValueError):
                inspect("cat <<END\n" + expression + "\nEND\n")
        self.assertEqual(inspect("cat <<END\n${value}\nEND\n"), (3, []))

    def test_large_literal_payload_retains_size(self):
        count, issues = inspect("cat <<END\n" + "# data\n" * 401 + "END\n")
        self.assertEqual(count, 403)
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
