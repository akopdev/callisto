from setuptools import find_packages, setup

setup(
    name="callisto",
    version="0.2.0",
    packages=find_packages(),
    requires=["rich"],
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
