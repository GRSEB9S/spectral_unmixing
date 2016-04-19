from setuptools import setup

setup(
    name='fourier.py',
    version='0.1',
    py_modules=['fourier'],
    install_requires=[
        'Click','gdal','numpy','scipy'
    ],
    entry_points='''
        [console_scripts]
        fourer.py=fourier.py:cli
    ''',
)
