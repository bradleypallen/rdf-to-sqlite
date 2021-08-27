from setuptools import setup, find_packages
import io
import os

VERSION = "0.2"

def get_long_description():
    with io.open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()

setup(
    name="rdf-to-sqlite",
    description="Utility for converting an RDF file to SQLite",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Bradley P. Allen",
    version=VERSION,
    license="MIT License",
    packages=find_packages(),
    install_requires=["click>=8.0.1", "rdflib>=6.0.0", "sqlite-utils>=3.12"],
    setup_requires=["pytest-runner"],
    extras_require={"test": ["pytest"]},
    entry_points="""
        [console_scripts]
        rdf-to-sqlite=rdf_to_sqlite.cli:cli
    """,
    tests_require=["rdf-to-sqlite[test]"],
    url="https://github.com/bradleypallen/rdf-to-sqlite",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
