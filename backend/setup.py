from setuptools import setup, find_packages

setup(
    name='backend-AIWantTheJob',                         # Nombre paquete
    version='0.9',
    description="Chatbot backend for the interview system",
    author="Jorge Alcalde Vesteiro",
    author_email="jorge.alcalde@rai.usc.es",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy==1.26.4',
        'flask==3.0.3',
        'flask-cors==4.0.1',
        'torch==2.3.1',
        'transformers==4.41.2',
        'huggingface-hub==0.23.3',
        'langchain==0.1.7',
        'langchain_community==0.0.20',
        'langchain-core==0.1.23',
        'langchain-text-splitters==0.2.1',
        'nemoguardrails==0.9.0',
        'chromadb==0.5.0',
        'pyftpdlib==1.5.0',
        'sentence-transformers==3.0.1',
        'bitsandbytes==0.43.1',
        'accelerate==0.31.0',
        'ipykernel==6.29.3',
        'ipython==8.22.2',
        'ipywidgets==8.1.3',
        'pytest==7.1.2',
        'pytest-asyncio==0.23.7'
    ],
    extras_require={
        'dev': ['pytest==7.1.2']
    },
)