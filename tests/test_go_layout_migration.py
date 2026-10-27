"""
Verify authorized Go migrations preserve scope, branches and literal data.
Compile only a fixed synthetic semantic fixture after its own source gate;
ordinary candidate validation never executes inspected source.
"""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

from source_governance.go_layout import candidate
from source_governance.go_source import inspect_go


ROOT = Path(__file__).resolve().parents[1]
HEADER = '// Synthetic migration regression.\n// No host state or provider access.\n'
PATTERN = r'(?://[^\n]*|(?s:/\*.*?\*/))'


class GoLayoutMigrationTests(unittest.TestCase):
    def test_scope_branches_and_loop_targets(self):
        source = HEADER + '''package main
import "fmt"
func main() {
x := 7
if x := x - 5; x == 2 { fmt.Print(x, ":") } else { panic("branch") }
fmt.Print(x, ":")
if x := 0; x != 0 { panic("branch") } else if y := 3; y == 3 { fmt.Print(y, ":") }
switch n := 4; n { case 4: fmt.Print(n, ":") }
switch value := any(5); typed := value.(type) { case int: fmt.Print(typed, ":") }
for i := 0; i < 2; i++ { if j := i; j == 0 { continue }; fmt.Print(i, ":") }
fmt.Print(x)
}
'''
        result, manual = candidate(source)
        self.assertEqual([], manual)
        self.assertEqual([], inspect_go(result, PATTERN)[1])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / 'src').mkdir()
            (root / 'src/main.go').write_text(result)
            (root / 'src/README.md').write_text('- `main.go`: Fixed scope and branch regression.\n')
            config = {'code': {'roots': ['src'], 'max_lines': 400,
                              'languages': {'.go': {'adapter': 'go', 'comment_pattern': PATTERN}}}}
            (root / 'api.sample.yaml').write_text(yaml.safe_dump(config))
            checked = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/check_source_governance.py'), '--repo-root', str(root)],
                capture_output=True, text=True, check=False, timeout=60,
            )
            self.assertEqual(0, checked.returncode, checked.stderr)
            environment = dict(os.environ)
            environment.update(GOTOOLCHAIN='local', GO111MODULE='off', GOENV='off', GOWORK='off', GOFLAGS='')
            ran = subprocess.run(
                ['go', 'run', 'src/main.go'], cwd=root, env=environment,
                capture_output=True, text=True, check=False, timeout=60,
            )
            self.assertEqual(0, ran.returncode, ran.stderr)
            self.assertEqual('2:7:3:4:5:1:7', ran.stdout)

    def test_comment_bearing_header_requires_manual_review(self):
        source = HEADER + 'package fixture\nfunc run() {\nif value := 1; /* retain */ value == 1 { println(value) }\n}\n'
        result, manual = candidate(source)
        self.assertEqual(1, len(manual))
        self.assertIn('/* retain */', result)
        self.assertTrue(any('if header' in item for item in inspect_go(result, PATTERN)[1]))

    def test_literal_contents_and_initializer_closure_survive(self):
        source = HEADER + 'package fixture\nvar text = `if x := 1; x { // data }`\nfunc run() { if f := func() bool { return true }; f() { println(text) } }\n'
        result, manual = candidate(source)
        self.assertEqual([], manual)
        self.assertIn('`if x := 1; x { // data }`', result)
        self.assertEqual([], inspect_go(result, PATTERN)[1])
        self.assertEqual((result, []), candidate(result))

    def test_candidate_validation_never_executes_init(self):
        result, manual = candidate(HEADER + 'package fixture\nfunc init() { panic("never execute") }\n')
        self.assertEqual([], manual)
        self.assertEqual([], inspect_go(result, PATTERN)[1])

    def test_invalid_syntax_has_no_candidate(self):
        with self.assertRaises(ValueError):
            candidate(HEADER + 'package fixture\nfunc broken(\n')
