#!/usr/bin/python
# -*- coding: utf-8 -*-

from osgeo import ogr, osr
import os
import shutil

# Zu bearbeitender Kanton
# 5 = SZ
# 11 = SO
KT_NR = 5

# Arbeitsverzeichnisse erstellen (falls nicht vorhanden)
DTM_DIR = "/home/stefan/tmp/bpav_sz/dtm_roh/"
SMOOTH_DIR = DTM_DIR + "dtm_smooth/"
HILLSHADE_DIR = DTM_DIR + "hillshading/"
HILLSHADE_BP_DIR = DTM_DIR + "hillshading_bp/"

if not os.path.exists(SMOOTH_DIR):
  os.makedirs(SMOOTH_DIR)
else:
  shutil.rmtree(SMOOTH_DIR)
  os.makedirs(SMOOTH_DIR)  

if not os.path.exists(HILLSHADE_DIR):
  shutil.rmtree(HILLSHADE_DIR)  
  os.makedirs(HILLSHADE_DIR)

if not os.path.exists(HILLSHADE_BP_DIR):
  shutil.rmtree(HILLSHADE_BP_DIR)  
  os.makedirs(HILLSHADE_BP_DIR)

shp1 = ogr.Open("../00_data/kantonsgrenzen/kantonsgrenzen.shp")
shp2 = ogr.Open("../00_data/dtm_dom_idx/dtm_dom_idx.shp")

layer1 = shp1.GetLayer(0)
layer2 = shp2.GetLayer(0)

layer1.SetAttributeFilter("kantonsnum = " + str(KT_NR))
for feature1 in layer1:
  geom1 = feature1.GetGeometryRef()


# DTM und Hillshading
for feature2 in layer2:
  geom2 = feature2.GetGeometryRef()
  nummer = feature2.GetField('nummer')
  
  if geom2.Intersects(geom1): 
    dtm_xyz_gz_name = nummer.replace("-", "") +"_dtm_03_02.xyz.gz";
    dtm_xyz_name = nummer.replace("-", "") +"_dtm_03_02.xyz";
    dtm_base_name = nummer.replace("-", "") +"_dtm_03_02";
    dtm_tif_name = nummer.replace("-", "") +"_dtm_03_02.tif";

    
    if os.path.isfile(DTM_DIR + dtm_xyz_gz_name):
      print dtm_xyz_gz_name
      
#      os.system("gunzip -c " + DTM_DIR + dtm_xyz_gz_name + " > " + DTM_DIR + dtm_xyz_name)
#      os.system("fromdos " + DTM_DIR + dtm_xyz_name)

      cmd = "sed -e 's/\s/,/g' " + DTM_DIR + dtm_xyz_name + " > " + DTM_DIR + "dtm_xyz.csv"
#      os.system(cmd)

      cmd = "sed -i '1s/^/x,y,z\\n/' " + DTM_DIR + "dtm_xyz.csv";
#      os.system(cmd)

      cmd = "sed -e 's|dtm_xyz.csv|"+DTM_DIR+"dtm_xyz.csv|g' dtm_xyz.vrt > " + DTM_DIR + "dtm_xyz.vrt"
      os.system(cmd)

      # Liefert IMMER minX, minY, maxX, maxY zurück?!
      extent = geom2.GetEnvelope()
      minX, maxX, minY, maxY = extent
      
      print minX
      print minY
      print maxX
      print maxY
      
      # +1 Meter: 1/16-Kacheln sind in x-Richtung nicht durch 2 teilbar.
      dx = maxX - minX + 1;
      dy = maxY - minY;
    
      px = dx / 2;
      py = dy / 2;
      
      # Mit gdal_grid aus den Punktdaten ein GeoTiff erstellen.
      # Input ist hier das DTM 2m-Grid. Möglich wären auch die Rohdaten.
      # Dann dürfte es aber langsamer werden ('nearest' ginge dann nicht mehr) -> Ist furchtbar/unbrauchbar langsam. Sogar mit 8 Prozessoren.
      # Ok, so sollte es auch mit Rohdaten schnell gehen (siehe unten gdal_fillnodata.py)
      cmd = "gdal_grid -a_srs epsg:21781 -a nearest:min_points=9:radius1=5.0:radius2=5.0:nodata=-9999 -txe " + str(minX) + " " + str(maxX+1) + " -tye " +str(minY) + " " + str(maxY) + " -outsize " + str(px) + " " + str(py) + " -of GTiff -ot Float32 -l dtm_xyz " + DTM_DIR + "dtm_xyz.vrt " + DTM_DIR + dtm_base_name + "_tmp_wrong_nodata.tif"
#      os.system(cmd)
      
      # gdal_grid setzt nodata nicht richtig.
      cmd = "gdal_translate -a_nodata -9999 " + DTM_DIR + dtm_base_name + "_tmp_wrong_nodata.tif " + DTM_DIR + dtm_base_name + "_tmp_correct_nodata.tif "
#      os.system(cmd)
      
      # Die Pixel ohne Wert wieder mit einem Wert füllen.
      # Maximal 500 Meter wird gesucht. Sollte reichen.
      # Algorithmus unbekannt.
      cmd = "gdal_fillnodata.py -md 500 " + DTM_DIR + dtm_base_name + "_tmp_correct_nodata.tif " + DTM_DIR + dtm_base_name + "_tmp.tif"
#      os.system(cmd)

      # Aus irgendeinem Grund sind die Pixel nicht 2m gross...??
      # Mmh, manchmal schon. Überprüfen ob dieser Schritt noch notwendig ist.
      cmd = "gdalwarp -overwrite -co COMPRESS=PACKBITS -co TILED=YES -t_srs epsg:21781 -te " + str(minX) + " " + str(minY) + " " + str(maxX+1) + " " + str(maxY) + " -tr 2 2 -r near " + DTM_DIR + dtm_base_name + "_tmp.tif " + DTM_DIR + dtm_tif_name;
#      os.system(cmd)

      # In einer Forschleife das DTM smoothen, damit die Höhenkurven geschmeidiger aussehen.
      # Smoothen hier wahrscheinlich nicht mehr notwendig, ich smoothe ja den ausgeschnittenen Teil unten nochmals für die Höhenkurven.
      os.system( "cp " + DTM_DIR + dtm_tif_name + " " + DTM_DIR + "input.tif" )
      input = DTM_DIR + "input.tif"
      output = DTM_DIR + "output.tif"
    
      for i in range(10):
        cmd = "gdalwarp -co COMPRESS=PACKBITS -r cubicspline " + input + " " + output
#        os.system(cmd)
        
#        os.system("cp " + output + " " + input )
#        os.system("rm " + output)

#      os.system("cp " + input + " " + SMOOTH_DIR + dtm_tif_name)
#      os.system("rm " + input)

      #Hillshading (mit gewarpten DTM)
      cmd = "gdaldem hillshade -co COMPRESS=LZW -compute_edges -az 270 -alt 40 " + DTM_DIR + dtm_tif_name + " " + HILLSHADE_DIR + dtm_tif_name
#      os.system(cmd)
    
      cmd = "gdaladdo -r average " + HILLSHADE_DIR + dtm_tif_name + " 2 4 8 16 32 64";
#      os.system(cmd)
    
      cmd = "gdaldem color-relief -co COMPRESS=LZW " + HILLSHADE_DIR + dtm_tif_name +  " ramp.txt " + HILLSHADE_BP_DIR  + dtm_tif_name
#      os.system(cmd)

      cmd = "gdaladdo -r average " + HILLSHADE_BP_DIR + dtm_tif_name + " 2 4 8 16 32 64";
#      os.system(cmd)

      os.system("rm " + DTM_DIR + dtm_base_name + "_tmp.tif")
      os.system("rm " + DTM_DIR + dtm_base_name + ".tif.aux.xml")
      os.system("rm " + DTM_DIR + dtm_base_name + "_tmp_wrong_nodata.tif")
      os.system("rm " + DTM_DIR + dtm_base_name + "_tmp_correct_nodata.tif")
      os.system("rm " + DTM_DIR + "input.tif")
      os.system("rm " + DTM_DIR + "input.tif.aux.xml")
      os.system("rm " + DTM_DIR + "output.tif.aux.xml")
#      os.system("rm " + DTM_DIR + dtm_xyz_name)


# Höhenkurven

os.system( "gdalbuildvrt " + DTM_DIR + "dtm.vrt " + DTM_DIR + "*.tif" );

for i in range(0, layer2.GetFeatureCount()):
  feature2 = layer2.GetFeature(i)
  geom2 = feature2.GetGeometryRef()
  nummer = feature2.GetField('nummer')

  if geom2.Intersects(geom1): 
    dtm_xyz_gz_name = nummer.replace("-", "") +"_dtm_03_02.xyz.gz";
    dtm_xyz_name = nummer.replace("-", "") +"_dtm_03_02.xyz";
    dtm_base_name = nummer.replace("-", "") +"_dtm_03_02";
    dtm_tif_name = nummer.replace("-", "") +"_dtm_03_02.tif";
    
    if os.path.isfile(DTM_DIR + dtm_tif_name):
      print dtm_tif_name

      dtm_base_name = nummer.replace("-", "") +"_dtm_03_02";
      dtm_tif_name = nummer.replace("-", "") +"_dtm_03_02.tif";

      extent = geom2.GetEnvelope()
      minX, maxX, minY, maxY = extent

      cmd = "gdal_translate -projwin " + str(minX-50) + " " + str(maxY+50) + " " + str(maxX+50) + " " + str(minY-50) + " " + DTM_DIR + "dtm.vrt " + DTM_DIR + "input.tif";
      os.system(cmd);
    
      input = DTM_DIR + "input.tif"
      output = DTM_DIR + "output.tif"
    
      for i in range(10):
        cmd = "gdalwarp -co COMPRESS=PACKBITS -r cubicspline " + input + " " + output
#        os.system(cmd)
#        os.system("cp " + output + " " + input )
#        os.system("rm " + output)

      cmd = "gdal_contour -a elev -i 10.0 " + input + " " + DTM_DIR + "contour_tmp.shp"
      os.system(cmd)
      
      # Zurechtscheiden auf Ursprungskachel und Kanton
      clip_wkt = geom2.ExportToWkt()
      cmd = "ogr2ogr -clipsrc '" + clip_wkt + "' " + DTM_DIR + "contour_tmp_clip_extent.shp " + DTM_DIR + "contour_tmp.shp"
      os.system(cmd)

      # zuerst kantons-shape erzeugen (ogr2ogr sqlite dialect...)
      # dann clippen

#      cmd = "ogr2ogr -clipsrc '" + clip_wkt + "' " + DTM_DIR + "contour_tmp_clip_canton.shp " + DTM_DIR + "contour_tmp_clip_extent.shp"
#      print cmd

#      os.system(cmd)

      
#      shp3 = ogr.Open(DTM_DIR + "contour_tmp.shp")
#      layer3 = shp3.GetLayer(0)
#    
#      for feature3 in layer3:
#        print "fooo"
#        geom3 = feature3.GetGeometryRef()
        

      
#      os.system("rm " + DTM_DIR + "contour_tmp.*")
#      os.system("rm " + DTM_DIR + "contour_tmp_clip_extent.*")
#      os.system("rm " + DTM_DIR + "contour_tmp_clip_canton.*")
      
      
      
      #os.system("rm " + DTM_DIR + dtm_base_name + "_tmp.tif")

print "Hallo Stefan."
