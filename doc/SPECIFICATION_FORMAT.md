# Specification Format

The specification JSON file informs `archstrap` of the way to bootstrap your
system. The specification format is broken down into three parts: packages,
system configuration, and initrd configuration.

## Packages

| Parameter | Description | Default |
|-----------|-------------|---------|
| `base` | The base system package group. | `base` |
| `kernel` | The kernel package. Implies the name of the kernel-headers package as well. | `linux` |
| `firmware` | The firmware package. | `linux-firmware` |
| `extra` | A list of additional packages to include. | `[]` |

## System Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `timezone` | The timezone to set as localtime. | N/A |
| `locale` | The locale to generate with `locale-gen` and to set as `LANG`. | N/A |
| `charset` | The charset to generate with `locale-gen`. | N/A |
| `keymap` | The keymap to set as `KEYMAP`. | N/A |
| `hostname` | The hostname for the machine. | N/A |
| `root_password` | Password for the `root` user. | Prompt the user |

## Initrd Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `modules` | The list of firmware modules to include in the initrd. | `[]` |
| `binaries` | The list of executable files to include in the initrd. | `[]` |
| `files` | The list of extra files to include in the initrd. | `[]` |
| `hooks` | The list of setup hooks to run while loading the initrd. | `[]` |
| `compression` | The name of the program to use to compress the initrd. | `xz` |

## Example

```
{
  "packages": {
    "extra": [
      "cryptsetup"
    ]
  },
  "system": {
    "timezone": "America/Los_Angeles",
    "locale": "en_US.UTF-8",
    "charset": "UTF-8",
    "keymap": "us",
    "hostname": "archstrap",
    "root_password": "hunter2"
  },
  "initrd": {
    "hooks": [
      "base",
      "udev",
      "keyboard",
      "autodetect",
      "keymap",
      "modconf",
      "block",
      "encrypt",
      "filesystems",
      "fsck"
    ]
  }
}
```
