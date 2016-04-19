from setuptools import setup

setup(
    name='fourer_parameters_extract.py',
    version='0.1',
    py_modules=['fourer_parameters_extract.py'],
    install_requires=[
        'Click','gdal','numpy','scipy'
    ],
    entry_points='''
        [console_scripts]
        fourer_parameters_extract.py=fourer_parameters_extract.py:cli
    ''',
)
