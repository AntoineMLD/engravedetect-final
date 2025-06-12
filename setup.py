from setuptools import setup, find_packages

setup(
    name="engravedetect",
    version="0.1.0",
    description="Système de gestion et d'analyse de données optiques",
    author="Antoine",
    packages=find_packages(),
    install_requires=[
        "scrapy>=2.8.0",
        "pandas>=2.0.0",
        "pyodbc>=4.0.39",
        "python-dotenv>=1.0.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "SQLAlchemy>=2.0.0",
        "numpy>=1.24.0",
        "logging>=0.5.1.2",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.4.2",
        "pydantic-settings>=2.0.3",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'run-pipeline=src.orchestrator.pipeline_manager:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
) 