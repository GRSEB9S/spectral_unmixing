#Usage: python fourer_parameters_TimeSeriesRaster.py input_folder extension output_file

import glob, os, argparse
try:
    from schema import Schema, And, Or, Use, SchemaError
except ImportError:
    exit('This example requires that `schema` data-validation library installed\n'
         'https://github.com/halst/schema')
try:
    from osgeo import gdal
except ImportError:
    exit('This program needs GDAL: Geospatial Data Abstraction Library\n'
	'https://pypi.python.org/pypi/GDAL/')

try:
    from osgeo.gdalconst import *
except ImportError:
    exit('This program needs GDAL: Geospatial Data Abstraction Library\n'
	'https://pypi.python.org/pypi/GDAL/')

try:
    from numpy import *
except ImportError:
    exit('This program needs numpy\n'
	'https://pypi.python.org/pypi/numpy/')

try:
    from scipy import *
except ImportError:
    exit('This program needs scipy\n'
	'https://pypi.python.org/pypi/scipy/')


def main(args):
	DirName = args.infolder
	Ext = args.extension
	file_list=glob.glob(DirName+"/*."+Ext)
	file_list.sort()
	#Use the first image on the folder as source foor the geographic information
	src_file = file_list[0]
	dst_file = args.outfile
	#Processing block size (could be argument)
	xBlockSize = yBlockSize =256
	# Open source file
	src_ds = gdal.Open( src_file )
	src_band = src_ds.GetRasterBand(1)
	rows = src_ds.RasterYSize
	cols = src_ds.RasterXSize
	NImg=len(file_list)
	# create destination file
	## driver.Create( outfile, outwidth, outheight, numbands, gdaldatatype)
	dst_driver = gdal.GetDriverByName('GTiff')
	dst_ds = dst_driver.Create(dst_file, src_ds.RasterXSize, src_ds.RasterYSize, NImg, gdal.GDT_Float32) 
	# create output bands
	fourarray = zeros(NImg*rows*cols*2).reshape(NImg,rows,cols*2)
	fourarray.dtype=complex128
	# set the projection and georeferencing info
	dst_ds.SetProjection( src_ds.GetProjection() )
	dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )
	# Main procces to get the fourier parameters 
	# Loops trough rows
	for i in range(0, rows, yBlockSize):
	  if i + yBlockSize < rows:
	    numRows = yBlockSize
	  else:
	    numRows = rows - i
	  # loop through the columns
	  for j in range(0, cols, xBlockSize):
	    if j + xBlockSize < cols:
	      numCols = xBlockSize
	    else:
	      numCols = cols - j
	    # read the data in
	    data=zeros(NImg*numRows*numCols).reshape(NImg,numRows,numCols)
	    k=0
	    for PrFile in file_list[0:NImg]:
	      DataSet = gdal.Open(PrFile, GA_ReadOnly)
	      data[k,...]=DataSet.GetRasterBand(1).ReadAsArray(j, i, numCols, numRows).copy()
	      DataSet=None
	      k=k+1
	    fourarray = zeros(NImg*numRows*numCols*2).reshape(NImg,numRows,numCols*2)
	    fourarray.dtype=complex128
	    for r in range(numRows):
	      for c in range(numCols):
		  #secuencia
		  if data[0,r,c] > 0:
		     temparray = fft(data[...,r,c])
		     fourarray[...,r,c] = temparray[0:NImg]
	    dst_ds.GetRasterBand(1).WriteArray(fourarray[0,:].real/NImg,j,i)
	    outband=2
	    for fidx in range(1,(NImg+1)/2):
	    	dst_ds.GetRasterBand(outband).WriteArray(fourarray[fidx,:].real/NImg,j,i)
		outband=outband+1	    	
		dst_ds.GetRasterBand(outband).WriteArray(fourarray[fidx,:].imag/NImg,j,i)
		outband=outband+1

	dst_ds = None

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("infolder",help="Input folder containing the time series",type=str)
	parser.add_argument("extension",help="Extention of the images input folder",type=str)
	parser.add_argument("outfile",help="Output file name",type=str)
	args = parser.parse_args()
	# Check for images in folder (same rows*cols)
	# Check outdir
	main(args)

