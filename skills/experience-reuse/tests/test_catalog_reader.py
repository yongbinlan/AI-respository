import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import tempfile
import unittest
import json

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/read_skill.py'
spec = importlib.util.spec_from_file_location('catalog_reader', SCRIPT)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class CatalogReaderBehavior(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='experience-catalog-test-')
        self.root = Path(self.temp.name)
        self.project = self.root / 'project'
        self.user = self.root / 'user'
        for location, content in [(self.project, 'project skill'), (self.user, 'different user skill')]:
            file = location / 'example/SKILL.md'
            file.parent.mkdir(parents=True)
            file.write_text(content, encoding='utf-8')
        self.roots = ['r0=' + str(self.project), 'r1=' + str(self.user)]

    def tearDown(self):
        self.temp.cleanup()

    def test_catalog_selects_supplied_project_instead_of_existing_user_alternative(self):
        path = reader.resolve_catalog(self.roots, 'r0/example/SKILL.md')
        self.assertEqual(path, self.project / 'example/SKILL.md')

    def test_unknown_alias_does_not_guess(self):
        with self.assertRaises(ValueError):
            reader.resolve_catalog(self.roots, 'r2/example/SKILL.md')

    def test_missing_project_target_does_not_fall_back_to_user_copy(self):
        (self.project / 'example/SKILL.md').unlink()
        with self.assertRaises(FileNotFoundError):
            reader.resolve_catalog(self.roots, 'r0/example/SKILL.md')

    def test_traversal_rejected(self):
        with self.assertRaises(ValueError):
            reader.resolve_catalog(self.roots, 'r0/../user/example/SKILL.md')

    def test_other_agent_catalog_rejected(self):
        with self.assertRaises(ValueError):
            reader.resolve_catalog(['r0=' + str(self.root / '.agents/skills')], 'r0/example/SKILL.md')

    def test_output_proves_actual_file_and_lookup_creates_no_files(self):
        before = sorted(str(p) for p in self.root.rglob('*'))
        output = io.StringIO()
        with redirect_stdout(output):
            code = reader.main(['--root', self.roots[0], '--root', self.roots[1], '--reference', 'r0/example/SKILL.md'])
        result = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(result['ok'])
        self.assertEqual(result['activation'], 'experience-reuse.catalog-first')
        self.assertEqual(result['content'], 'project skill')
        self.assertFalse(result['fallback_attempted'])
        self.assertEqual(before, sorted(str(p) for p in self.root.rglob('*')))

    def test_duplicate_alias_rejected(self):
        with self.assertRaises(ValueError):
            reader.resolve_catalog([self.roots[0], 'r0=' + str(self.user)], 'r0/example/SKILL.md')


if __name__ == '__main__':
    unittest.main(verbosity=2)
