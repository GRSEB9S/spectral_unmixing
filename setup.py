from setuptools import setup

setup(
    name='spectral_unmixing',
    version='0.1',
    py_modules=['spectral_unmixing'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        clip_group_region=clip_group_region:main
	endmembers_from_vector=endmembers_from_vector:main
	endarray_to_raster=endarray_to_raster:main
	export_endmembers=export_endmembers:main
	unmix=unmix:main
    ''',
)
