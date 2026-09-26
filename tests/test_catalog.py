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

    def test_recurses_into_active_skill_groups_and_skips_archives(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / "skills" / "email" / "email-inbox-triage" / "SKILL.md"
            archived = root / "skills" / ".archive" / "old-mail" / "SKILL.md"
            active.parent.mkdir(parents=True)
            archived.parent.mkdir(parents=True)
            active.write_text("description: Read and triage unread email\n")
            archived.write_text("description: Old mail workflow\n")
            catalog = skill_catalog(root, request="summarize unread mail")
            self.assertEqual([candidate.name for candidate in catalog], ["email-inbox-triage"])

    def test_normalizes_common_swedish_email_words_for_candidate_ranking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            email = root / "skills" / "email" / "email-inbox-triage" / "SKILL.md"
            other = root / "skills" / "art" / "ascii-art" / "SKILL.md"
            email.parent.mkdir(parents=True)
            other.parent.mkdir(parents=True)
            email.write_text("description: Triage unread email in an inbox\n")
            other.write_text("description: Create an illustration\n")
            catalog = skill_catalog(root, request="Läs olästa mail")
            self.assertEqual(catalog[0].name, "email-inbox-triage")
