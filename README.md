		
## Summary
This project contains utilities (a pipeline) to automate the linear spectral unmixing process in GRASS-GIS

### Utilities

Add description here. See table below

| Utility                   | Argument                     |
|---------------------------|------------------------------|
| clip_group_region         | groupname,subfix,roi,nullval |
| endmembers_from_vector    | vname,groupname              |
| endarray_to_raster        | endarray,endrastname         |
| export_end                | gn                           |
| unmix                     | image,endmembers,out,utype   |


### Inputs

GRASS imagery group.
Region of interest (default = actual region).
Vector containing the pure pixel (endmembers) location and "class id"
Unmixing method name (default = "ucls")

### Outputs

A raster layer of abundance of endmembers for each "class id"

## Testing
### Install


### Pipeline example:

clip_group_region gn subfix roi nullval
 
endarray endmembers_from_vector vname,gn 

endarray_to_raster endarray endrastname 

unmix raster endmembers out "ucls" 

