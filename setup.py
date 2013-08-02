from setuptools import setup

setup(
    name="pypm",
    version="0.0.1",
    description="A better way to manage and import dependencies.",
    long_description=open('README.rst').read(),
    author="Kevin Conway",
    author_email="kevinjacobconway@gmail.com",
    url="https://github.com/kevinconway/pypm",
    packages=['pypm'],
    scripts=['scripts/pypm'],
    license=open('LICENSE').read(),
    requires=[],
)
