#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import shutil
import sys

GDAL_PREFIX = "/usr/local/gdal/gdal-dev/bin/"

# Zu bearbeitender Kanton
# 5 = SZ
# 11 = SO
# 8 = GL
KT_NR = 8

# Verzeichnis der DTM-GeoTIFF
DTM_DIR = "/home/stefan/tmp/glarus/"

os.system( GDAL_PREFIX+"gdalbuildvrt " + DTM_DIR + "dtm.vrt " + DTM_DIR + "*.tif" );

shp1 = ogr.Open("../00_data/kantonsgrenzen/kantonsgrenzen.shp")
# Neu gemacht für Glarus, da nicht mehr 1/16 Kacheln sondern nur 1/4 Kachel.
shp2 = ogr.Open("../00_data/dtm_dom_idx/gl/dtm_dom_idx.shp")

layer1 = shp1.GetLayer(0)
layer2 = shp2.GetLayer(0)

layer1.SetAttributeFilter("kantonsnum = " + str(KT_NR))
for feature1 in layer1:
  geom1 = feature1.GetGeometryRef()

for feature2 in layer2:
  geom2 = feature2.GetGeometryRef()
  # 'location' statt 'nummer'
  nummer = feature2.GetField('location')
  print "nummer: " + nummer

  if geom2.Intersects(geom1): 
    # Schön, das sieht jetzt einfacher aus, das in 'location' wirklich Filename steht.
    # Ah so schön auch wieder nicht... Anders!
    dtm_base_name = nummer.replace(".tif","")
    dtm_tif_name = dtm_base_name + ".tif";
    
    if os.path.isfile(DTM_DIR + dtm_tif_name):
      print "filename: " + dtm_tif_name
      
      extent = geom2.GetEnvelope()
      minX, maxX, minY, maxY = extent

      cmd = GDAL_PREFIX+"gdal_translate -projwin " + str(minX-50) + " " + str(maxY+50) + " " + str(maxX+50) + " " + str(minY-50) + " " + DTM_DIR + "dtm.vrt " + DTM_DIR + "input.tif";
      os.system(cmd);

      input = DTM_DIR + "input.tif"
      output = DTM_DIR + "output.tif"
      
    
      for i in range(15):
        cmd = GDAL_PREFIX+"gdalwarp -co COMPRESS=PACKBITS -r cubicspline " + input + " " + output
        os.system(cmd)
        os.system("cp " + output + " " + input )
        os.system("rm " + output)

      # 5 Meter für Glarus
      cmd = GDAL_PREFIX+"gdal_contour -a elev -i 5.0 " + input + " " + DTM_DIR + "contour_tmp.shp"
      os.system(cmd)
      os.system("rm " + input)
            
      # Zurechtscheiden der Höhenlinien auf Ursprungskachel und Kanton
      clip_wkt = geom2.ExportToWkt()
      cmd = GDAL_PREFIX+"ogr2ogr -clipsrc '" + clip_wkt + "' " + DTM_DIR + "contour_tmp_clip_tileextent.shp " + DTM_DIR + "contour_tmp.shp"
      os.system(cmd)
      
      cmd = GDAL_PREFIX+"ogr2ogr -dialect SQLITE " + DTM_DIR + "kantonsgrenze_" + str(KT_NR) + ".shp ../00_data/kantonsgrenzen/kantonsgrenzen.shp -sql \"SELECT * FROM kantonsgrenzen WHERE kantonsnum = " + str(KT_NR) + "\""  
      os.system(cmd)
      
      cmd = GDAL_PREFIX+"ogr2ogr -clipsrc " + DTM_DIR + "kantonsgrenze_" + str(KT_NR) + ".shp " + DTM_DIR + "contour_tmp_clip_canton.shp " + DTM_DIR + "contour_tmp_clip_tileextent.shp"
      os.system(cmd)

      # Höhenkurven kleiner 100m (sinnvolle Grösse?) entfernen
      cmd = GDAL_PREFIX+"ogr2ogr -append -dialect SQLITE " + DTM_DIR + "contour.shp " + DTM_DIR + "contour_tmp_clip_canton.shp -sql \"SELECT * FROM  contour_tmp_clip_canton WHERE ST_Length(GEOMETRY) > 100\""
      os.system(cmd)

      # tmp Objekte löschen
      os.system("rm " + DTM_DIR + "contour_tmp*.*")
      os.system("rm " + DTM_DIR + "kantonsgrenze*.*")

