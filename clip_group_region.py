import click
import grass.script as gscript
from grass.script.core import gisenv

@click.command(options_metavar='<Argumenst>')
@click.argument('groupname',metavar='Imagery_group')
@click.argument('subfix',metavar='Output_subfix')
@click.argument('roi',metavar='Region_of interest')


def main(**kwargs):
    	""" This utility clips images of a gruop and create a gorup of the output files.
    	The output raster name will be like: originalname_subfix	  
    	Optionaly it set the null values of the output group
    
	Example: clip_group_region LE72270902002150EDC00_toar cliped madryn 0"""
    	roi = kwargs['roi']
	groupname = kwargs['groupname']
	subfix = kwargs['subfix']
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


if __name__ == '__main__':
    main()
