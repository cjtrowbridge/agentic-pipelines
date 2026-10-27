// Propose source-preserving Go layout edits for an authorized migration.
// Parse stdin and emit edits only; never execute source or write host files.
package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"io"
	"os"
	"strings"
)

// Edit describes one byte range replacement in the original source.
// Zero-width insertions retain their order when multiple scopes end together.
type Edit struct {
	Start int
	End int
	Text string
}

// Migration accumulates exact edits and reports headers requiring manual care.
// Original comments and expressions are retained rather than reprinted from AST.
type Migration struct {
	Edits []Edit
	Manual []string
	positions *token.FileSet
	source []byte
	newlines map[int]bool
}

// offset resolves physical bytes, ignoring source line directives.
// Every edit addresses the original packet, not a rewritten intermediate file.
func (m *Migration) offset(pos token.Pos) int {
	return m.positions.PositionFor(pos, false).Offset
}

// replace records a byte replacement without modifying the input packet.
// The consumer must reject overlaps before applying any edits atomically.
func (m *Migration) replace(start, end int, text string) {
	edit := Edit{}
	edit.Start = start
	edit.End = end
	edit.Text = text
	m.Edits = append(m.Edits, edit)
}

// newline inserts whitespace once at a statement boundary.
// It never changes tokens inside a string, comment or loop clause.
func (m *Migration) newline(pos token.Pos) {
	offset := m.offset(pos)
	if !m.newlines[offset] {
		m.newlines[offset] = true
		m.replace(offset, offset, "\n")
	}
}

// header lifts an initializer into a new enclosing lexical scope.
// The scope includes the full if/else or switch, preserving variable lifetime.
func (m *Migration) header(word string, start token.Pos, init ast.Stmt, condition, end token.Pos) {
	if init == nil {
		return
	}
	prefix := strings.TrimSpace(string(m.source[m.offset(start)+len(word):m.offset(init.Pos())]))
	middle := strings.TrimSpace(string(m.source[m.offset(init.End()):m.offset(condition)]))
	if prefix != "" || (middle != ";" && middle != "") {
		m.Manual = append(m.Manual, fmt.Sprintf("%d: initializer header contains comments; review manually", m.positions.PositionFor(start, false).Line))
		return
	}
	m.replace(m.offset(start), m.offset(start)+len(word), "{\n")
	m.replace(m.offset(init.End()), m.offset(condition), "\n"+word+" ")
	m.replace(m.offset(end), m.offset(end), "\n}")
}

// inspect proposes scoped initializer moves and statement-boundary whitespace.
// For-clause grammar and type-switch bindings retain their existing syntax.
func (m *Migration) inspect(file *ast.File) {
	exempt := make(map[ast.Node]bool)
	ast.Inspect(file, func(node ast.Node) bool {
		switch typed := node.(type) {
		case *ast.ForStmt:
			exempt[typed.Init] = true
			exempt[typed.Post] = true
		case *ast.IfStmt:
			exempt[typed.Init] = true
			m.header("if", typed.If, typed.Init, typed.Cond.Pos(), typed.End())
		case *ast.SwitchStmt:
			exempt[typed.Init] = true
			condition := typed.Body.Lbrace
			if typed.Tag != nil {
				condition = typed.Tag.Pos()
			}
			m.header("switch", typed.Switch, typed.Init, condition, typed.End())
		case *ast.TypeSwitchStmt:
			exempt[typed.Init] = true
			exempt[typed.Assign] = true
			m.header("switch", typed.Switch, typed.Init, typed.Assign.Pos(), typed.End())
		}
		return true
	})
	seen := make(map[int]bool)
	seen[m.positions.PositionFor(file.Package, false).Line] = true
	ast.Inspect(file, func(node ast.Node) bool {
		if node == nil || exempt[node] {
			return true
		}
		line := m.positions.PositionFor(node.Pos(), false).Line
		switch typed := node.(type) {
		case *ast.BlockStmt:
			if len(typed.List) > 0 {
				if m.positions.PositionFor(typed.List[0].Pos(), false).Line == line {
					m.newline(typed.List[0].Pos())
				}
				last := typed.List[len(typed.List)-1]
				if m.positions.PositionFor(last.End(), false).Line == m.positions.PositionFor(typed.Rbrace, false).Line {
					m.newline(typed.Rbrace)
				}
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
				m.newline(node.Pos())
			}
			seen[line] = true
		}
		return true
	})
}

// main validates one source packet and emits a reviewable migration proposal.
// Syntax errors fail closed before an edit proposal can be emitted.
func main() {
	source, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintln(os.Stderr, "cannot read source")
		os.Exit(1)
	}
	positions := token.NewFileSet()
	file, err := parser.ParseFile(positions, "input.go", source, parser.ParseComments|parser.AllErrors)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	migration := Migration{}
	migration.positions = positions
	migration.source = source
	migration.newlines = make(map[int]bool)
	migration.inspect(file)
	err = json.NewEncoder(os.Stdout).Encode(migration)
	if err != nil {
		fmt.Fprintln(os.Stderr, "cannot encode migration")
		os.Exit(1)
	}
}
