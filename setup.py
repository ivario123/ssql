from setuptools import setup, find_packages

setup(
    name="ssql",
    version="0.0.1",
    author_email="ivajns-9@student.ltu.se",
    packages=find_packages(),
    install_requires=[
        "sshtunnel",
        "mysql",
        "mysql-connector-python"
    ],
)
