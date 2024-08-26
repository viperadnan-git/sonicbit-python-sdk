import re

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version() -> str:
    with open("sonicbit/__init__.py", "r") as f:
        version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)
        return version


setup(
    name="sonicbit",
    version=get_version(),
    author="Adnan Ahmad",
    author_email="viperadnan@gmail.com",
    description="An unofficial Python SDK for SonicBit which uses the internal API to interact with the application.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/viperadnan-git/sonicbit-python-sdk",
    license="GNU General Public License v3.0",
    keywords="sonicbit python sdk",
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
