"""
openff-pydantic
Helper classes for Pydantic compatibility in the OpenFF stack
"""
import sys
from setuptools import setup, find_namespace_packages
import versioneer

short_description = "Helper classes for Pydantic compatibility in the OpenFF stack".split("\n")[0]

# from https://github.com/pytest-dev/pytest-runner#conditional-requirement
needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

try:
    with open("README.md", "r") as handle:
        long_description = handle.read()
except:
    long_description = None


setup(
    name='openff-pydantic',
    author='Matt Thompson',
    author_email='matt.thompson@openforcefield.org',
    description=short_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='MIT',
    packages=find_namespace_packages(),
    include_package_data=True,
    setup_requires=[] + pytest_runner,
)
