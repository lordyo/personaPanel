from setuptools import setup, find_packages

setup(
    name="persona_framework",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "dspy-ai",
        "pyyaml",
    ],
    author="AI Developer",
    author_email="ai@example.com",
    description="A DSPy-based framework for generating and utilizing AI personas",
    long_description=open("project_docs/concept.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/persona_framework",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    package_data={
        "persona_framework": [
            "config/dimensions/*.yaml",
            "config/settings.yaml",
        ],
    },
) 