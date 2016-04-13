### Landsat from .tar.gz to TOAR reflectance

wd = "/data/work/DatosBase/Landsat_originales/"

# Uncompress files
mkdir tif
for file in $(ls *.tar.gz); do
  echo tar -zxvf $file -C ./tif
done

# Warp to utm20
cd tif
mkdir UTM20
for file in `ls *.TIF`; do
  gdalwarp -t_srs EPSG:32720 $file UTM20/$file -r bilinear
done

#importo a grass
for file in `ls UTM20/*.TIF`; do
   name=`basename $file .TIF`
   r.in.gdal input=$file output=$name
done

## Create imagery groups
for rgroup in $(g.list rast pattern=LE* | uniq -w 15); do
 sen=${rgroup:0:3}
 pr=${rgroup:3:6}
 yr=${rgroup:9:4}
 day=${rgroup:13:3}
 group=${sen}_${pr}_${yr}_${day}
 i.group group=$group subgroup=completo input=`g.list rast pattern=${rgroup:0:15}* sep=,`
done


### Registrar as timeseries de grass
t.create type=strds temporaltype=absolute output=$tds title="" description=""

# Loop for each date
for rgroup in $(g.mlist rast pattern=LE* mapset=posdoc | uniq -w 15 | awk -F'_' '{print $1}'); do
# Loop for each band
  for band in $(g.mlist rast pattern=$rgroup* mapset=posdoc); do
   yr=${band:9:4}
   jd=${band:13:3}
   fecha_st=$(dateutils.dconv -i '%Y%D' ${yr}${jd})
   fecha_end=$(dateutils.dconv -i '%Y%D' $((${yr}${jd}+7)))
   t.register -i type=rast input=${tds} maps=$band start=$fecha_st end=$fecha_end
done
done

g.list rast pattern=LE72270902002*_B*  | uniq -w 20   | uniq -w 20 > landsat_base
while read line; do 
name=${line:0:21}; 
 i.landsat.toar input_prefix=${name}_B. output_prefix=${name}_toar. metfile=/data/Work/DatosBase/Landsat/tif/${name}_MTL.txt
done < landsat_base
