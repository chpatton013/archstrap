import unittest
from unittest.mock import MagicMock, call, patch

from context import archstrap

from archstrap import run


class RunTest(unittest.TestCase):
    @patch("archstrap.make_mode")
    def test_run(self, make_mode):
        spec = MagicMock()
        mode = MagicMock()

        make_mode.return_value = mode

        run(spec, "mode", "install_root")

        make_mode.assert_called_once_with("mode")
        spec.apply.assert_called_once_with("install_root", mode)
