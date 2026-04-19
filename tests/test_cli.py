import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cli
from exceptions import InvalidInput


class TutorCLIAliasTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_aliases_file = cli.ALIASES_FILE
        self.original_history_file = cli.HISTORY_FILE
        self.original_built_in_aliases = dict(cli.BUILT_IN_ALIASES)

        cli.ALIASES_FILE = str(Path(self.temp_dir.name) / "aliases.conf")
        cli.HISTORY_FILE = str(Path(self.temp_dir.name) / "history.txt")

    def tearDown(self):
        cli.ALIASES_FILE = self.original_aliases_file
        cli.HISTORY_FILE = self.original_history_file
        cli.BUILT_IN_ALIASES.clear()
        cli.BUILT_IN_ALIASES.update(self.original_built_in_aliases)
        self.temp_dir.cleanup()

    def write_aliases(self, content):
        Path(cli.ALIASES_FILE).write_text(content, encoding="utf-8")

    def test_built_in_alias_resolves(self):
        app = cli.TutorCLI()

        self.assertEqual(app.resolve_command("ss"), "student_summary")

    def test_custom_alias_file_supports_multiple_formats(self):
        self.write_aliases(
            "\n".join([
                "alias ls lessons",
                "pay=add_payment",
                "sumall summary",
            ])
        )

        app = cli.TutorCLI()

        self.assertEqual(app.resolve_command("ls"), "lessons")
        self.assertEqual(app.resolve_command("pay"), "add_payment")
        self.assertEqual(app.resolve_command("sumall"), "summary")

    def test_aliases_can_chain(self):
        self.write_aliases(
            "\n".join([
                "short ss",
                "ss student_summary",
            ])
        )

        app = cli.TutorCLI()

        self.assertEqual(app.resolve_command("short"), "student_summary")

    def test_alias_loop_raises_clear_error(self):
        self.write_aliases(
            "\n".join([
                "a b",
                "b a",
            ])
        )

        app = cli.TutorCLI()

        with self.assertRaises(InvalidInput):
            app.resolve_command("a")

    def test_invalid_alias_config_raises(self):
        self.write_aliases("alias only_two_parts")

        with self.assertRaises(InvalidInput):
            cli.TutorCLI()


if __name__ == "__main__":
    unittest.main()
