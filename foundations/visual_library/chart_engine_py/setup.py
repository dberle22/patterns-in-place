"""
Compatibility shim for older pip versions that still expect setup.py for
editable installs even when the package is configured through pyproject.toml.
"""

from setuptools import setup


setup()
