from pathlib import Path
import unittest
from scripts.lint_prompts import lint

class PromptCatalogTests(unittest.TestCase):
    def test_catalog_is_valid(self)->None:
        self.assertEqual([],lint(Path("prompts")))

if __name__=="__main__": unittest.main()
