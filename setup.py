"""
Setup script for the Empathy Engine package.
"""

from setuptools import setup, find_packages

setup(
    name="empathy-engine",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "textblob",
        "nltk",
        "pyttsx3",
        "flask",
        "transformers",
        "torch",
        "gtts",
        "python-dotenv",
        "scipy",
        "numpy",
    ],
    entry_points={
        'console_scripts': [
            'empathy-engine=main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A service that dynamically modulates the vocal characteristics of synthesized speech based on emotions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="text-to-speech, emotion, ai, nlp",
    url="https://github.com/yourusername/empathy-engine",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
)
