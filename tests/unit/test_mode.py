import unittest
from unittest.mock import patch

from context import archstrap

from archstrap.mode import make_mode, ExecMode, DryrunMode, ShellMode


class MockPrint:
    def __init__(self):
        self.buffer = ""

    def __call__(self, *args):
        self.buffer += " ".join([str(arg) for arg in args])
        self.buffer += "\n"


class ModeTest(unittest.TestCase):
    def setUp(self):
        self.mock_print = MockPrint()

        logging_info = patch("archstrap.mode.logging.info")
        subprocess_check_call = patch("archstrap.mode.subprocess.check_call")
        print = patch("archstrap.mode.print")

        self.logging_info = logging_info.start()
        self.subprocess_check_call = subprocess_check_call.start()
        self.print = print.start()

        self.print.side_effect = self.mock_print

        self.addCleanup(logging_info.stop)
        self.addCleanup(subprocess_check_call.stop)
        self.addCleanup(print.stop)


class ExecModeTest(ModeTest):
    def setUp(self):
        super().setUp()
        self.mode = ExecMode()

    def test_on_begin(self):
        self.mode.on_begin()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_section(self):
        self.mode.on_section("section")
        self.logging_info.assert_called_once_with("SECTION %s", "section")
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_command(self):
        self.mode.on_command("command")
        self.logging_info.assert_called_once_with("COMMAND %s", "command")
        self.subprocess_check_call.assert_called_once_with(
            "command", shell=True
        )
        self.print.assert_not_called()

    def test_on_end(self):
        self.mode.on_end()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()


class DryrunModeTest(ModeTest):
    def setUp(self):
        super().setUp()
        self.mode = DryrunMode()

    def test_on_begin(self):
        self.mode.on_begin()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_section(self):
        self.mode.on_section("section")
        self.logging_info.assert_called_once_with("SECTION %s", "section")
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_command(self):
        self.mode.on_command("command")
        self.logging_info.assert_called_once_with("COMMAND %s", "command")
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_end(self):
        self.mode.on_end()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()


class ShellModeTest(ModeTest):
    def setUp(self):
        super().setUp()
        self.mode = ShellMode()

    def test_on_begin(self):
        self.mode.on_begin()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_called()
        self.assertEqual(
            f"#!/usr/bin/bash\nset -xeuo pipefail\n",
            self.print.side_effect.buffer,
        )

    def test_on_section(self):
        self.mode.on_section("section")
        self.logging_info.assert_called_once_with("SECTION %s", "section")
        self.subprocess_check_call.assert_not_called()
        self.print.assert_called()
        self.assertEqual(
            f"\n# section\n",
            self.print.side_effect.buffer,
        )

    def test_on_command(self):
        self.mode.on_command("command")
        self.logging_info.assert_called_once_with("COMMAND %s", "command")
        self.subprocess_check_call.assert_not_called()
        self.print.assert_called_once_with("command")

    def test_on_end(self):
        self.mode.on_end()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()


class MakeModeTest(unittest.TestCase):
    def test_make_mode(self):
        self.assertEqual(ExecMode, make_mode("exec").__class__)
        self.assertEqual(DryrunMode, make_mode("dryrun").__class__)
        self.assertEqual(ShellMode, make_mode("shell").__class__)
