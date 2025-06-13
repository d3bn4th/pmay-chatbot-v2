from setuptools import setup, find_packages

setup(
    name="pmay-chatbot-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "chromadb",
        "langchain",
        "langchain-community",
        "langchain-core",
        "langchain-text-splitters",
        "ollama",
        "sentence-transformers",
        "torch",
    ],
    python_requires=">=3.8",
) 