from setuptools import setup, find_packages

setup(
    name="biodbcore",
    version="0.1.3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas==2.2.3",
        "numpy==2.2.4",
        "pyarrow==19.0.0",
        "python-dateutil==2.9.0.post0",
        "pytz==2025.2",
        "requests==2.32.3",
        "tqdm==4.67.1",
        "urllib3==2.3.0",
        "certifi==2025.1.31",
        "charset-normalizer==3.4.1",
        "idna==3.10",
        "six==1.17.0"
    ],
    entry_points={
        "console_scripts": [
            "biodbcore=biodbcore.biodbcore:main",
        ]
    },
    python_requires=">=3.10",
    author="Ondřej Sloup",
    author_email="dev@lupphes.com",
    description="BioDbCoRe - Biological Database Core Tool",
    url="https://github.com/Lupphes/biodbcore",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
