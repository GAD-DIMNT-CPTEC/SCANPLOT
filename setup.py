# SCANPLOT - Um sistema de plotagem simples para o SCANTEC
# CC-BY-NC-SA-4.0 2022 INPE

from setuptools import setup

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
    url="https://github.com/GAD-DIMNT-CPTEC/SCANPLOT",
    py_modules=['scanplot', 'core_scanplot', 'data_structures', 'aux_functions',
                'global_variables', 'plot_functions', 'gui_functions'],
    install_requires=['numpy', 'matplotlib', 'pandas', 'seaborn', 'SkillMetrics', 'scipy'],
    extras_require={
        'fields': ['xarray', 'cartopy'],
        'gui': ['xarray', 'cartopy', 'panel>=1.5,<2', 'param', 'holoviews', 'hvplot', 'geoviews'],
        'test': ['pytest', 'build'],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.8.2',
)
