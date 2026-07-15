from pathlib import Path
import unittest


class DocumentationTests(unittest.TestCase):
    def test_migration_guide_names_required_boundaries(self) -> None:
        text = Path("docs/migrating_from_agents.md").read_text(encoding="utf-8")
        for term in ("./pipelines", "AGENTS.md", "TODO.md", "journal", "api.yaml", "schema version 2", "rollback", "LLM stage"):
            self.assertIn(term, text)

    def test_active_product_files_do_not_reference_removed_systems(self) -> None:
        roots = (Path("AGENTS.md"), Path("README.md"), Path("playbooks"), Path("prompts"), Path("references"), Path("templates"))
        for root in roots:
            paths = [root] if root.is_file() else list(root.rglob("*.md"))
            for path in paths:
                text = path.read_text(encoding="utf-8").lower()
                self.assertNotIn("kanban/", text, path)
                self.assertNotIn("./agents/", text, path)
                self.assertNotIn("rules.md", text, path)


if __name__ == "__main__":
    unittest.main()
