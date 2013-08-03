from setuptools import setup

with open('README.rst') as f:

    long_description = f.read()

with open('LICENSE') as f:

    license = f.read()

setup(
    name="pypm",
    version="0.0.1",
    description="A better way to manage and import dependencies.",
    long_description=long_description,
    author="Kevin Conway",
    author_email="kevinjacobconway@gmail.com",
    url="https://github.com/kevinconway/pypm",
    packages=['pypm'],
    scripts=['scripts/pypm'],
    license=license,
    requires=[],
)
