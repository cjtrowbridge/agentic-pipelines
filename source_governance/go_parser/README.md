# Go syntax parser

Trusted standard-library helper for Go source governance. Reads source on stdin
and returns lexical spans and statement layout findings; never executes it.
The Python adapter gates the framework before compiling this helper. The helper
itself uses the existing conservative C-style checks, avoiding recursive builds.

- `main.go`: Parse Go syntax, emit exact token spans and reject compressed statement bodies.
