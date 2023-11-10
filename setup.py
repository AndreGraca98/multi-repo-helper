from pathlib import Path

from setuptools import find_packages, setup
from setuptools.command.install import install

from _setup import setup_executable
from _version import __version__


class PostInstallCommand(install):
    def run(self):
        super().run()
        setup_executable()


setup(
    name="mrh",
    version=__version__,
    author="André Graça",
    author_email="andrepgraca+mrh@gmail.com",
    description="Multi repository helper",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    platforms="Python",
    cmdclass={
        "install": PostInstallCommand,
    },
)
