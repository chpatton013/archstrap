import os
import logging
import subprocess
import tempfile
import unittest
from typing import Iterable

logging.basicConfig(level=logging.DEBUG)

ARCHSTRAP_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
SRC_DIR = os.path.join(ARCHSTRAP_ROOT, "src")
TEST_CASES_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "cases")
)


def archstrap_command(
    archstrap: str,
    install_root: str,
    mode: str,
    spec: str,
) -> Iterable[str]:
    return [
        "python",
        archstrap,
        f"--install-root={install_root}",
        f"--mode={mode}",
        spec,
    ]


class TestCase:
    def __init__(self, name, path):
        self.name = name
        self.path = path


class TempFile:
    def __init__(self, content: str, **kwargs):
        fd, self.path = tempfile.mkstemp(text=True, **kwargs)
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        logging.debug("Created temporary file %s", self.path)

    def __del__(self):
        logging.debug("Deleting temporary file %s", self.path)
        subprocess.call(["sync"])
        os.unlink(self.path)


class TempLoopDevice:
    def __init__(self, size: str, **kwargs):
        self.size = size
        self.kwargs = kwargs
        self.path = None
        self.loop = None
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        logging.debug("TempLoopDevice.open")
        if not self.path:
            _, self.path = tempfile.mkstemp(**self.kwargs)
            subprocess.check_call([
                "fallocate", "--offset", "0", "--length", self.size, self.path
            ])
            logging.debug("Resized tempfile %s", self.path)
        if not self.loop:
            self.loop = subprocess.check_output([
                "losetup", "--find", "--show", self.path
            ]).decode("utf-8").strip()
            logging.debug("Created loop device %s", self.loop)

    def close(self):
        logging.debug("TempLoopDevice.close")
        if self.loop:
            logging.debug("Detaching loop device %s", self.loop)
            subprocess.call(["sync"])
            subprocess.check_call(["losetup", "--detach", self.loop])
            self.loop = None
        if self.path:
            logging.debug("Removing tempfile %s", self.path)
            subprocess.call(["sync"])
            subprocess.check_call(["rm", "--force", self.path])
            self.path = None


class Mount:
    def __init__(self, src: str, dest: str):
        self.src = src
        self.dest = None

        logging.debug("Formatting filesystem in device %s", self.src)
        subprocess.check_call(["mkfs", "--type=ext4", self.src])

        logging.debug("Mounting filesystem to %s", dest)
        subprocess.check_call(["mount", self.src, dest])

        self.dest = dest

    def __del__(self):
        if self.dest:
            logging.debug("Unmounting filesystem from %s", self.src)
            subprocess.call(["sync"])
            subprocess.call(["umount", self.src])


def make_test_fn():
    def test_fn(self):
        temp_loop = TempLoopDevice(str(2 * 2**30), dir="/mnt")
        install_root = tempfile.TemporaryDirectory(dir="/mnt")
        mount = Mount(temp_loop.loop, install_root.name)

        content = subprocess.check_output(
            archstrap_command(
                SRC_DIR,
                install_root.name,
                "shell",
                self._test_case.path,
            )
        ).decode("utf-8")

        output_file = TempFile(content)

        subprocess.check_call(["bash", output_file.path])

    return test_fn


def generate_test_cases(root):
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if path.endswith(".json") and os.path.isfile(path):
            yield TestCase(name, path)


for case in generate_test_cases(TEST_CASES_ROOT):
    classname = f"Test_{case.name}"
    globals()[classname] = type(
        classname,
        (unittest.TestCase, ),
        {
            f"test_{case.name}": make_test_fn(),
            "_test_case": case,
        },
    )
