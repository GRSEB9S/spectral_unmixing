export PYTHONPATH="${PYTHONPATH}:/usr/lib/otb/python"
export OTB_APPLICATION_PATH=/usr/lib/otb/applications

import sys 
import otbApplication
import grass.script as gscript
from grass.script.core import gisenv
import os
import glob
import sqlite3
from subprocess import call
import pandas
import numpy

def clip_group_region(groupname,subfix,roi,nullval):
    # This functions clips images of a gruop as groupname+subfix, 
    # Set the null value of the clipped raster (usefull for landsat null=0)
    # And creates a gruop of the recently created files
    gscript.run_command('g.region', region=roi)
    grouplist=gscript.read_command("i.group", group=groupname, flags="g" ).split()
    for raster in grouplist:
        name=raster.split("@")[0]
        band= name.split(".")[1]
        rout= name.split(".")[0]+"_"+subfix
        expression="{rout}.{b} = {rin}".format(rin=name,rout=rout,b=band)
        gscript.mapcalc(expression)                                                          
        gscript.run_command('r.null', map="{rout}.{b}".format(rout=rout,b=band),setnull=nullval)
    mlist=gscript.list_grouped('raster', pattern=groupname+"_"+subfix+"*")[gisenv()['MAPSET']]
    gscript.run_command("i.group", group=groupname+"_"+subfix, input=mlist)
    return
# EXAMPLE: clip_group_region("LE72270902002150EDC00_toar","cliped",roi,0)
    
    
def endmembers_from_vector(vname,groupname):
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
    return(endarray)

def endarray_to_raster(endarray,endrastname):
    rows = numpy.shape(endarray)[0]
    cols = numpy.shape(endarray)[1]
    for nrow in range(rows):
        er=endrastname+"."+str(nrow+1)
        gscript.mapcalc("{out} = null()".format(out=er), overwrite=True)
        for ncol in range(cols):
            val=endarray[nrow,ncol]
            print("{out} = if(col()=={ncol} && row()==1,{val},{out})".format(out=er,ncol=ncol+1,val=val))
            gscript.mapcalc("{out} = if(col()=={ncol} && row()==1,{val},{out})".format(out=er,ncol=ncol+1,val=val), overwrite=True)
    return

# export endmembers groupas otb needs!
def export_end(gn):
    mlist=gscript.list_grouped('raster', pattern=gn+"_endmembers"+"*")[gisenv()['MAPSET']]
    gscript.run_command("g.region", rast=gn+"_endmembers."+str(1), zoom=gn+"_endmembers."+str(1))
    for map in mlist:
        gscript.run_command("r.out.gdal",input=map, output=wd+"/"+map+".tif", format="GTiff")
    pat = mlist[0].split(".")[0]
    filelist=glob.glob(wd+"/"+pat+".?"+".tif")
    files=' '.join(filelist)
    expr="/usr/bin/gdalbuildvrt -separate {dir}/{vrt} {files}".format(dir=wd,vrt="temp.vrt",files=files)
    os.system(expr)
    tiffout=wd+"/"+pat+".tif"
    expr="/usr/bin/gdal_translate {dir}/{vrt} {out}".format(dir=wd,vrt="temp.vrt", out=tiffout)
    os.system(expr)
    gscript.run_command("g.region", region=roi)
    return

def unmix(image,endmembers,out,utype):
    # The following line creates an instance of the HyperspectralUnmixing application
    HyperspectralUnmixing=otbApplication.Registry.CreateApplication("HyperspectralUnmixing")
    # The following lines set all the application parameters:
    HyperspectralUnmixing.SetParameterString("in",image)
    HyperspectralUnmixing.SetParameterString("ie",endmembers)
    HyperspectralUnmixing.SetParameterString("out",out)
    HyperspectralUnmixing.SetParameterString("ua",utype)
    # The following line execute the application
    HyperspectralUnmixing.ExecuteAndWriteOutput()
    return

#######################################################################
#######    Workflow to get the fractional cover maps...  ##############
#######################################################################
wd = "/data/Work/GrassDb/grass_ipy/unmix"
os.chdir(wd)
# Remember to create the group with the desired images (LS7 bands 1 2 3 4 5 7)
# Same basename as the raster included. Format=basename.band
# Use Option A if clipping is needed. Use option B otherwise
gn = "LE72270902000209EDC00_toar"
subfix = "cliped"
nullval = 0
roi = "madpen"
# Endmembers vector
vname = "endmembers"
# Numerical column name holding the classes
vclasscol = "class" 

############################################################################
# Step 1 Option A
#Start here if clip the group to a roi is necesary

clip_group_region(gn,subfix,roi,nullval)

# Export the cliped images
gn_s=groupname+"_"+subfix
gscript.run_command("r.out.gdal",input=gn_s, output=wd+"/"+gn_s+".tif", format="GTiff" )

## Get the endmembers from the attribute table
endarray=endmembers_from_vector(vname,gn)

## Write the endmembers as grass raster 
endrastname = "{gn_s}_endmembers".format(gn_s=gn_s)
endarray_to_raster(endarray,endrastname)
## Export the endmembers
export_end(gn_s)

# Unmix
raster="{wd}/{gn_s}.tif".format(wd=wd,gn_s=gn_s)
endmembers="{wd}/{gn_s}_endmembers.tif".format(wd=wd,gn_s=gn_s)
out="{wd}/{gn_s}_unmixed.tif".format(wd=wd,gn_s=gn_s)
    
unmix(raster,endmembers,out,"ucls")


##############################################################################

# Step 1 Option B
#Start here if clip the group to a roi is NOT necesary and skip if used option 1
#if clipped not needed
gn="LE72270902002150EDC00_toar_cliped"
list=gscript.read_command("i.group", group=gn, flags="g" ).split()
gscript.run_command("r.out.gdal",input=gn, output=wd+"/"+gn+".tif", format="GTiff" )

## Get the endmembers from the attribute table
endarray=endmembers_from_vector(vname,grasterin)
## Write the endmembers as grass raster 
endrastname = gn+"_endmembers"
endarray_to_raster(endarray,endrastname)
## Export the endmembers
export_end(gn)

# Unmix
raster=wd+"/"+gn+".tif"
endmembers=wd+"/"+gn+"_endmembers"+".tif"
out=wd+"/"+gn+"_unmixed"+".tif"

    
unmix(raster,endmembers,out,"ucls")
