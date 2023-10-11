"""
setup.py
====================
A Python script for packaging and distributing the 'tutgen' tool.

This script defines the metadata and dependencies for the 'tutgen' package.

Author: Roman Parise
Email: pariseroman@gmail.com
"""

from setuptools import setup, find_packages

# Read the requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="tutgen",
    version="1.0.0",
    description="A Python tool for generating programming tutorials from JSON blueprints",
    author="Roman Parise",
    author_email="pariseroman@gmail.com",
    url="https://github.com/yourusername/tutgen",
    packages=find_packages(),
    install_requires=requirements,  # Use the requirements list
    entry_points={
        "console_scripts": [
            "tutgen = tutgen.main:main",
        ],
    },
    package_data={"tutgen": ["animation.template"]},
)
