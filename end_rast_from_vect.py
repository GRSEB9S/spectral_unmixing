import click
import grass.script as gscript
from grass.script.core import gisenv
import os
import sqlite3
import pandas
import numpy,glob

@click.command(options_metavar='<Options>')
@click.argument('vname',metavar='endmember_location')
@click.argument('vclasscol',metavar='column_storing_classes')
@click.argument('gname',metavar='imagery_group')
@click.argument('endrastname',metavar='imagery_group')
@click.argument('roi',metavar='region')
@click.option('--overwrite/--no-overwrite', default=False, help="Use --overwrite if the output file exists and you what to overwrite it.")


def main(**kwargs):
	wd="outputs"    	
	""" This utility creates "b" grass rasters of 1 x c dimension  
	Example: end_rast_from_vect class endmembers LE72270902000209EDC00_toar endmembers madryn"""
	groupname = kwargs['gname']
	vname = kwargs['vname']
	endrastname = kwargs['endrastname']
	vclasscol = kwargs['vclasscol']	
	overwrite = kwargs['overwrite']
	# try to be independent of roi
	roi = kwargs['roi']
	grouplist=gscript.read_command("i.group", group=groupname, flags="g" ).split()
	for rast in grouplist:
		band = rast.split("@")[0].split(".")[1]
		colname="b_"+str(band)
		gscript.run_command('v.db.addcolumn', map=vname, columns=colname + " DOUBLE")
		gscript.run_command('v.what.rast', map=vname, raster=rast, column=colname)  
	dbp = os.path.join(gisenv()['GISDBASE'], gisenv()['LOCATION_NAME'],gisenv()['MAPSET'], 'sqlite', 'sqlite.db')
	con = sqlite3.connect(dbp)
	vatt = pandas.read_sql("SELECT * FROM "+vname, con)
	uqclasses = set(vatt["class"])
	numclass=len(uqclasses)
	endarray = numpy.zeros(shape=(len(grouplist),numclass))
	for ref_class in uqclasses:
		endarray[:,ref_class-1]=vatt.loc[vatt[vclasscol] == ref_class].mean()[2:]
	rows = numpy.shape(endarray)[0]
	cols = numpy.shape(endarray)[1]
	for nrow in range(rows):
	    	er=endrastname+"."+str(nrow+1)
	    	gscript.mapcalc("{out} = null()".format(out=er), overwrite=overwrite)
	    	for ncol in range(cols):
			val=endarray[nrow,ncol]
			print("{out} = if(col()=={ncol} && row()==1,{val},{out})".format(out=er,ncol=ncol+1,val=val))
			gscript.mapcalc("{out} = if(col()=={ncol} && row()==1,{val},{out})".format(out=er,ncol=ncol+1,val=val), overwrite=True)
	mlist=gscript.list_grouped('raster', pattern=groupname+"_endmembers"+"*")[gisenv()['MAPSET']]
	gscript.run_command("g.region", rast=groupname+"_endmembers."+str(1), zoom=groupname+"_endmembers."+str(1))
	for map in mlist:
		gscript.run_command("r.out.gdal",input=map, output=wd+"/"+map+".tif", format="GTiff",overwrite=True)
	pat = mlist[0].split(".")[0]
	filelist=glob.glob(wd+"/"+pat+".?"+".tif")
	files=' '.join(filelist)
	expr="/usr/bin/gdalbuildvrt -separate {dir}/{vrt} {files}".format(dir=wd,vrt="endmembers.vrt",files=files)
	os.system(expr)
	tiffout=wd+"/"+pat+".tif"
	expr="/usr/bin/gdal_translate {dir}/{vrt} {out}".format(dir=wd,vrt="endmembers.vrt", out=tiffout)
	os.system(expr)
	gscript.run_command("g.region", region=roi)

if __name__ == '__main__':
    main()


