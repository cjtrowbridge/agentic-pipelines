from pathlib import Path
import unittest


class DocumentationTests(unittest.TestCase):
    def test_bootstrap_requires_a_tracked_host_api_sample(self) -> None:
        text = Path("playbooks/how_to_bootstrap_framework_submodule_into_host_repo.md").read_text(encoding="utf-8")
        self.assertIn("tracked root `api.sample.yaml`", text)
        self.assertIn("copied from the framework sample", text)
        self.assertIn("only `api.yaml` is ignored", text)

    def test_readme_explains_pipeline_entry_points_after_introduction(self) -> None:
        text = Path("README.md").read_text(encoding="utf-8")
        heading = "## Pipeline entry points"
        self.assertIn(heading, text)
        self.assertLess(text.index("Agentic Pipelines is"), text.index(heading))
        self.assertLess(text.index(heading), text.index("## How agents use the framework"))
        for command in ("validate_pipeline_package.py", "preflight", "discover", "run", "inspect-entity", "report", "analyze", "retry-cohort", "rollback-entity"):
            self.assertIn(command, text)

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
