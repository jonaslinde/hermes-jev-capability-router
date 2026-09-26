import tempfile
import unittest
from pathlib import Path

from catalog import profile_catalog, skill_catalog


class CatalogTests(unittest.TestCase):
    def test_reads_only_profile_metadata_and_soul(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); profile = root / "profiles" / "researcher"; profile.mkdir(parents=True)
            (profile / "config.yaml").write_text('description: "Research and evidence work"\n')
            (profile / "SOUL.md").write_text("# Researcher\nUse primary sources.")
            (profile / ".env").write_text("SHOULD_NOT_BE_READ=secret")
            catalog = profile_catalog(root)
            self.assertEqual(catalog[0].name, "researcher")
            self.assertEqual(catalog[0].description, "Research and evidence work")
            self.assertNotIn("secret", catalog[0].excerpt)

    def test_reads_profile_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); skill = root / "skills" / "web"; skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\ndescription: Search primary sources\n---\n# Web")
            catalog = skill_catalog(root)
            self.assertEqual([(x.name, x.description) for x in catalog], [("web", "Search primary sources")])
