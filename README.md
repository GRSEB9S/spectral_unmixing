		
## Summary
This project contains some utilities to help and automate the procces of obtaining linear spectral unmixing of images stored in GRASS-GIS,.
This utilities depends on the HyperspectralUnmixing program of the Orfeo Toolbox (https://www.orfeo-toolbox.org/CookBook/CookBooksu132.html#x165-10350004.10.4).

### Utilities

The project contains three utilities:
- clip_group_region: This utility clips, exports and stacks all the images of a GRASS image group (As otb_Hyperspectral_unmixing needs). The output raster name will be like: `originalname_subfix` and will be stored in the `wd` folder. Optionally it set the null values of the output images.

-end_rast_from_vect:  This utility creates the endmembers raster image (end_raster) to use for unmixing. The endmembers will be stored as a multiband image, so that each band (b) holds the mean reflectance value of the (e) endmembers, resulting in a b x 1 x e raster. It takes the location of the pure pixels for each class from the point vector (endmember_location) and the column `class_column`.

- unmix: This utility performes spectral unmixing of the images stored in the 'gname' group, using the endmembers created with `end_rast_from_vect`

The table below shows the arguments needed for each utility. 

| Utility                   | Argument                     |
|---------------------------|------------------------------|
| clip_group_region         | groupname,subfix,roi,nullval |
| end_rast_from_vect        | vname,groupname              |
| unmix                     | image,endmembers,out,utype   |



### Inputs

- GRASS imagery group (gname).

- Region of interest (roi).

- Vector containing the pure pixel (endmembers) location and "class id"

- Unmixing method name (default = "ucls")

### Outputs

A multi band raster layer of abundance of endmembers for each "class id"

 
### Install

This program uses GRASS and Orfeo Toolbox. To install in Ubuntu/Mint/Debian open a terminal:

`sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable`

`sudo apt-get update`

`sudo apt-get install grass otb otb-wrapping`

To install the pipeline:

`git clone https://github.com/leohardtke/spectral_unmixing.git`


- Install the application 

`cd spectral_unmixing`

`pip install .`

### Pipeline example:

The `test_db` folder includes a sample GRASS GIS databes to test the pipeline 

`clip_group_region LE72270902000209EDC00_toar madryn madryn --overwrite`

`end_rast_from_vect endmembers class LE72270902000209EDC00_toar end madryn overwrite=True`

`unmix outputs/LE72270902000209EDC00_toar.tif outputs/LE72270902000209EDC00_toar_endmembers.tif outputs/unmixed_image.tif`


