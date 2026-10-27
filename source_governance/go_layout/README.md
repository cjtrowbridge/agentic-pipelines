# Go layout migration proposals

This helper proposes byte edits for explicitly authorized source migrations.
Read Go on stdin and receive JSON on stdout. It never writes or executes input.
Build this trusted helper only after the framework canonical source gate passes.
Consumers must reject overlapping edits, parse the full candidate and review it
before replacing any host file. Headers containing comments require manual care.
Initializer scopes include the entire if/else or switch; loop grammar stays intact.

- `main.go`: Propose scoped initializer moves and statement-boundary whitespace.
