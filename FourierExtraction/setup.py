from setuptools import setup

setup(
    name='fourier_extract',
    version='0.1',
    py_modules=['fourier_extract'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        fourier_extract=fourier_extract:cli
    ''',
)

