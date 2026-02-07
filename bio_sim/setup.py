"""Setup configuration for bio-sim package."""
from setuptools import setup, find_packages

setup(
    name="bio-sim",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pygame>=2.5.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "pylint>=2.17.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
)
