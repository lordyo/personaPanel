from setuptools import setup, find_packages

setup(
    name="persona_panel",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    author="PersonaPanel Team",
    author_email="example@example.com",
    description="A comprehensive application for managing and interacting with different AI personas",
    keywords="ai, personas, chat, management",
    python_requires=">=3.8",
) 