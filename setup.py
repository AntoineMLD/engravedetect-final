from setuptools import setup, find_packages

setup(
    name="engravedetect",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "scrapy",
        "pandas",
        "pyodbc",
        "python-dotenv",
        "beautifulsoup4"
    ],
    python_requires=">=3.8",
) 