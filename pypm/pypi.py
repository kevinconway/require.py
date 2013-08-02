"""This module contains a wrapper around an xmlrpclib connection to PyPi.

Normally putting thin wrappers around things is a bad idea. However, the
choice to wrap the xmlrpclib connection was intended primarily to provide
documentation for the available methods.

What each method is, does, and requires is documented on the PyPi site.
However, that documentation does not come through the rpc library in a way
that is easily consumable. Wrapping the methods gives us the ability to
put in clear docstrings for use with the builtin `help` call.
"""

import xmlrpclib


class Pypi(object):
    """This class is a thin wrapper around the xmlrpclib ServerProxy.

    The purpose of wrapping the rpc object is to provide methods with
    docstrings and repr's instead of the basic rpc magic.
    """

    def __init__(self):

        self.rpc = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')

    def list_packages(self):
        """Retrieve a list of all available packages from pypi."""

        return self.rpc.list_packages()

    def package_releases(self, package_name, show_hidden=False):
        """Retrieve a list of releases registered for the given package_name.

        Returns a list with all version strings if show_hidden is True or only
        the non-hidden ones otherwise.
        """

        return self.rpc.package_releases(package_name, show_hidden)

    def package_roles(self, package_name):
        """Retrieve a list of users and their roles for a given package_name.

        Role is either 'Maintainer' or 'Owner'.
        """

        return self.rpc.package_roles(package_name)

    def user_packages(self, user):
        """Retrieve a list of [role_name, package_name] for a given username.

        Role is either 'Maintainer' or 'Owner'.
        """

        return self.rpc.user_packages(user)

    def release_downloads(self, package_name, version):
        """Retrieve a list of files and download count."""

        return self.rpc.release_downloads(package_name, version)

    def release_urls(self, package_name, version):
        """Retrieve a list of download URLs for the given package release.

        Returns a list of dicts with the following keys:

            url
            packagetype ('sdist', 'bdist', etc)
            filename
            size
            md5_digest
            downloads
            has_sig
            python_version (required version, or 'source', or 'any')
            comment_text
        """

        return self.rpc.release_urls(package_name, version)

    def release_data(self, package_name, version):
        """Retrieve metadata describing a specific package release.

        Returns a dict with keys for:
            name
            version
            stable_version
            author
            author_email
            maintainer
            maintainer_email
            home_page
            license
            summary
            description
            keywords
            platform
            download_url
            classifiers (list of classifier strings)
            requires
            requires_dist
            provides
            provides_dist
            requires_external
            requires_python
            obsoletes
            obsoletes_dist
            project_url
            docs_url (URL of the packages.python.org docs if supplied)
        If the release does not exist, an empty dictionary is returned.
        """

        return self.rpc.release_data(package_name, version)

    def search(self, spec, operator='and'):
        """Search the package database using the indicated search spec.

        The spec may include any of thes keywords below. For example:

            {'description': 'spam'}

        will search description fields. Within the spec, a field's value can
        be a string or a list of strings (the values within the list are
        combined with an OR), for example: {'name': ['foo', 'bar']}.
        Valid keys for the spec dict are listed here. Invalid keys are ignored.

        Possible keys:

            name
            version
            author
            author_email
            maintainer
            maintainer_email
            home_page
            license
            summary
            description
            keywords
            platform
            download_url

        Arguments for different fields are combined using either "and"
        (the default) or "or".

        Example:

            search({'name': 'foo', 'description': 'bar'}, 'or').

        The results are returned as a list of dicts:

            {
                'name': package name,
                'version': package release version,
                'summary': package release summary
            }
        """

        return self.rpc.search(spec, operator)

    def browse(self, classifiers):
        """Retrieve a list of (name, version) pairs.

        List contains all releases classified with all of the given
        classifiers. 'classifiers' must be a list of Trove classifier strings.
        """

        return self.rpc.browse(classifiers)
