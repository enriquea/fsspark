from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="fslite",
    version="0.0.1",
    url="https://github.com/bigbio/fslite",
    license="Apache-2.0",
    author="Enrique Audain Martinez",
    author_email="enrique.audain@gmail.com",
    description="Feature selection in Spark",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "networkx",
        "setuptools",
        "pandas",
        "pyarrow",
        "scikit-learn",
        "scipy",
    ],
    classifiers=[
        # Classifiers for your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.9.0",
)
