"""Setup script for Etsy AI Agent"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="etsy-ai-agent",
    version="1.0.0",
    author="AI Assistant",
    author_email="noreply@example.com",
    description="AI智能体帮助你在Etsy上销售数字产品赚钱",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/etsy-ai-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "etsy-agent=main:app",
        ],
    },
)
