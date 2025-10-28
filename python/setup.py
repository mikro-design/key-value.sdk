"""Setup configuration for keyvalue-client package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="keyvalue-client",
    version="0.1.0",
    author="",
    author_email="",
    description="Python client for Key-Value store with memorable 5-word tokens",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mikro-design/key-value.py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "encryption": [
            "cryptography>=41.0.0",
        ],
        "clipboard": [
            "pyperclip>=1.8.0",
        ],
        "webhook": [
            "flask>=2.0.0",
        ],
    ],
    entry_points={
        "console_scripts": [
            # Could add CLI tools here
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/mikro-design/key-value.py/issues",
        "Source": "https://github.com/mikro-design/key-value.py",
        "Documentation": "https://key-value.co/docs",
    },
)
