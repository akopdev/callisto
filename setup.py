from setuptools import find_packages, setup

from callisto import __version__

setup(
    name="callisto",
    version=__version__,
    packages=find_packages(),
    extras_require={
        "dev": [
            "setuptools>65.5.0",
            "flake8",
            "pydocstyle",
            "piprot",
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
            "isort",
            "black",
            "safety",
            "aioresponses",
        ],
    },
)
