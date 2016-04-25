import click
import grass.script as gscript
from grass.script.core import gisenv
import os

@click.command(options_metavar='<Argumenst>')
@click.argument('groupname',metavar='Imagery_group')
@click.argument('subfix',metavar='Output_subfix')
@click.argument('roi',metavar='Region_of interest')
@click.argument('nullval',default=0,metavar='nullvalue')
@click.argument('wd',default="outputs",metavar="Working_directory")
@click.option('--overwrite/--no-overwrite', default=False, help="Use --overwrite if the output file exists and you what to overwrite it.")

def main(**kwargs):
    	""" This utility clips, exports and stack all the images of a group (As otb_Hyperspectral_unmixing needs).
    	The output raster name will be like: originalname_subfix and will be stored in the wd folder.	  
    	Optionally it set the null values of the output images
    
	Example: clip_group_region LE72270902000209EDC00_toar madryn madryn --overwrite"""

	""" Set GRASS environmental variables"""	
	os.environ['GRASS_MESSAGE_FORMAT'] = 'silent' 
	os.environ['GRASS_VERBOSE='] = "0" 
	print("Processing... Please be patient")
	""" Pass the CL arguments """    	
	wd = kwargs['wd']
    	roi = kwargs['roi']
	groupname = kwargs['groupname']
	subfix = kwargs['subfix']
	nullval = kwargs['nullval']
	""" Create the output folder if not present """
	overwrite = kwargs['overwrite']
	if os.path.exists(wd)==False:
		os.makedirs(wd)
	"""  Set GRASS working region """
    	gscript.run_command('g.region', region=roi)
	""" Clip each raster on the group and set null value"""
    	grouplist=gscript.read_command("i.group", group=groupname, flags="g" ).split()
    	for raster in grouplist:
        	name=raster.split("@")[0]
        	band= name.split(".")[1]
        	rout= name.split(".")[0]+"_"+subfix
        	expression="{rout}.{b} = {rin}".format(rin=name,rout=rout,b=band)
		if overwrite == True:
			gscript.mapcalc(expression,overwrite=True)
		if overwrite == False:		
			gscript.mapcalc(expression)                                                          
        	gscript.run_command('r.null', map="{rout}.{b}".format(rout=rout,b=band),setnull=nullval)
  	""" Create a list of images to add to the new group (clipped images)"""
  	mlist=gscript.list_grouped('raster', pattern=groupname+"_"+subfix+"*")[gisenv()['MAPSET']]
    	gscript.run_command("i.group", group=groupname+"_"+subfix, input=mlist)
	""" Export the clipped images"""
	for img in mlist:		
		if overwrite == True:
			gscript.run_command("r.out.gdal",input=img, output=wd+"/"+img+".tif", format="GTiff",overwrite=True)
		if overwrite == False:		
			gscript.run_command("r.out.gdal",input=img, output=wd+"/"+img+".tif", format="GTiff",overwrite=False)
	flist=[wd+"/"+orig+".tif" for orig in mlist]
	""" Stack the exported images"""
	expression="gdal_merge.py -o {wd}/{out}_{sf}.tif -separate {inlist}".format(wd=wd,out=groupname,inlist=' '.join(flist),sf=subfix)   
	os.system(expression)       
	return


if __name__ == '__main__':
    main()
