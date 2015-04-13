"""Command line scripts for managing dependencies."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import os
import shlex
import subprocess
import sys


def common_arguments():
    """Generate a parser with all common arguments configured."""
    parser = argparse.ArgumentParser(description='Manage Python dependencies.')
    parser.add_argument(
        '--target',
        required=True,
        help='The target Python package to install dependencies in.',
    )
    parser.add_argument(
        '--pymodule-name',
        default='.pymodules',
        help='The name of the pymodules directory to create.',
    )
    return parser


def install_arguments(parser=None):
    """Attach a subparser for the install command."""
    parser = parser or common_arguments()
    sub_parser = parser.add_subparsers().add_parser('install')
    sub_parser.add_argument(
        'dependencies',
        nargs='+',
    )
    return parser


def generate_install_command(target, pymodule='.pymodule', dependencies=()):
    """Generate a pip command to install dependencies."""
    if not dependencies:

        raise ValueError('Must install at least one dependency.')

    target = os.path.abspath(target)
    command = 'pip install --target {0} --upgrade '.format(
        os.path.join(target, pymodule)
    )
    command_args = []
    for dependency in dependencies:

        if os.path.isfile(dependency):

            command_args.append('-r {0} '.format(dependency))
            continue

        command_args.append('{0} '.format(dependency))

    command = (command + ''.join(command_args)).encode('ascii')
    if sys.version_info[0] > 2:

        command = command.decode('utf8')

    return shlex.split(command)


def install(argv=None):
    """Install a dependency."""
    parser = install_arguments()
    args = parser.parse_args(argv)
    command = generate_install_command(
        args.target,
        args.pymodule_name,
        args.dependencies,
    )
    subprocess.check_call(command)
