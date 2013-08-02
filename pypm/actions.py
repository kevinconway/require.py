"""This module contains all of the PyPi and package installation actions.

Functions in this module may be used on their own. However, their primary
purpose is for use in the `pypm` cli.
"""

import os
import sys
import re

import collections
import urllib2
import tempfile
import shutil
import tarfile

from distutils.core import run_setup
from distutils.version import LooseVersion

from .pypi import Pypi

pypi_client = Pypi()


def install_package_dependencies(dist_package_path=None):
    """This function locally install all dependencies needed for a package.

    If a `dist_package_path` is provided, that location will be used at the
    directory containing the `setup.py` script. The dist_package_path must be
    an absolute path.

    If no `dist_package_path` is provided then the current working directory is
    assumed to be the target.
    """

    dist_package_path = dist_package_path or os.getcwd()

    sys.path.append(dist_package_path)

    setup_path = os.path.join(dist_package_path, 'setup.py')

    setup = run_setup(setup_path)

    # Only find first root level package.
    package = [p for p in setup.packages if '.' not in p]

    if len(package) < 1:

        raise Exception("Could not find any Python packages for "
                        "distribution package (%s)." % (dist_package_path,))

    package = package[0]

    py_package_path = os.path.join(dist_package_path, package)

    pymodules_path = make_pymodules_directory(target_path=py_package_path)

    requirements = (parse_requirement(r) for r in setup.get_requires())
    install_requires = []

    if (hasattr(setup, 'install_requires') and
        setup.install_requires is not None):

        #######################################################################
        # Hacky hack for setup.py's that use strings instead of the canonical
        # lists for requirements declarations.
        # TODO(kevinconway): Create some sort of parsing function to fix this.
        if type(setup.install_requires) is str:

            setup.install_requires = [setup.install_requires]
        #######################################################################

        install_requires = (parse_requirement(r)
                            for r in setup.install_requires)

    def all_requirements():
        """Merge all requires into one generator."""

        try:

            for r in requirements:

                yield r

        except StopIteration:

            pass

        try:

            for r in install_requires:

                yield r

        except StopIteration:

            pass

    # Grap PyPi releases for deps.
    releases = (get_release(package=r.package,
                            comparison=r.comparison,
                            version=r.version) for r in all_requirements())

    downloads = (download_release(package=r.package + '-dist',
                                  handle=r.handle,
                                  target_path=pymodules_path)
                 for r in releases)

    # Execute the pipeline and generate the final list of directories.
    downloads = list(downloads)

    for d in downloads:

        install_package_dependencies(d.path)

        # Move deps into .pymodules dir.
        os.renames(os.path.join(d.path, d.package),
                   os.path.join(pymodules_path, d.package))

        shutil.rmtree(d.path)


def make_pymodules_directory(target_path=None):
    """This function creates a .pymodules folder at the given path.

    This function will create the missing intermediate folders if needed.

    The `target_path` must be an absolute path.

    If the `target_path` is not given then the current working directory will
    be used.

    The final path of the directory is returned.
    """

    target_path = target_path or os.getcwd()

    pymodules_dir = os.path.join(target_path, '.pymodules')

    if not os.path.isdir(pymodules_dir):
        os.mkdir(pymodules_dir)

    return pymodules_dir


def parse_requirement(requirement):
    """This function generates a package name and version from `requirement`.

    The `requirement` may be in the PEP386 form or in the pip form.

    Examples:

        -   somepackage (>3.0.0)

        -   somepackage==1.2.3
    """

    # Convert PEP style versions into pip style versions.
    requirement = (requirement
                   .replace(" ", "")
                   .replace("(", "")
                   .replace(")", "")
                   )

    package = requirement
    comparison = None
    version = None

    comparisons = "(==|<=|>=|!=|<|>)"

    package_data = re.split(comparisons, package)

    ###########################################################################
    # Hacky hack to work around multiple version requirement strings for a
    # single module.
    # TODO(kevinconway): Create some sort of parsing function to fix this.
    if len(package_data) > 3:

        package_data = package_data[:3]
    ###########################################################################

    print requirement
    print package_data

    # If the the requirement contains a version then unpack it into pieces.
    if len(package_data) > 1:

        package, comparison, version = package_data

    pkg = collections.namedtuple('PackageData',
                                 ['package', 'comparison', 'version']
                                 )

    pkg.package = package
    pkg.comparison = comparison
    pkg.version = version

    return pkg


def get_release(package, comparison=None, version=None):
    """This package grabs a file handle for the most applicable release.

    The `comparison` and `version` are optional, but must be provided together.
    If they are not supplied then the most recent version of `package` will
    be retrieved.

    The handle returned in the tuple is a file-like object that can be read
    from.
    """

    available_versions = pypi_client.package_releases(package, True)

    if len(available_versions) < 1:

        raise Exception("No releases found for package (%s)." % (package,))

    final_version = None

    if comparison is not None and version is not None:

        target_version = LooseVersion(version)

        matching_versions = (LooseVersion(v) for v in available_versions)

        if comparison == '==':

            matching_versions = (v for v in matching_versions
                                 if v == target_version)

        elif comparison == '<':

            matching_versions = (v for v in matching_versions
                                 if v < target_version)

        elif comparison == '>':

            matching_versions = (v for v in matching_versions
                                 if v > target_version)

        elif comparison == '<=':

            matching_versions = (v for v in matching_versions
                                 if v <= target_version)

        elif comparison == '>=':

            matching_versions = (v for v in matching_versions
                                 if v >= target_version)

        elif comparison == '!=':

            matching_versions = (v for v in matching_versions
                                 if v != target_version)

        matching_versions = list(matching_versions)

        if len(matching_versions) < 1:

            raise Exception("Could not find a compatible version for %r %r %r"
                            % (package, comparison, version))

        final_version = matching_versions[0].vstring

    else:

        # Use most recent is not version requested.
        final_version = available_versions[0]

    release = collections.namedtuple('Release', ['package', 'handle'])

    release.package = package
    release.handle = get_release_handle(package, final_version)

    return release


def get_release_handle(package, version):
    """Open the download link for a release and return the handle for it.

    The handle returned is a file like object that can be read from.
    """

    urls = pypi_client.release_urls(package, version)

    urls = (u for u in urls if u['packagetype'] == 'sdist')

    urls = list(urls)

    if len(urls) < 1:

        raise Exception("Could not find any source distribution release urls "
                        "for %r %r" % (package, version,))

    release_url = urls[0]['url']

    return urllib2.urlopen(release_url)


def download_release(package, handle, target_path=None):
    """Download, unpack, and move the release to the given path.

    The `target_path` must be an absolute path. If `target_path` is not given
    then the current directory is used.

    This function returns the path that it downloaded the package to.
    """

    target_path = target_path or os.getcwd()
    target_path = os.path.join(target_path, package)

    tempdir = tempfile.mkdtemp()
    tarpath = os.path.join(tempdir, 'package')
    tarball = open(tarpath, 'wb')
    tarball.write(handle.read())
    tarball.close()

    tarball = open(tarpath, 'rb')
    tarball = tarfile.open(tarpath, fileobj=tarball)
    unpacked_path = os.path.join(tempdir, package)
    tarball.extractall(unpacked_path)
    package_folder_name = [n for n in tarball.getnames() if '/' not in n][0]
    tarball.close()

    os.renames(os.path.join(unpacked_path, package_folder_name), target_path)

    download = collections.namedtuple('Download', ['package', 'path'])
    download.package = package
    download.path = target_path

    return download
