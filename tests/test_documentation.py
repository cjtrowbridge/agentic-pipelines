from pathlib import Path
import unittest


class DocumentationTests(unittest.TestCase):
    def test_pipeline_progress_rule_requires_query_counts_and_eta(self) -> None:
        text = Path("AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("completed and remaining query counts", text)
        self.assertIn("static-template and assembled-request sizes", text)
        self.assertIn("ETA derived from elapsed time", text)
        self.assertIn("without exposing credentials or protected inputs", text)

    def test_pdf_sources_must_be_converted_before_model_use(self) -> None:
        text = Path("AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Never provide a PDF directly to an LLM", text)
        self.assertIn("linked Markdown/text derivative", text)
        design = Path("playbooks/how_to_design_a_pipeline.md").read_text(encoding="utf-8")
        self.assertIn("derived text—not the PDF", design)

    def test_ctrl_c_rule_requires_controlled_exit(self) -> None:
        text = Path("AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Ctrl+C as a controlled interruption", text)
        self.assertIn("exit with status 130", text)
        operation = Path("playbooks/how_to_operate_and_resume_a_pipeline.md").read_text(encoding="utf-8")
        self.assertIn("return exit status 130", operation)

    def test_prompt_rule_requires_limits_and_reasoning_justification(self) -> None:
        text = Path("AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("completion-token limit", text)
        self.assertIn("context-window limit (`num_ctx`)", text)
        self.assertIn("`num_predict` does not limit context/KV-cache allocation", text)
        self.assertIn("Reasoning is opt-in", text)
        prompts = Path("playbooks/how_to_build_pipeline_prompts.md").read_text(encoding="utf-8")
        self.assertIn("completion-token limit", prompts)
        self.assertIn("context-window limit (`num_ctx`)", prompts)
        self.assertIn("never mistake `num_predict` for a context/KV-cache limit", prompts)
        self.assertIn("disable it for clear, constrained transformations", prompts)

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
