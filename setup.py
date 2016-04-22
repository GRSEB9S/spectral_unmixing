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
	end_rast_from_vect=end_rast_from_vect:main
	export_endmembers=export_endmembers:main
	#unmix=unmix:main
    ''',
)
