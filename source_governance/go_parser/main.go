// Parse untrusted Go source for governance without importing or executing it.
// Emit lexical spans and statement-layout findings for the Python source gate.
package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/scanner"
	"go/token"
	"io"
	"os"
)

// Lexeme records parser-recognized comments and executable token positions.
// Python applies the host's configured comment pattern to these exact spans.
type Lexeme struct {
	Line int
	Text string
	Comment bool
}

// Report keeps syntax errors distinct from policy layout findings.
// Invalid input cannot be certified by a partial syntax tree.
type Report struct {
	Tokens []Lexeme
	Issues []string
	Error string
}

// inspectLayout distinguishes statement bodies from composite literal data.
// Loop-clause separators and type-switch bindings are Go grammar, not actions.
func inspectLayout(file *ast.File, positions *token.FileSet) []string {
	issues := make([]string, 0)
	exempt := make(map[ast.Node]bool)
	ast.Inspect(file, func(node ast.Node) bool {
		switch typed := node.(type) {
		case *ast.ForStmt:
			exempt[typed.Init] = true
			exempt[typed.Post] = true
		case *ast.TypeSwitchStmt:
			exempt[typed.Assign] = true
		}
		return true
	})
	seen := make(map[int]bool)
	seen[positions.PositionFor(file.Package, false).Line] = true
	ast.Inspect(file, func(node ast.Node) bool {
		if node == nil || exempt[node] {
			return true
		}
		line := positions.PositionFor(node.Pos(), false).Line
		switch typed := node.(type) {
		case *ast.BlockStmt:
			if len(typed.List) > 0 && positions.PositionFor(typed.List[0].Pos(), false).Line == line {
				issues = append(issues, fmt.Sprintf("%d: put block body on its own line", line))
			}
			return true
		case *ast.EmptyStmt:
			return true
		}
		_, statement := node.(ast.Stmt)
		switch node.(type) {
		case *ast.FuncDecl, *ast.ValueSpec, *ast.TypeSpec, *ast.ImportSpec:
			statement = true
		case *ast.DeclStmt:
			statement = false
		}
		if statement {
			if seen[line] {
				issues = append(issues, fmt.Sprintf("%d: multiple statements on one line", line))
			}
			seen[line] = true
		}
		return true
	})
	return issues
}

// inspect parses source and scans tokens using the same standard Go grammar.
// No package resolution, type checking, compilation or source execution occurs.
func inspect(source []byte) Report {
	result := Report{}
	positions := token.NewFileSet()
	file, err := parser.ParseFile(positions, "input.go", source, parser.ParseComments|parser.AllErrors)
	if err != nil {
		result.Error = err.Error()
		return result
	}
	result.Issues = inspectLayout(file, positions)
	tokens := token.NewFileSet()
	input := tokens.AddFile("input.go", tokens.Base(), len(source))
	var lexer scanner.Scanner
	lexer.Init(input, source, nil, scanner.ScanComments)
	for {
		position, kind, literal := lexer.Scan()
		if kind == token.EOF {
			break
		}
		if kind == token.SEMICOLON && literal == "\n" {
			continue
		}
		if literal == "" {
			literal = kind.String()
		}
		lexeme := Lexeme{}
		lexeme.Line = tokens.PositionFor(position, false).Line
		lexeme.Text = literal
		lexeme.Comment = kind == token.COMMENT
		result.Tokens = append(result.Tokens, lexeme)
	}
	return result
}

// main reads one source packet and writes one deterministic JSON report.
// Process errors fail visibly and never execute any inspected package.
func main() {
	source, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, "cannot read Go source")
		os.Exit(1)
	}
	err = json.NewEncoder(os.Stdout).Encode(inspect(source))
	if err != nil {
		fmt.Fprintln(os.Stderr, "cannot encode Go source report")
		os.Exit(1)
	}
}
