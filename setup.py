import os
from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="endfield",
    version="0.0.1",
    author="Kevin L.",
    author_email="kevinliu@vt.com",
    description="Arknights: Endfield Command Line Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ReZeroE/Endfield",

    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    license="MIT",

    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],

    keywords=["endfield", "example"],
    install_requires=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")).read().splitlines(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "endfield = endfield.main:main",
            "ef = endfield.main:main",
        ],
    },
)