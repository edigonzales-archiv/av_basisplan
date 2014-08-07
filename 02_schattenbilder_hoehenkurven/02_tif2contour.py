#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import shutil

# Zu bearbeitender Kanton
# 5 = SZ
# 11 = SO
# 8 = GL
KT_NR = 8

# Verzeichnis der DTM-GeoTIFF
DTM_DIR = "/home/stefan/tmp/bpav_sz/dtm_roh/"

os.system( "gdalbuildvrt " + DTM_DIR + "dtm.vrt " + DTM_DIR + "*.tif" );

shp1 = ogr.Open("../00_data/kantonsgrenzen/kantonsgrenzen.shp")
shp2 = ogr.Open("../00_data/dtm_dom_idx/dtm_dom_idx.shp")

layer1 = shp1.GetLayer(0)
layer2 = shp2.GetLayer(0)

layer1.SetAttributeFilter("kantonsnum = " + str(KT_NR))
for feature1 in layer1:
  geom1 = feature1.GetGeometryRef()

for feature2 in layer2:
  geom2 = feature2.GetGeometryRef()
  nummer = feature2.GetField('nummer')

  if geom2.Intersects(geom1): 
    dtm_base_name = nummer.replace("-", "") +"_dtm_03_02";
    dtm_tif_name = nummer.replace("-", "") +"_dtm_03_02.tif";

    if os.path.isfile(DTM_DIR + dtm_tif_name):
      print dtm_tif_name

      extent = geom2.GetEnvelope()
      minX, maxX, minY, maxY = extent

      cmd = "gdal_translate -projwin " + str(minX-50) + " " + str(maxY+50) + " " + str(maxX+50) + " " + str(minY-50) + " " + DTM_DIR + "dtm.vrt " + DTM_DIR + "input.tif";
      os.system(cmd);

      input = DTM_DIR + "input.tif"
      output = DTM_DIR + "output.tif"
    
      for i in range(10):
        cmd = "gdalwarp -co COMPRESS=PACKBITS -r cubicspline " + input + " " + output
        os.system(cmd)
        os.system("cp " + output + " " + input )
        os.system("rm " + output)

      cmd = "gdal_contour -a elev -i 10.0 " + input + " " + DTM_DIR + "contour_tmp.shp"
      os.system(cmd)
      os.system("rm " + input)
      
      # Zurechtscheiden der Höhenlinien auf Ursprungskachel und Kanton
      clip_wkt = geom2.ExportToWkt()
      cmd = "ogr2ogr -clipsrc '" + clip_wkt + "' " + DTM_DIR + "contour_tmp_clip_tileextent.shp " + DTM_DIR + "contour_tmp.shp"
      os.system(cmd)
      
      cmd = "ogr2ogr -dialect SQLITE " + DTM_DIR + "kantonsgrenze_" + str(KT_NR) + ".shp ../00_data/kantonsgrenzen/kantonsgrenzen.shp -sql \"SELECT * FROM kantonsgrenzen WHERE kantonsnum = " + str(KT_NR) + "\""  
      os.system(cmd)
      
      cmd = "ogr2ogr -clipsrc " + DTM_DIR + "kantonsgrenze_" + str(KT_NR) + ".shp " + DTM_DIR + "contour_tmp_clip_canton.shp " + DTM_DIR + "contour_tmp_clip_tileextent.shp"
      os.system(cmd)

      # Höhenkurven kleiner 100m (sinnvolle Grösse?) entfernen
      cmd = "ogr2ogr -append -dialect SQLITE " + DTM_DIR + "contour.shp " + DTM_DIR + "contour_tmp_clip_canton.shp -sql \"SELECT * FROM  contour_tmp_clip_canton WHERE ST_Length(GEOMETRY) > 100\""
      os.system(cmd)

      # tmp Objekte löschen
      os.system("rm " + DTM_DIR + "contour_tmp*.*")
      os.system("rm " + DTM_DIR + "kantonsgrenze*.*")


