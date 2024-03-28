from .. import __pkgname__, __version__


def get_package_version():
    return {
        "pkgname": __pkgname__,
        "version": __version__,
    }
