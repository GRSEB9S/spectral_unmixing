import click
import grass.script as gscript
from grass.script.core import gisenv
import os
import sqlite3
import pandas
import numpy,glob

@click.command(options_metavar='<Options>')
@click.argument('vname',metavar='endmember_location')
@click.argument('vclasscol',metavar='class_column')
@click.argument('gname',metavar='imagery_group')
@click.argument('endrastname',metavar='end_raster')
@click.argument('roi',metavar='region')
@click.option('--overwrite/--no-overwrite', default=True, help="Use --overwrite if the output file exists and you what to overwrite it.")
@click.argument('wd',default="outputs",metavar="Working_directory")

def main(**kwargs):
	
	""" This utility creates the endmembers raster image (end_raster) to use for unmixing.
	 The endmembers will be stored as a multiband image, so that each band (b) holds the reflectance value
	of the (e) endmember, resulting in a b x 1 x e raster.
	
	It takes the location of the pure pixels for each class from the point vector (endmember_location) and the column 'class_column'.	
	
	Example: end_rast_from_vect endmembers class LE72270902000209EDC00_toar end madryn overwrite=True"""
	
	""" Set GRASS environmental variables"""	
	os.environ['GRASS_MESSAGE_FORMAT'] = 'silent' 
	os.environ['GRASS_VERBOSE='] = "0" 
	print("Processing... Please be patient")	
	# Pass CL argument		
	wd = str(kwargs['wd'])
	groupname = str(kwargs['gname'])	
	vname = str(kwargs['vname'])
	endrastname = str(kwargs['endrastname'])
	vclasscol = str(kwargs['vclasscol'])	
	overwrite = str(kwargs['overwrite'])
	roi = str(kwargs['roi'])
	# Add a column with the name  of each image to unmix and add the corresponding raster value
	grouplist=gscript.read_command("i.group", group=groupname, flags="g" ).split()
	for rast in grouplist:
		band = rast.split("@")[0].split(".")[1]
		colname="b_"+str(band)
		gscript.run_command('v.db.addcolumn', map=vname, columns=colname + " DOUBLE")
		gscript.run_command('v.what.rast', map=vname, raster=rast, column=colname)  
	# Conect to the vector database	
	dbp = os.path.join(gisenv()['GISDBASE'], gisenv()['LOCATION_NAME'],gisenv()['MAPSET'], 'sqlite', 'sqlite.db')
	con = sqlite3.connect(dbp)
	# Query the db and store as pandas df
	vatt = pandas.read_sql("SELECT * FROM "+vname, con)
	uqclasses = set(vatt["class"])
	numclass=len(uqclasses)
	endarray = numpy.zeros(shape=(len(grouplist),numclass))
	# Calculate the avarage for each class and band
	for ref_class in uqclasses:
		endarray[:,ref_class-1]=vatt.loc[vatt[vclasscol] == ref_class].mean()[2:]
	# create the endmember raster 	
	rows = numpy.shape(endarray)[0]
	cols = numpy.shape(endarray)[1]
	# Write the endmember raster values
	for nrow in range(rows):
	    	er=endrastname+"."+str(nrow+1)
	    	gscript.mapcalc("{out} = null()".format(out=er), overwrite=True)
	    	for ncol in range(cols):
			val=endarray[nrow,ncol]
			gscript.mapcalc("{out} = if(col()=={ncol} && row()==1,{val},{out})".format(out=er,ncol=ncol+1,val=val), overwrite=True)
	mlist=gscript.list_grouped('raster', pattern=groupname+"_endmembers"+"*")[gisenv()['MAPSET']]
	# Resize the region to match the endmember raster	
	gscript.run_command("g.region", rast=groupname+"_endmembers."+str(1), zoom=groupname+"_endmembers."+str(1))
	# Export the endmembers raster and stack
	for map in mlist:
		gscript.run_command("r.out.gdal",input=map, output=wd+"/"+map+".tif", format="GTiff",overwrite=True)
	pat = mlist[0].split(".")[0]
	filelist=glob.glob(wd+"/"+pat+".?"+".tif")
	files=' '.join(filelist)
	expr="gdalbuildvrt -separate {dir}/{vrt} {files}".format(dir=wd,vrt="endmembers.vrt",files=files)
	os.system(expr)
	tiffout=wd+"/"+pat+".tif"
	expr="gdal_translate {dir}/{vrt} {out}".format(dir=wd,vrt="endmembers.vrt", out=tiffout)
	os.system(expr)
	gscript.run_command("g.region", region=roi)
	return

if __name__ == '__main__':
    main()


