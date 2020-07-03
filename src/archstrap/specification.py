import copy
import os
from typing import Any, Iterable, Iterator, Mapping, Optional

from archstrap.mode import Mode

DEFAULT_INITRD_HOOKS = [
    "base",
    "udev",
    "autodetect",
    "modconf",
    "block",
    "filesystems",
    "fsck",
]


class PackageSpecification:
    def __init__(
        self,
        base: Optional[str] = "base",
        kernel: Optional[str] = "linux",
        firmware: Optional[str] = "linux-firmware",
        extra: Iterable[str] = [],
    ):
        self.base = base
        self.kernel = kernel
        self.firmware = firmware
        self.extra = list(extra)

    @property
    def kernel_headers(self) -> Optional[str]:
        return f"{self.kernel}-headers" if self.kernel else None

    def packages(self) -> Iterator[str]:
        if self.base:
            yield self.base
        if self.kernel:
            yield self.kernel
            yield self.kernel_headers
        if self.firmware:
            yield self.firmware
        yield from self.extra

    def apply(self, install_root: str, mode: Mode):
        mode.on_section("Install Packages")

        mode.on_command(f"pacstrap {install_root} {' '.join(self.packages())}")


class SystemSpecification:
    def __init__(
        self,
        timezone: str,
        locale: str,
        charset: str,
        keymap: str,
        hostname: str,
        root_password: Optional[str] = None,
    ):
        self.timezone = timezone
        self.locale = locale
        self.charset = charset
        self.keymap = keymap
        self.hostname = hostname
        self.root_password = root_password

    def apply(self, install_root: str, mode: Mode):
        mode.on_section("Configure System")

        # Systemd
        systemd_firstboot = [
            "systemd-firstboot",
            "--setup-machine-id",
            f"--timezone={self.timezone}",
            f"--locale={self.locale}",
            f"--keymap={self.keymap}",
            f"--hostname={self.hostname}",
            f"--root={install_root}",
        ]
        if self.root_password:
            systemd_firstboot.append(f"--root-password={self.root_password}")
        else:
            mode.on_command(f"arch-chroot {install_root} passwd")
        mode.on_command(" ".join(systemd_firstboot))

        # Timezone
        mode.on_command(f"arch-chroot {install_root} hwclock --systohc")

        # Locale
        locale_gen_file = os.path.join(install_root, "etc/locale.gen")
        mode.on_command(
            f"echo {self.locale} {self.charset} > {locale_gen_file}"
        )
        mode.on_command(f"arch-chroot {install_root} locale-gen")

        # Network
        hosts_file = os.path.join(install_root, "etc/hosts")
        mode.on_command(
            "\n".join([
                f"cat > {hosts_file} <<EOF",
                "127.0.0.1 localhost",
                "::1       localhost",
                f"127.0.1.1 {self.hostname}.localdomain {self.hostname}",
                "EOF",
            ])
        )


class InitrdSpecification:
    def __init__(
        self,
        modules: Iterable[str] = [],
        binaries: Iterable[str] = [],
        files: Iterable[str] = [],
        hooks: Iterable[str] = DEFAULT_INITRD_HOOKS,
        compression: str = "xz",
        compression_options: Iterable[str] = [],
    ):
        self.modules = list(modules)
        self.binaries = list(binaries)
        self.files = list(files)
        self.hooks = list(hooks)
        self.compression = compression
        self.compression_options = compression_options

    def apply(self, install_root: str, mode: Mode):
        mode.on_section("Create Initramfs")

        mkinitcpio_conf_file = os.path.join(install_root, "etc/mkinitcpio.conf")
        mode.on_command(
            "\n".join([
                f"cat > {mkinitcpio_conf_file} <<EOF",
                f"MODULES=({' '.join(self.modules)})",
                f"BINARIES=({' '.join(self.binaries)})",
                f"FILES=({' '.join(self.files)})",
                f"HOOKS=({' '.join(self.hooks)})",
                f"COMPRESSION=\"{self.compression}\"",
                f"COMPRESSION_OPTIONS=({' '.join(self.compression_options)})",
                "EOF",
            ])
        )
        mode.on_command(
            f"kernel=\"$(find {install_root}/lib/modules -mindepth 1 -maxdepth 1 -type d | xargs basename)\""
        )
        mode.on_command(
            f"arch-chroot {install_root} mkinitcpio −−allpresets --kernel=\"$kernel\" --generate /boot/initramfs-linux-fallback.img"
        )


class Specification:
    def __init__(
        self,
        packages: PackageSpecification,
        system: SystemSpecification,
        initrd: InitrdSpecification,
    ):
        self.packages = packages
        self.system = system
        self.initrd = initrd

    def apply(self, install_root: str, mode: Mode):
        mode.on_begin()
        self.packages.apply(install_root, mode)
        self.system.apply(install_root, mode)
        self.initrd.apply(install_root, mode)
        mode.on_end()


def make_specification(spec: Mapping[str, Any]) -> Specification:
    spec = copy.deepcopy(dict(spec))
    spec["packages"] = PackageSpecification(**spec.get("packages", {}))
    spec["system"] = SystemSpecification(**spec["system"])
    spec["initrd"] = InitrdSpecification(**spec.get("initrd", {}))
    return Specification(**spec)
