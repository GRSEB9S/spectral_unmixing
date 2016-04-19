import click
import glob, os, argparse
from osgeo import gdal
from osgeo.gdalconst import *
from numpy import *
from scipy import *

@click.command()
@click.argument('infolder',type=click.Path(exists=True))
@click.argument('outfile')

def cli(infolder,outfile):
	"""This program extracts the Fourier parameters of a remote sensing time series.

	The input folder should contain a time series of images in the same projection and
	with constant number of rows and columns in any GDAL supported format.

	The output file is a multi band Geotiff image containing the amplitude and phase of 
	the different harmonics. 
	
	You can test the program downloading the sample images from:\n
	https://github.com/leohardtke/some_code/tree/master/FourierExtraction/test_images

	"""
	DirName = infolder
	Ext = "tif"
	file_list=glob.glob(DirName+"/*."+Ext)
	file_list.sort()
	#Use the first image on the folder as source foor the geographic information
	src_file = file_list[0]
	dst_file = outfile
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

