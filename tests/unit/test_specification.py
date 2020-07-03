import unittest
from unittest.mock import MagicMock, call, patch

from context import archstrap

from archstrap.specification import (
    InitrdSpecification,
    PackageSpecification,
    Specification,
    SystemSpecification,
    make_specification,
)


class PackageSpecificationTest(unittest.TestCase):
    def test_package_list(self):
        self.assertListEqual(
            [],
            list(
                PackageSpecification(
                    base=None,
                    kernel=None,
                    firmware=None,
                ).packages()
            ),
        )
        self.assertListEqual(
            ["base"],
            list(PackageSpecification(kernel=None, firmware=None).packages()),
        )
        self.assertListEqual(
            ["linux", "linux-headers"],
            list(PackageSpecification(base=None, firmware=None).packages()),
        )
        self.assertListEqual(
            ["linux-firmware"],
            list(PackageSpecification(base=None, kernel=None).packages()),
        )
        self.assertListEqual(
            ["base", "linux", "linux-headers", "linux-firmware"],
            list(PackageSpecification().packages()),
        )

    def test_apply(self):
        mode = MagicMock()

        spec = PackageSpecification("base", "kernel", "firmware", ["extra"])
        spec.apply("install_root", mode)

        mode.on_section.assert_called_once_with("Install Packages")
        mode.on_command.assert_has_calls([
            call(
                "pacstrap install_root base kernel kernel-headers firmware extra"
            ),
        ])


class SystemSpecificationTest(unittest.TestCase):
    def test_apply(self):
        mode = MagicMock()

        spec = SystemSpecification(
            "timezone",
            "locale",
            "charset",
            "keymap",
            "hostname",
            "root_password",
        )
        spec.apply("install_root", mode)

        mode.on_section.assert_called_once_with("Configure System")
        mode.on_command.assert_has_calls([
            call(
                " ".join([
                    "systemd-firstboot",
                    "--setup-machine-id",
                    "--timezone=timezone",
                    "--locale=locale",
                    "--keymap=keymap",
                    "--hostname=hostname",
                    "--root=install_root",
                    "--root-password=root_password",
                ])
            ),
            call("arch-chroot install_root hwclock --systohc"),
            call("echo locale charset > install_root/etc/locale.gen"),
            call("arch-chroot install_root locale-gen"),
            call(
                "\n".join([
                    "cat > install_root/etc/hosts <<EOF",
                    "127.0.0.1 localhost",
                    "::1       localhost",
                    "127.0.1.1 hostname.localdomain hostname",
                    "EOF",
                ]),
            ),
        ])

    def test_apply_no_root_password(self):
        mode = MagicMock()

        spec = SystemSpecification(
            "timezone",
            "locale",
            "charset",
            "keymap",
            "hostname",
        )
        spec.apply("install_root", mode)

        mode.on_command.assert_has_calls([
            call("arch-chroot install_root passwd")
        ])


class InitrdSpecificationTest(unittest.TestCase):
    def test_apply(self):
        mode = MagicMock()

        spec = InitrdSpecification(
            ["modules"],
            ["binaries"],
            ["files"],
            ["hooks"],
            "compression",
            ["compression_options"],
        )
        spec.apply("install_root", mode)

        mode.on_section.assert_called_once_with("Create Initramfs")
        mode.on_command.assert_has_calls([
            call(
                "\n".join([
                    "cat > install_root/etc/mkinitcpio.conf <<EOF",
                    "MODULES=(modules)",
                    "BINARIES=(binaries)",
                    "FILES=(files)",
                    "HOOKS=(hooks)",
                    "COMPRESSION=\"compression\"",
                    "COMPRESSION_OPTIONS=(compression_options)",
                    "EOF",
                ]),
            ),
            call(
                "kernel=\"$(find install_root/lib/modules -mindepth 1 -maxdepth 1 -type d | xargs basename)\""
            ),
            call(
                "arch-chroot install_root mkinitcpio −−allpresets --kernel=\"$kernel\" --generate /boot/initramfs-linux-fallback.img"
            ),
        ])


class SpecificationTest(unittest.TestCase):
    def test_apply(self):
        packages = MagicMock()
        system = MagicMock()
        initrd = MagicMock()
        mode = MagicMock()

        spec = Specification(packages, system, initrd)
        spec.apply("install_root", mode)

        mode.on_begin.assert_called_once_with()
        packages.apply.assert_called_once_with("install_root", mode)
        system.apply.assert_called_once_with("install_root", mode)
        initrd.apply.assert_called_once_with("install_root", mode)
        mode.on_end.assert_called_once_with()
