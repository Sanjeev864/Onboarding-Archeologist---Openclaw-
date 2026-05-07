from setuptools import setup, find_packages

setup(
    name="archaeologist",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0",
        "pydantic>=2.0.0,<2.11.0",
        "pydantic-settings>=2.0.0",
        "sqlalchemy>=2.0.0",
        "httpx>=0.24.0",
        "GitPython>=3.1.0",
        "python-dotenv>=1.0.0",
        "PyGithub>=2.0.0",
        "python-telegram-bot==20.4",
    ],
    python_requires=">=3.10",
)
