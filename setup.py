from setuptools import setup, find_packages

setup(
    name="verzugszinsen-b2b",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "dach-verzugszinsen = verzugszinsen_b2b.cli:main",
        ],
    },
)
