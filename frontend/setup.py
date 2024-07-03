from setuptools import setup, find_packages

setup(
    name='fronted-AIWantTheJob',                         # Nombre paquete
    version='0.9',
    description="Chatbot web frontend",
    author="Jorge Alcalde Vesteiro",
    author_email="jorge.alcalde@rai.usc.es",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit==1.35.0',
        'streamlit-chat==0.1.1',
        'pandas==2.0.2',
        'numpy==1.24.3',
        'pytest==7.1.2',
        'pytest-asyncio==0.23.7',
    ],
    extras_require={
        'dev': ['pytest==7.1.2']
    },
)