import click
import grass.script as gscript
from grass.script.core import gisenv
import os

@click.command(options_metavar='<Argumenst>')
@click.argument('groupname',metavar='Imagery_group')
@click.argument('subfix',metavar='Output_subfix')
@click.argument('roi',metavar='Region_of interest')
@click.argument('nullval',default=0,metavar='nullvalue')
@click.option('--overwrite/--no-overwrite', default=False, help="Use --overwrite if the output file exists and you what to overwrite it.")

def main(**kwargs):
    	""" This utility clips images of a gruop and create a gorup of the output files.
    	The output raster name will be like: originalname_subfix	  
    	Optionaly it set the null values of the output group
    
	Example: clip_group_region LE72270902000209EDC00_toar madryn madryn --overwrite"""
	wd="outputs"
	if os.path.exists("outputs/")==False:
		os.makedirs(wd)
    	roi = kwargs['roi']
	groupname = kwargs['groupname']
	subfix = kwargs['subfix']
	nullval = kwargs['nullval']
	overwrite = kwargs['overwrite']
    	gscript.run_command('g.region', region=roi)
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
    	mlist=gscript.list_grouped('raster', pattern=groupname+"_"+subfix+"*")[gisenv()['MAPSET']]
    	gscript.run_command("i.group", group=groupname+"_"+subfix, input=mlist)
	for img in mlist:
		print(expression)		
		if overwrite == True:
			gscript.run_command("r.out.gdal",input=img, output=wd+"/"+img+".tif", format="GTiff",overwrite=True)
		if overwrite == False:		
			gscript.run_command(expression) 
	flist=[wd+"/"+orig+".tif" for orig in mlist]
	expression="/usr/bin/gdal_merge.py -o {wd}/{out}_{sf}.tif -separate {inlist}".format(wd=wd,out=groupname,inlist=' '.join(flist),sf=subfix)   
	print(expression)
	os.system(expression)       
	return


if __name__ == '__main__':
    main()
