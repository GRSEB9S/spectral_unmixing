import click
import sys, os
sys.path.append('/usr/lib/otb/python')
import otbApplication
import grass.script as gscript

@click.command(options_metavar='<Options>')
@click.argument('raster_name',metavar='raster_name')
@click.argument('endrastername',metavar='EndmemberRasters')
@click.argument('output',metavar='output')

def main(**kwargs):
	""" 
	This utility performes spectral unmixing of the images stored in the 'gname' group, using the endmembers created with `end_rast_from_vect`

	Example:  uunmix outputs/LE72270902000209EDC00_toar.tif outputs/LE72270902000209EDC00_toar_endmembers.tif outputs/unmixed_image.tif
	"""
	""" Set GRASS environmental variables"""	
	os.environ['GRASS_MESSAGE_FORMAT'] = 'silent' 
	os.environ['GRASS_VERBOSE='] = "0" 
	wd="outputs"	
	raster_name = str(kwargs['raster_name'])
	output = str(kwargs['output'])
	endrastername = str(kwargs['endrastername'])		
	image = raster_name
	print(image)
	# The following line creates an instance of the HyperspectralUnmixing application	
	HyperspectralUnmixing=otbApplication.Registry.CreateApplication("HyperspectralUnmixing")
	# The following lines set all the application parameters:	
	HyperspectralUnmixing.SetParameterString("in",image)
	HyperspectralUnmixing.SetParameterString("ie",endrastername)
	HyperspectralUnmixing.SetParameterString("out",output)
	HyperspectralUnmixing.SetParameterString("ua","ucls")
	# The following line execute the application
	HyperspectralUnmixing.ExecuteAndWriteOutput()
	name=str.split(str.split(output,".tif")[0],"/")[1]

	gscript.run_command("r.in.gdal",input=output, output=name)
	return

if __name__ == '__main__':
    main()

