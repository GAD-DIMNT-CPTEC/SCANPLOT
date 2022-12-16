# SCANPLOT - Um sistema de plotagem simples para o SCANTEC
# CC-BY-NC-SA-4.0 2022 INPE

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="SCANPLOT", 
    description="Um sistema de plotagem simples para o SCANTEC",
    version="1.1.0",
    author="Carlos Frederico Bastarz",
    author_email="cfbastarz@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cfbastarz/SCANPLOT",
    packages=find_packages(include=['.']),
    install_requires=['numpy','matplotlib','xarray','pandas','seaborn','SkillMetrics','scipy'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.8.2',
)
