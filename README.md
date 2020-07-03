# archstrap

*Over-engineered bootstrapping for an Arch Linux system*

## Summary

`archstrap` bootstraps an Arch Linux system from the live installer media via a
configuration file.

## Usage

`archstrap` is an executable Python application. You should be able to run it
directly (`archstrap ...`), or with Python (`python archstrap ...`).

```
usage: archstrap [-h] [--doc] [--version] [--install-root INSTALL_ROOT]
                 [--mode {exec,dryrun,shell}] [--debug | --quiet]
                 specification
```

### Modes

`archstrap` can run in one of three modes: `exec`, `dryrun`, or `shell`. The
desired mode can be selected with the `--mode` command-line argument.

`exec`: This mode runs commands on the same system that `archstrap` is being
invoked on.

`dryrun`: This mode logs the commands that would be run in `exec` mode, but does
not run them.

`shell`: This mode outputs the commands that would be run to stdout in the
format of a shell script.

### Output

By default `archstrap` will product some modest output while running. You can
control this with one of the `--debug` or `--quiet` command-line flags.
`--debug` will enable far more logging output, while `--quiet` will trim the
output down to error-reporting only.

### Specification

`archstrap` loads a specification from a JSON file that you provide using last
positional command-line argument. This file describes the way to bootstrap your
system. The complete specification format is documented
[here](doc/SPECIFICATION_FORMAT.md). An [example specification
file](data/example.spec.json) has been provided.

## Packaging / Distribution

`archstrap` uses `PyInstaller` to package distributable releases. You can use the
make target `dist` to create your own distribution:

```
make dist
```

This will create (among other things) the output file `./dist/archstrap` which
is a self-contained executable that you can redeploy to any Linux machine.

Note that PyInstaller requires that `ldd` and `objcopy` be available on your
PATH. Install them through your distribution's package manager. They are usually
found in the `binutils` package.

## Tests

`archstrap` has several different test suites, each with their own intent and
requirements. Some of these test suites must be run as `root` because they make
changes to the system they are running on. It is recommended that you run these
tests in VM - such as the one provided by this project's
[Vagrantfile](Vagrantfile).

You can use Vagrant for this purpose with the following commands:

```
vagrant up --provision
vagrant ssh
cd /vagrant
sudo su
```

You can invoke all tests with a single command:

```
make test
```

Or you can invoke specific test suites explicitly:

```
make unit_test
make dist_test
```

## License

`archstrap` is licensed under either of the following, at your option:

* Apache License, Version 2.0 ([LICENSE-APACHE](license/LICENSE-APACHE) or
  http://www.apache.org/licenses/LICENSE-2.0)
* MIT license ([LICENSE-MIT](license/LICENSE-MIT) or
  http://opensource.org/licenses/MIT)

## Contributing

Contributions are welcome in the form of bug reports, feature requests, or pull
requests.

Contribution to `archstrap` is organized under the terms of the [Contributor
Covenant](doc/CONTRIBUTOR_COVENANT.md).
