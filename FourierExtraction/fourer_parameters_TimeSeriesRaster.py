#! /usr/bin/python

import sys, math, os, glob, matplotlib
from pylab import *
from osgeo import gdal
from osgeo.gdalconst import *
from numpy import * 
from scipy import *

#Genera una lista ordenada de archivos a procesar
DirName="/comp/Datosbase/Mod13a3_1k"	
os.chdir(DirName)
Ext="tif"
lista=glob.glob("*."+Ext)
lista.sort()

#src_file = sys.argv[1]
src_file = lista[0]
#dst_file = sys.argv[2]
dst_file = "/home/leomint/Escritorio/salida.tif"
out_bands = 1

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
fourarray = zeros(rows*cols*2).reshape(rows,cols*2)
fourarray.dtype=complex128
band1=zeros(rows*cols).reshape(rows,cols)
 
# set the projection and georeferencing info
dst_ds.SetProjection( src_ds.GetProjection() )
dst_ds.SetGeoTransform( src_ds.GetGeoTransform() )

# read the data in
data=zeros(NImg*rows*cols).reshape(NImg,rows,cols)
#Carga en "data" cada una de las imágenes
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

#seria para el caso del primer harmonico
for r in range(rows):
  for c in range(cols):
      #secuencia
      if data[0,r,c] > 0:
         temparray = fft(data[...,r,c])
         fourarray[r,c] = temparray[0]


# write each band out
band1=fourarray[:].real/NImg
dst_ds.GetRasterBand(1).WriteArray(band1)
dst_ds = None

import pylab
pylab.imshow(band1)
pylab.show()

