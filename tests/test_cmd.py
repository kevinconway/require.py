"""Test suite for the custom import logic."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import shlex
import sys

from require import cmd


def test_pip_command_generates():
    """Check if pip commands are generated correctly."""
    test_requirements = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'test-requirements.txt',
    ))
    command = cmd.generate_install_command(
        target='test',
        pymodule='.testmodules',
        dependencies=('pip', test_requirements),
    )
    expected_command = 'pip install --target {0} --upgrade pip -r {1}'.format(
        os.path.abspath(os.path.join(
            'test',
            '.testmodules',
        )),
        test_requirements,
    ).encode('ascii')
    if sys.version_info[0] > 2:

        expected_command = expected_command.decode('utf8')

    assert command == shlex.split(expected_command)
