from setuptools import setup

with open('README.rst') as f:

    long_description = f.read()

setup(
    name="requirepy",
    version="0.1.0",
    description="A better way to manage and import dependencies.",
    long_description=long_description,
    author="Kevin Conway",
    author_email="kevinjacobconway@gmail.com",
    url="https://github.com/kevinconway/require.py",
    packages=['require'],
    license='Apache2',
    entry_points={
        'console_scripts': [
            'requirepy = require.cmd:install',
        ],
    },
)
