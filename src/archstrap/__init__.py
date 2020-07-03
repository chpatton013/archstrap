from archstrap.mode import make_mode
from archstrap.specification import Specification


def run(specification: Specification, mode_name: str, install_root: str):
    mode = make_mode(mode_name)
    specification.apply(install_root, mode)
