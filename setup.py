from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="b2b-verzugszinsen",
    version="1.0.0",
    author="DACH Digitalwerk",
    author_email="dach.digitalwerk@gmail.com",
    description="Taggenaue kaufmännische Verzugszinsberechnung & Mahnwesen im DACH-Raum (§ 288 BGB, § 456 UGB, Art. 104 OR)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DACHDigitalwerk/verzugszinsen-mahnung-rechner-b2b",
    project_urls={
        "Live Rechner": "https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/",
        "B2B Ratgeber": "https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html",
        "Bug Tracker": "https://github.com/DACHDigitalwerk/verzugszinsen-mahnung-rechner-b2b/issues",
    },
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "b2b-zinsen=b2b_verzugszinsen.cli:main",
        ],
    },
)
