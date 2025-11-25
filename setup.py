"""
Nagarro Agentic Services Platform
AI-powered cloud migration and modernization platform
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="nagarro-agentic-services",
    version="0.1.0",
    author="Nagarro",
    author_email="agentic-services@nagarro.com",
    description="AI-powered cloud migration platform with specialized agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nagarro/agentic-services",
    project_urls={
        "Bug Tracker": "https://github.com/nagarro/agentic-services/issues",
        "Documentation": "https://github.com/nagarro/agentic-services/blob/main/README.md",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.11.1",
            "black>=23.7.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "pre-commit>=3.3.3",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentic-services=agentic_services.cli:main",
        ],
    },
)
