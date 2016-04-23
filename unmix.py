import click
import otbApplication
import grass.script as gscript

@click.command(options_metavar='<Options>')
@click.argument('gname',metavar='ImageryGroup')
@click.argument('subfix',metavar='subfix')
#@click.argument('endrastername',metavar='EndmemberRasters')
@click.argument('output',metavar='output')

def main(**kwargs):
	""" 
	Example:  unmix LE72270902000209EDC00_toar madryn unmix 
	"""
	wd="outputs"	
	gname = kwargs['gname']
	subfix = kwargs['subfix']
	output = kwargs['output']
	out = "./"+wd+"/"+output	
	endrastername="./"+wd+"/"+gname+"_endmembers.tif"	
	image = "./"+wd+"/"+gname+"_"+subfix+".tif"
	# The following line creates an instance of the HyperspectralUnmixing application	
	HyperspectralUnmixing=otbApplication.Registry.CreateApplication("HyperspectralUnmixing")
	# The following lines set all the application parameters:	
	HyperspectralUnmixing.SetParameterString("in",str(image))
	HyperspectralUnmixing.SetParameterString("ie",str(endrastername))
	HyperspectralUnmixing.SetParameterString("out",str(out)+".tif")
	HyperspectralUnmixing.SetParameterString("ua","ucls")
	# The following line execute the application
	HyperspectralUnmixing.ExecuteAndWriteOutput()
	gscript.run_command("r.in.gdal",input=str(out)+".tif", output=str(output))
	return

if __name__ == '__main__':
    main()

