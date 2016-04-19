"""Usage: python fourer_parameters_TimeSeriesRaster.py INFOLDER OUTFILE...
Arguments:
  OUTFILE:  Output file containing the fourier Parameters.
  INFOLDER: Input folder containing the remote sensing time series.
"""

import glob, os
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
try:
    from docopt import docopt
except ImportError:
    exit('This program needs doctop\n'
	'https://pypi.python.org/pypi/doctop/')


def main(args):
	#Genera una lista ordenada de archivos a procesar
	DirName="/home/leo/Desktop/tmp/test_images"
	#/comp/Datosbase/Mod13a3_1k"	
	os.chdir(DirName)
	Ext="tif"
	lista=glob.glob("*."+Ext)
	lista.sort()

	#src_file = sys.argv[1]
	src_file = lista[0]
	#dst_file = sys.argv[2]
	dst_file = "/home/leo/Desktop/tmp/fourier.tif"
	out_bands = 9

	# Open source file
	src_ds = gdal.Open( src_file )
	src_band = src_ds.GetRasterBand(1)
	rows = src_ds.RasterYSize
	cols = src_ds.RasterXSize
	NImg=len(lista)

	# create destination file
	## driver.Create( outfile, outwidth, outheight, numbands, gdaldatatype)
	dst_driver = gdal.GetDriverByName('GTiff')
	dst_ds = dst_driver.Create(dst_file, src_ds.RasterXSize, src_ds.RasterYSize, out_bands, gdal.GDT_Float32) 

	 
	# create output bands
	fourarray = zeros(9*rows*cols*2).reshape(9,rows,cols*2)
	fourarray.dtype=complex128
	band1=zeros(rows*cols).reshape(rows,cols)
	band2=zeros(rows*cols).reshape(rows,cols)
	band3=zeros(rows*cols).reshape(rows,cols)
	band4=zeros(rows*cols).reshape(rows,cols)
	band5=zeros(rows*cols).reshape(rows,cols)
	band6=zeros(rows*cols).reshape(rows,cols)
	band7=zeros(rows*cols).reshape(rows,cols)
	band8=zeros(rows*cols).reshape(rows,cols)
	band9=zeros(rows*cols).reshape(rows,cols)

	 
	# set the projection and georeferencing info
	dst_ds.SetProjection( src_ds.GetProjection() )
	dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )

	# read the data in
	data=zeros(NImg*rows*cols).reshape(NImg,rows,cols)
	#Carga en "data" cada una de las imagenes
	j=0
	for PrFile in lista[0:NImg]:
	  DataSet = gdal.Open(PrFile, GA_ReadOnly)
	  if DataSet is None:
	    print 'No se pudo abrir: ' + PrFile
	    sys.exit(1)
	  rows = DataSet.RasterYSize
	  cols = DataSet.RasterXSize
	  TempB = DataSet.GetRasterBand(1)
	  TempA = TempB.ReadAsArray(0, 0, cols, rows)
	  data[j,...]=TempA.copy()
	  DataSet=None
	  TempB=None
	  TempA=None
	  j=j+1

	for r in range(rows):
	  for c in range(cols):
	      #secuencia
	      if data[0,r,c] > 0:
		 temparray = fft(data[...,r,c])
		 fourarray[...,r,c] = temparray[0:out_bands]


	# write each band out
	band1=fourarray[0,:].real/NImg 
	band2=fourarray[1,:].real/NImg 
	band3=fourarray[1,:].imag/NImg 
	band4=fourarray[2,:].real/NImg 
	band5=fourarray[2,:].imag/NImg 
	band6=fourarray[3,:].real/NImg 
	band7=fourarray[3,:].imag/NImg 
	band8=fourarray[4,:].real/NImg 
	band9=fourarray[4,:].imag/NImg 

	dst_ds.GetRasterBand(1).WriteArray(band1)
	dst_ds.GetRasterBand(2).WriteArray(band2)
	dst_ds.GetRasterBand(3).WriteArray(band3)
	dst_ds.GetRasterBand(4).WriteArray(band4)
	dst_ds.GetRasterBand(5).WriteArray(band5)
	dst_ds.GetRasterBand(6).WriteArray(band6)
	dst_ds.GetRasterBand(7).WriteArray(band7)
	dst_ds.GetRasterBand(8).WriteArray(band8)
	dst_ds.GetRasterBand(9).WriteArray(band9)

	dst_ds = None

if __name__ == '__main__':
	args = docopt(__doc__)
	main(args)

