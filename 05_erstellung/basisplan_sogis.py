#!/usr/bin/python
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------
# 
# Script for generation of the Basisplan AV
#
# Copyright (C) 2012 Andreas Schmid
#
# EMAIL: andreas.schmid (at) bd.so.ch
# WEB  : www.sogis.ch
#
#---------------------------------------------------------------------
# 
# licensed under the terms of GNU GPL 2
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 
#---------------------------------------------------------------------

## Import python stuff
import os, sys, time, math, copy, datetime, csv, logging, urllib, urllib2, subprocess, shutil, optparse


class Settings:
  """Contains all the settings and their default values.
  Keep in mind that OptionParser also provides default values.
  These overwrite the default values specified here. """
  def __init__(self):
    ## Die Ausführung des Skripts nur simulieren?
    self.simulate = False
    ## Die Zwischenergebnisse (PNG-Dateien, unkomprimierte GeoTIFFs) beibehalten statt sie zu löschen?
    self.keep_tempfiles = False
    ## Keine Bilder vom WMS anfordern (d.h. den Basisplan aus noch vorhandenen, früher heruntergeladenen Bildern erzeugen)
    self.no_download = False
    ## Die fertigen Tiles in ein bestimmtes Zielverzeichnis kopieren?
    self.copy_to_targetdir = False
    ## Verzeichnis, in welches die Dateien nach dem Erstellen verschoben werden sollen (optionaler Schritt)
    self.targetdir = ""
    ## DPI und Massstab
    self.dpi = 508
    self.scale = 5000
    ## Farbig (f) oder schwarz-weiss (sw) erstellen?
    self.colortype = "f"
    ## Nur Situation (s), nur Liegenschaften (l) oder beides (b, default) erstellen?
    self.mode = "b"
    ## Datei mit der Definition der Basisplan-Kacheln
    self.tileindex = ""
    ## Name einer spezifischen zu erstellenden Kachel (falls man nur eine einzelne Kachel aus der gesamten Definition erstellen möchte)
    self.restrict_tile = ""
    ## Anzahl WMS-Teilrequests pro Kachel (wird nur für die den Situation-Layer berücksichtigt)
    self.numrequests = 1
    ## Überlappung der Beschriftungslayer in x- und y-Richtung
    self.overlapx = 100.0
    self.overlapy = 50.0
    ## Beginn der URL des WMS, inkl. Slash (/) als letztes Zeichen (d.h. URL des WMS ohne Name des QGIS-Projektfiles)
    ## Die komplette URL des WMS wird von der Methode get_wms_url() zurückgegeben.
    self._base_wms_url = "http://localhost/cgi-bin/qgis_mapserv.fcgi?map=/usr/lib/cgi-bin/"
    ## Anzahl Versuche bei WMS GetMap Requests
    self.getmap_retries = 3
    ## Ouput Verzeichnis (Verzeichnis, in welchem die Dateien erstellt werden)
    self.outdir = ""
    ## Inhalt der Tiles auf Kantonsfläche clippen?
    self.clip = True
    ## Für Clip auf Kantonsfläche: Verbindung zur DB (Beachten: Falls man hier zusätzlich ein Passwort angibt (password=soundso), wird dieses auch in den Logfiles erscheinen, weil alle Optionen im Logfile registriert werden (mit Log-Level INFO))
    ## Aus Gründen der Analogie zur Eigenschaft _clip_cutlinesql soll mit der Methode get_clip_cutline() auf diesen Wert zugegriffen werden.
    self._clip_cutline = "PG:\"host=srsofaioi4531.ktso.ch dbname=sogis user=mspublic\""
    ## Für Clip auf Kantonsfläche: Zu wählende Geometrie für Clip
    ## Einerseits wird die Kantonsfläche gewählt, andererseits Bufferflächen von der halben Differenz der Breiten der Kantons- und Landesgrenzsignaturen um die Landesgrenzabschnitte herum. Damit wird erreicht, dass die Landesgrenzsignaturen, die breiter sind als die Kantonsgrenzsignaturen, nicht abgeschnitten werden. Die Distanz des zusätzlichen Buffers bei den Landesgrenzabschnitten wird ähnlich ermittelt wie die Bufferdistanz um die Kantonsgrenzen herum. Die Differenz zwischen den Breiten der Kantons- und Landesgrenzsignaturen wird in der Berechnung als Bruchteil der Breite der Kantonsgrenzsignatur eingesetzt. (Die Differenz ist 0.8mm, dies entspricht 2/3 von 1.2mm, der Breite der Kantonsgrenzsignatur.)
    ## Für Kantone ohne Landesgrenzabschnitt kann wie weiter unten beschrieben eine vereinfachte Abfrage verwendet werden.
    ## Der komplette SQL-Ausdruck wird von der Methode get_clip_cutlinesql() zurückgegeben, wobei der buffer_radius ermittelt wird. Dabei wird der String "<<<buffer_radius>>>" durch den ermittelten Buffer-Radius ersetzt.
    self._clip_cutlinesql = "\"SELECT ST_SetSRID(ST_Buffer(geometrie,<<<buffer_radius>>>),-1) FROM (SELECT ST_Union(ARRAY(SELECT geometrie FROM av_basisplan.maske_kanton WHERE art='Kantonsfläche' UNION SELECT ST_Buffer(geometrie,2.0 / 3.0 * <<<buffer_radius>>>,'endcap=flat') FROM av_avdpool_ng.landesgrenzen_landesgrenzabschnitt)) AS geometrie) AS kantonsflache_und_landesgrenzbuffer\""
    ## Für Kantone ohne Landesgrenzabschnitt kann folgende vereinfachte Abfrage verwendet werden:
    ##self._clip_cutlinesql = "\"SELECT ST_SetSRID(ST_Buffer(geometrie,<<<buffer_radius>>>),-1) FROM av_basisplan.maske_kanton WHERE art='Kantonsfläche'\""
  
  ## WMS URL
  def get_wms_url(self):
    return self._base_wms_url + "bpav" + str(self.scale) + self.colortype + ".qgs"
  
  ## Cutline-Parameter für Clip
  def get_clip_cutline(self):
    return self._clip_cutline
  
  ## Cutline-SQL-Parameter für Clip
  def get_clip_cutlinesql(self):
    REFERENZMASSSTAB = 5000.0
    BREITE_MM_KANTONSGRENZE = 1.2
    return self._clip_cutlinesql.replace("<<<buffer_radius>>>", str(BREITE_MM_KANTONSGRENZE * math.sqrt(REFERENZMASSSTAB / float(self.scale)) * float(self.scale) / 1000.0 / 2.0))
  
  ## Namen der WMS-Gruppenlayer
  def get_layers_situ(self):
    return "bpav" + str(self.scale) + self.colortype + "_situation"
  def get_layers_beschr(self):
    return "bpav" + str(self.scale) + self.colortype + "_beschriftungen"
  def get_layers_beschr_halo(self):
    return self.get_layers_beschr() + ",bpav" + str(self.scale) + self.colortype + "_hintergrundfl_beschriftungen"
  def get_layers_liegen(self):
    return "bpav" + str(self.scale) + self.colortype + "_liegenschaften"
  
  ## Logfile (Pfad inkl. Dateiname)
  def get_logfile_path(self):
    return os.path.join(self.outdir, "bpav" + str(self.scale) + self.colortype + "_log.txt")



def parse_options():
  ## Get options from command arguments
  optparser = optparse.OptionParser(usage="usage: %prog [options] tileindex outdir\n \
  Example: basisplan.py -p 3 --tile 1088-44 /home/username/tileindex_bpav5000.csv /home/username/bpav5000f", 
  version="%prog 1.5")
  optparser.add_option("--simulate",
    action = "store_true",
    dest = "simulate",
    default = False,
    help = "simulate, don't download anything and don't create any file")
  optparser.add_option("-k", "--keep_temporary",
    action = "store_true",
    dest = "keep_tempfiles",
    default = False,
    help = "keep the temporary files (PNGs, temporary VRTs) instead of removing them")
  optparser.add_option("--no_download",
    action = "store_true",
    dest = "no_download",
    default = False,
    help = "don't download any images from the WMS, use existing ones instead")
  optparser.add_option("-t","--targetdir",
    action = "store",
    type = "string",
    dest = "targetdir",
    default = "",
    help = "directory to move the finished tiles to. If not specified, the tiles will remain in the outdir.")
  optparser.add_option("-r","--dpi",
    action = "store",
    type = "int",
    dest = "dpi",
    default = 508,
    help = "Resolution (dpi) to generate the tiles at. Default: 508")
  optparser.add_option("-s", "--scale",
    action = "store",
    type = "int",
    dest = "scale",
    default = 5000,
    help = "scale of the map. Default: 5000 (for 1:5000)")
  optparser.add_option("-c", "--colortype",
    action = "store",
    type = "choice",
    dest = "colortype",
    default = "f",
    choices = ["f", "sw"],
    help = "color (f) or black/white (sw) map. Default: f")
  optparser.add_option("--noclip",
    action = "store_false",
    dest = "clip",
    default = True,
    help = "don't clip the output to a geometry which is specified in the script settings")
  optparser.add_option("-l", "--layer",
    action = "store",
    type = "choice",
    dest = "mode",
    default = "b",
    choices = ["s", "l", "b"],
    help = "generate just the situation (s), the real estate (Liegenschaften, l), or both (b). Default: b")
  optparser.add_option("--tile",
    action = "store",
    type = "string",
    dest = "restrict_tile",
    default = "",
    help = "Only create the tile with the specified name, even if there are more tiles in the tile index than just this one. This tile must be listed in the tile index file.")
  optparser.add_option("-p","--partial_requests",
    action = "store",
    type = "int",
    dest = "numrequests",
    default = 1,
    help = "Number of partial requests to create the tile in (concerns the situation layer only). Default: 1")
  optparser.add_option("-o","--overlap",
    action = "store",
    type = "string",
    dest = "overlap",
    default = "100.0 50.0",
    help = "Overlap (meters) in x and y direction to use for improved creation of the label layer (e.g. '0 0'). Default: '100.0 50.0'")

  # instantiate a Settings object
  settings = Settings()

  # parse the options and arguments
  (options, args) = optparser.parse_args()

  # assign the values of the positional arguments (mandatory arguments) to the settings object attributes
  # Positional arguments information:
  # 0: tileindex: Path to the CSV file containing the extent and number of the tiles (tile index). Example: "/home/username/directory/bpav5000.csv"
  # 1: outdir:   Example: /opt/tmp_avbasis/bpav5000f
  if len(args) != 2:
    optparser.error("wrong number of arguments (2 arguments required)")
  else:
    settings.tileindex = args[0]
    settings.outdir = args[1]

  # assign the option values to the settings object attributes
  settings.simulate = options.simulate
  settings.keep_tempfiles = options.keep_tempfiles
  settings.no_download = options.no_download
  settings.targetdir = options.targetdir
  if settings.targetdir == "":
    settings.copy_to_targetdir = False
  else:
    settings.copy_to_targetdir = True
  settings.dpi = options.dpi
  settings.scale = options.scale
  settings.colortype = options.colortype
  settings.clip = options.clip
  settings.mode = options.mode
  settings.restrict_tile = options.restrict_tile
  settings.numrequests = options.numrequests
  overlap = str.split(options.overlap)
  try:
    if len(overlap) == 1:
      settings.overlapx = float(overlap[0])
      settings.overlapy = float(overlap[0])
    elif len(overlap) == 2:
      settings.overlapx = float(overlap[0])
      settings.overlapy = float(overlap[1])
    else:
      optparser.error("invalid overlap argument")
  except ValueError:
    optparser.error("invalid overlap argument")
  
  return settings



## Methode zum Löschen von Dateien
## Parameter:
## fname: Datei, die gelöscht werden soll
def deleteFile(fname):
  try:
    os.remove(fname)
  except OSError as e:
    logging.error(fname + " could not be deleted: " + str(e))
  except Exception as e:
    logging.exception(e)
  else:
    logging.debug(fname + " deleted")



## Methode zum Loggen der Grösse eines Verzeichnis
## Parameter:
## directory: Verzeichnis, dessen Grösse geloggt werden soll
def logDirectorySize(directory):
  try:
    args = ['du', '-hs', directory]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    returncode = p.returncode
    if returncode <> 0:
      raise Exception(stderrdata)
      #raise subprocess.CalledProcessError(returncode, ' '.join(args)) # Variante, leider kann hier aber stderrdata nicht mitgeliefert werden
  except Exception as e:
    logging.warning("Command '" + ' '.join(args) + "' was not successful")
    logging.warning(e)
  else:
    logging.info("The size of " + directory + " is now " + stdoutdata)
  # different approach, but did not work:
  #try:
  #  call = subprocess.check_call(['du', '-hs', directory])
  #except subprocess.CalledProcessError as e:
  #  logging.warning("The size of " + directory + " could not be determined. See also the following warning.")
  #  logging.warning(e)
  #else:
  #  logging.info("The size of " + directory + " is now ...")
          


## Kacheln gemäss der in tileinfo enthaltenen Ausdehnung herunterladen
## Rückgabewert ist ein dictionary mit URLs und Pfaden der Bilder, die nicht heruntergeladen werden konnten
def getImages(settings, tileinfo, numrequests, overlapx, overlapy, transparent, layersstring, layerssuffix):
  failed_downloads = {}
  tilenr = tileinfo['nummer']
  xmin = float(tileinfo['XMIN']) - overlapx
  xmax = float(tileinfo['XMAX']) + overlapx
  ymin = float(tileinfo['YMIN']) - overlapy
  ymax = float(tileinfo['YMAX']) + overlapy
  
  dx = xmax - xmin
  dy = ymax - ymin
  
  ## TODO ist Runden i.O.?
  width = round((dx/settings.scale) / 0.0254 * settings.dpi)
  height = round((dy/settings.scale) / 0.0254 * settings.dpi)
  
  for i in range(numrequests):
    filename = "bpav" + str(settings.scale) + settings.colortype + "_" + tilenr + "_" + str(int(i+1))
    url = settings.get_wms_url()
    bbox = str(xmin) + "," + str(ymin + i * dy / numrequests) + "," + str(xmax) + "," + str(ymin + (i + 1) * dy / numrequests)
    widthstring = str(int(width))
    heightstring =  str(int(height / numrequests))
    imageformat = "image/png"
    if settings.colortype == "sw":
      imageformat = "image/png; mode=1bit"
    
    params = {
      "SERVICE": "WMS",
      "VERSION": "1.3.0",
      "REQUEST": "GetMap",
      "LAYERS": layersstring,
      "STYLES": "",
      "TRANSPARENT": str(transparent),
      "CRS": "EPSG:21781",
      "BBOX": bbox,
      "WIDTH": widthstring,
      "HEIGHT": heightstring,
      "DPI": str(settings.dpi),
      "FORMAT": imageformat}
      
    if not "?" in url:
      url += "?"
    else:
      if not (url.endswith("?") or url.endswith("&")):
        url += "&"
    
    url_params = urllib.urlencode(params)
    url += url_params
    
    filepath = os.path.join(settings.outdir, filename + layerssuffix + ".png")
    
    logging.log(logging.DEBUG, "Downloading " + filename + layerssuffix + ".png")
    logging.log(logging.DEBUG, "URL: " + url)
    logging.log(logging.DEBUG, "bbox: " + bbox + " width, height: " + widthstring + ", " + heightstring)
    wmsrequest_starttime = datetime.datetime.now()
    if not settings.simulate:
      getmap_success = False
      for r in range(settings.getmap_retries):
        if r > 0:
          logging.info("This is try number " + str(r + 1) + " for downloading " + filename + layerssuffix + ".png")
        try:
          response = urllib2.urlopen(url)
          if "image/png" in response.info()["Content-Type"]:
            img = response.read()
            logging.debug("Saving file to " + filepath)
            open(filepath, 'wb').write(img)
            getmap_success = True
          elif "text" in response.info()["Content-Type"]:
            logging.warning("Invalid content type: " + response.info()["Content-Type"] + ". Saving file to " + filepath + ".txt")
            img = response.read()
            open(filepath + ".txt", 'wb').write(img)
          else:
            logging.warning("Invalid content type: " + response.info()["Content-Type"] + ". File not saved.")
        except urllib2.URLError as e:
          msg = "The server couldn't fulfill the request."
          if hasattr(e, "code"):
            msg += " HTTP status code: " + str(e.code) + "."
          #if hasattr(e, "reason"):
          #  msg += " Reason: " + str(e.reason)
          logging.info(msg)
        except IOError as e:
          logging.exception(e)
        except Exception as e:
          logging.exception(e)
        else:
          logging.debug("Downloaded a file from the WMS")
        if getmap_success:
          break
        else:
          if r == settings.getmap_retries - 1:
            # add the filepath and URL of the failed download to the dictionary:
            failed_downloads[url] = filepath
            logging.warning(filename + layerssuffix + ".png failed to download. Will retry later.")
    wmsrequest_duration = datetime.datetime.now() - wmsrequest_starttime
    logging.info("Download of " + filepath + " complete. Duration: " + str(wmsrequest_duration.seconds) + " sec")
    
    ## Worldfile schreiben
    logging.debug("Writing world file: " + filepath + "w")
    if not settings.simulate:
      try:
        outfile = open(filepath + "w",  "w")
      except IOError:
        logging.exception("Could not write world file")
      else:
        res = dx/width
        outfile.write(str(res))
        outfile.write("\n")
        outfile.write("0.0")
        outfile.write("\n")
        outfile.write("0.0")
        outfile.write("\n")
        outfile.write(str(-1 * res))
        outfile.write("\n")
        outfile.write(str(xmin + 0.5 * res))
        outfile.write("\n")
        outfile.write(str((ymin + (i + 1) * dy / numrequests) - 0.5 * res))
        outfile.close()
        logging.debug("Writing world file sucessful.")
        
  return failed_downloads


## Bilder anfordern, die zuvor fehlgeschlagen sind
## Parameter:
## failed_downloads: dictionary, welcher URLs und Pfade der nochmals herunterzuladenden Dateien enthält
## Rückgabewert ist ein dictionary mit URLs und Pfaden der Bilder, die definitiv nicht heruntergeladen werden konnten
def getFailedImages(settings, failed_downloads):
  failed_again = {}
  for url, filepath in sorted(failed_downloads.iteritems()):
    logging.debug("Trying to download " + filepath + " again")
    wmsrequest_starttime = datetime.datetime.now()
    if not settings.simulate:
      getmap_success = False
      for r in range(settings.getmap_retries):
        if r > 0:
          logging.info("This is try number " + str(r + 1) + " for downloading " + filepath)
        try:
          response = urllib2.urlopen(url)
          if "image/png" in response.info()["Content-Type"]:
            img = response.read()
            logging.debug("Saving file to " + filepath)
            open(filepath, 'wb').write(img)
            getmap_success = True
          elif "text" in response.info()["Content-Type"]:
            logging.warning("Invalid content type: " + response.info()["Content-Type"] + ". Saving file to " + filepath + ".txt")
            img = response.read()
            open(filepath + ".txt", 'wb').write(img)
          else:
            logging.warning("Invalid content type: " + response.info()["Content-Type"] + ". File not saved.")
        except urllib2.URLError as e:
          msg = "The server couldn't fulfill the request."
          if hasattr(e, "code"):
            msg += " HTTP status code: " + str(e.code) + "."
          #if hasattr(e, "reason"):
          #  msg += " Reason: " + str(e.reason)
          logging.info(msg)
        except IOError as e:
          logging.exception(e)
        except Exception as e:
          logging.exception(e)
        else:
          logging.debug("Downloaded a file from the WMS")
        if getmap_success:
          break
        else:
          if r == settings.getmap_retries - 1:
            # this has been the last try
            logging.error(filepath + " could definitely not be downloaded")
            failed_again[url] = filepath
    wmsrequest_duration = datetime.datetime.now() - wmsrequest_starttime
    logging.info("Download of " + filepath + " complete. Duration: " + str(wmsrequest_duration.seconds) + " sec")
  if len(failed_again) > 0:
    logging.error("The following files could definitely not be downloaded: " + str(failed_again.values()))
  return failed_again
    


## Verarbeitung der Situation zu GeoTIFFs (farbig)
def postprocessSituationF(settings, tileinfo, numrequests):
  tilenr = tileinfo['nummer']
  xmin = float(tileinfo['XMIN'])
  xmax = float(tileinfo['XMAX'])
  ymin = float(tileinfo['YMIN'])
  ymax = float(tileinfo['YMAX'])
  
  logging.debug("Processing tile " + tilenr)
  basefilename = "bpav" + str(settings.scale) + settings.colortype + "_" + tilenr
  tileprocessing_starttime = datetime.datetime.now()
  
  try:
    ## Bilder (Situation) zu einem VRT zusammensetzen
    logging.debug("Creating a VRT (Situation):")
    cmd = "gdalbuildvrt -q " + os.path.join(settings.outdir, basefilename + "_situation.vrt") + " "
    for i in range(numrequests):
      cmd += os.path.join(settings.outdir, basefilename + "_" + str(i+1) + "_situation.png") + " "
    logging.log(logging.DEBUG, cmd)
    if not settings.simulate:
      os.system(cmd)
    logging.debug(os.path.join(settings.outdir, basefilename + "_situation.vrt") + " created")
    
    ## Beschriftungen überlagern
    logging.debug("Overlay labels:")
    cmd = "gdalwarp -q -wm 512 -overwrite -co 'TILED=YES' -s_srs EPSG:21781 -t_srs EPSG:21781 -te " + str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax) + " -of GTiff " 
    if settings.clip == True:
      cmd += "-dstalpha -cutline " + settings.get_clip_cutline() + " -csql " + settings.get_clip_cutlinesql() + " "
    cmd += os.path.join(settings.outdir, basefilename + "_situation.vrt") + " " + os.path.join(settings.outdir, basefilename + "_1_beschriftungen.png") + " " + os.path.join(settings.outdir, basefilename + "_72ppi.tif")
    logging.log(logging.DEBUG, cmd)
    imageprocessing_starttime = datetime.datetime.now()
    if not settings.simulate:
      os.system(cmd)
    imageprocessing_duration = datetime.datetime.now() - imageprocessing_starttime
    logging.log(logging.DEBUG, "Duration (overlay labels with gdalwarp): " + str(imageprocessing_duration.seconds) + " sec")
    
    ## Komprimieren und Auflösungsangabe (PPI) korrigieren
    logging.debug("Compress file:")
    cmd = "gdal_translate -q -mo TIFFTAG_XRESOLUTION=508 -mo TIFFTAG_YRESOLUTION=508 -of GTiff -co 'TILED=YES' "
    if settings.colortype == "f":
      cmd += "-co 'COMPRESS=LZW' "
    else:
      cmd += "-co 'COMPRESS=CCITTFAX4' -co 'NBITS=1' "
    cmd += os.path.join(settings.outdir, basefilename + "_72ppi.tif") + " " + os.path.join(settings.outdir, basefilename + ".tif")
    logging.log(logging.DEBUG, cmd)
    imageprocessing_starttime = datetime.datetime.now()
    if not settings.simulate:
      os.system(cmd)
    imageprocessing_duration = datetime.datetime.now() - imageprocessing_starttime
    logging.log(logging.DEBUG, "Duration (compressing): " + str(imageprocessing_duration.seconds) + " sec")
    
    ## Overviews hinzufügen
    logging.debug("Add overviews:")
    cmd = "gdaladdo -q -r average " + os.path.join(settings.outdir, basefilename + ".tif") + " 2 4 8 16 32"
    logging.log(logging.DEBUG, cmd)
    imageprocessing_starttime = datetime.datetime.now()
    if not settings.simulate:
      os.system(cmd)
    imageprocessing_duration = datetime.datetime.now() - imageprocessing_starttime
    logging.log(logging.DEBUG, "Duration (adding overviews): " + str(imageprocessing_duration.seconds) + " sec")
  except:
    logging.exception("Processing of tile " + tilenr + " failed.")
    # try to remove the resulting tif
    deleteFile(os.path.join(settings.outdir, basefilename + ".tif"))
  else:
    # remove the processed png and pngw files
    if not settings.simulate and not settings.keep_tempfiles:
      for i in range(numrequests):
        deleteFile(os.path.join(settings.outdir, basefilename + "_" + str(i+1) + "_situation.png"))
        deleteFile(os.path.join(settings.outdir, basefilename + "_" + str(i+1) + "_situation.pngw"))
      deleteFile(os.path.join(settings.outdir, basefilename + "_1_beschriftungen.png"))
      deleteFile(os.path.join(settings.outdir, basefilename + "_1_beschriftungen.pngw"))
    # create a vrt file referencing all the finished tif files
    logging.debug("Create vrt file:")
    cmd = "gdalbuildvrt -q " + os.path.join(settings.outdir, "bpav" + str(settings.scale) + settings.colortype + ".vrt") + " " + os.path.join(settings.outdir, "bpav" + str(settings.scale) + settings.colortype + "_*[!ni].tif") # *[!ni] excludes the *_liegenschaften.tif and *_72ppi.tif files
    logging.debug(cmd)
    if not settings.simulate:
      os.system(cmd)
  finally:
    # remove the temporary files
    if not settings.simulate and not settings.keep_tempfiles:
      deleteFile(os.path.join(settings.outdir, basefilename + "_situation.vrt"))
      deleteFile(os.path.join(settings.outdir, basefilename + "_72ppi.tif"))
  
  tileprocessing_duration = datetime.datetime.now() - tileprocessing_starttime
  logging.info(tilenr + " processed. Duration: " + str(tileprocessing_duration) + " sec")

## Verarbeitung der Liegenschaften zu GeoTIFFs (farbig)
def postprocessLiegenschaftenF(settings, tileinfo, numrequests):
  tilenr = tileinfo['nummer']
  xmin = float(tileinfo['XMIN'])
  xmax = float(tileinfo['XMAX'])
  ymin = float(tileinfo['YMIN'])
  ymax = float(tileinfo['YMAX'])
  
  logging.debug("Processing tile " + tilenr + " (Liegenschaften)")
  basefilename = "bpav" + str(settings.scale) + settings.colortype + "_" + tilenr
  tileprocessing_starttime = datetime.datetime.now()

  try:
    ## In GeoTIFF konvertieren, komprimieren und Auflösungsangabe (PPI) korrigieren
    logging.debug("Convert and compress file:")
    cmd = "gdal_translate -q -a_srs EPSG:21781 -of GTiff -co 'TILED=YES' -co 'COMPRESS=LZW' -mo TIFFTAG_XRESOLUTION=508 -mo TIFFTAG_YRESOLUTION=508 " + os.path.join(settings.outdir, basefilename + "_1_liegenschaften.png") + " " + os.path.join(settings.outdir, basefilename + "_liegenschaften.tif")
    logging.log(logging.DEBUG, cmd)
    imageprocessing_starttime = datetime.datetime.now()
    if not settings.simulate:
      os.system(cmd)
    imageprocessing_duration = datetime.datetime.now() - imageprocessing_starttime
    logging.log(logging.DEBUG, "Duration (converting and compressing): " + str(imageprocessing_duration.seconds) + " sec")
    
    ## Overviews hinzufügen
    logging.debug("Add overviews:")
    cmd = "gdaladdo -q -r average " + os.path.join(settings.outdir, basefilename + "_liegenschaften.tif") + " 2 4 8 16 32"
    logging.log(logging.DEBUG, cmd)
    imageprocessing_starttime = datetime.datetime.now()
    if not settings.simulate:
      os.system(cmd)
    imageprocessing_duration = datetime.datetime.now() - imageprocessing_starttime
    logging.log(logging.DEBUG, "Duration (adding overviews): " + str(imageprocessing_duration.seconds) + " sec")
  except:
    logging.exception("Processing of tile " + tilenr + " (Liegenschaften) failed.")
    # try to remove the resulting tif
    deleteFile(os.path.join(settings.outdir, basefilename + "_liegenschaften.tif"))
  else:
    # remove the processed png and pngw files
    if not settings.simulate and not settings.keep_tempfiles:
      deleteFile(os.path.join(settings.outdir, basefilename + "_1_liegenschaften.png"))
      deleteFile(os.path.join(settings.outdir, basefilename + "_1_liegenschaften.pngw"))
    # create a vrt file referencing all the finished tif files
    logging.debug("Create vrt file:")
    cmd = "gdalbuildvrt -q " + os.path.join(settings.outdir, "bpav" + str(settings.scale) + settings.colortype + "_liegenschaften.vrt") + " " + os.path.join(settings.outdir, "bpav" + str(settings.scale) + settings.colortype + "_*_liegenschaften.tif")
    logging.debug(cmd)
    if not settings.simulate:
      os.system(cmd)
 
  tileprocessing_duration = datetime.datetime.now() - tileprocessing_starttime
  logging.info(tilenr + " (Liegenschaften) processed. Duration: " + str(tileprocessing_duration) + " sec")

## Verarbeitung der Situation zu GeoTIFFs (schwarz-weiss)
def postprocessSituationSw(settings, tileinfo, numrequests):
  tilenr = tileinfo['nummer']
  xmin = float(tileinfo['XMIN'])
  xmax = float(tileinfo['XMAX'])
  ymin = float(tileinfo['YMIN'])
  ymax = float(tileinfo['YMAX'])
  
  logging.debug("Processing tile " + tilenr)
  basefilename = "bpav" + str(settings.scale) + settings.colortype + "_" + tilenr
  tileprocessing_starttime = datetime.datetime.now()
  
  try:
    ## Für den Beschriftungslayer den NODATA-Wert definieren (0)
    logging.debug("Preparing the label layer:")
    cmd = ""
    ## Das Clippen (cutline) könnte analog zur Farbvariante erst im späteren Schritt "Bilder zum vollständigen VRT zusammensetzen" über alle VRTs vorgenommen werden.
    ## Weil es aber möglicherweise performanter ist und das Resultat dasselbe ist, wird nur der Beschriftungslayer geclippt.
    ## In der schwarz-weissen Variante geht es nur darum, die ausserkantonalen Gebiete weiss abzudecken. Es kommt keine Transparenz zum Einsatz.
    if settings.clip == True:
      cmd = "gdalwarp -q -wm 512 -overwrite -dstnodata 0 -of VRT -cutline " + settings.get_clip_cutline() + " -csql " + settings.get_clip_cutlinesql() + " " + os.path.join(settings.outdir, basefilename + "_1_beschriftungen.png") + " " + os.path.join(settings.outdir, basefilename + "_beschriftungen.vrt")
    else:
      cmd = "gdalbuildvrt -q -srcnodata 0 " + os.path.join(settings.outdir, basefilename + "_beschriftungen.vrt") + " " + os.path.join(settings.outdir, basefilename + "_1_beschriftungen.png")
    logging.log(logging.DEBUG, cmd)
    if not settings.simulate:
      os.system(cmd)
    logging.debug(os.path.join(settings.outdir, basefilename + "_beschriftungen.vrt") + " created")
    
    ## Für den Halo-Layer den NODATA-Wert definieren (1)
    if settings.colortype == "sw":
      logging.debug("Preparing the label halo layer:")
      cmd = "gdalbuildvrt -q -srcnodata 1 " + os.path.join(settings.outdir, basefilename + "_beschriftungenhalo.vrt") + " " + os.path.join(settings.outdir, basefilename + "_1_beschriftungenhalo.png")
      logging.log(logging.DEBUG, cmd)
      if not settings.simulate:
        os.system(cmd)
      logging.debug(os.path.join(settings.outdir, basefilename + "_beschriftungenhalo.vrt") + " created")
    
    ## Bilder zum vollständigen VRT zusammensetzen
    logging.debug("Creating the complete tile as VRT:")
    cmd = "gdalbuildvrt -q -te " + str(xmin) + " " + str(ymin) + " " + str(xmax) + " " + str(ymax) + " " + os.path.join(settings.outdir, basefilename + ".vrt") + " "
    for i in range(numrequests):
      cmd += os.path.join(settings.outdir, basefilename + "_" + str(i+1) + "_situation.png") + " "
    if settings.colortype == "sw":
      cmd += os.path.join(settings.outdir, basefilename + "_beschriftungenhalo.vrt") + " " 
    cmd += os.path.join(settings.outdir, basefilename + "_beschriftungen.vrt")
    logging.log(logging.DEBUG, cmd)
    if not settings.simulate:
      os.system(cmd)
    logging.debug(os.path.join(settings.outdir, basefilename + ".vrt") + " created")
    
    ## VRT in GeoTIFF konvertieren, komprimieren und Auflösungsangabe (PPI) korrigieren
    logging.debug("Convert file to GeoTIFF:")
    cmd = "gdal_translate -q -a_srs EPSG:21781 -mo TIFFTAG_XRESOLUTION=508 -mo TIFFTAG_YRESOLUTION=508 -of GTiff -co 'TILED=YES' "
    if settings.colortype == "f":
      cmd += "-co 'COMPRESS=LZW' "
    else:
      cmd += "-co 'COMPRESS=CCITTFAX4' -co 'NBITS=1' "
    cmd += os.path.join(settings.outdir, basefilename + ".vrt") + " " + os.path.join(settings.outdir, basefilename + ".tif")
    logging.log(logging.DEBUG, cmd)
    imageprocessing_starttime = datetime.datetime.now()
    if not settings.simulate:
      os.system(cmd)
    imageprocessing_duration = datetime.datetime.now() - imageprocessing_starttime
    logging.log(logging.DEBUG, "Duration (converting to GeoTIFF): " + str(imageprocessing_duration.seconds) + " sec")
    
    ## Overviews hinzufügen
    if settings.colortype == "sw":
      logging.debug("Add overviews:")
      cmd = "gdaladdo -q -r nearest " + os.path.join(settings.outdir, basefilename + ".tif") + " 2 4 8 16 32"
      logging.log(logging.DEBUG, cmd)
      imageprocessing_starttime = datetime.datetime.now()
      if not settings.simulate:
        os.system(cmd)
      imageprocessing_duration = datetime.datetime.now() - imageprocessing_starttime
      logging.log(logging.DEBUG, "Duration (adding overviews): " + str(imageprocessing_duration.seconds) + " sec")
  except:
    logging.exception("Processing of tile " + tilenr + " failed.")
    # try to remove the resulting tif
    deleteFile(os.path.join(settings.outdir, basefilename + ".tif"))
  else:
    # remove the processed png and pngw files
    if not settings.simulate and not settings.keep_tempfiles:
      for i in range(numrequests):
        deleteFile(os.path.join(settings.outdir, basefilename + "_" + str(i+1) + "_situation.png"))
        deleteFile(os.path.join(settings.outdir, basefilename + "_" + str(i+1) + "_situation.pngw"))
      deleteFile(os.path.join(settings.outdir, basefilename + "_1_beschriftungen.png"))
      deleteFile(os.path.join(settings.outdir, basefilename + "_1_beschriftungen.pngw"))
      if settings.colortype == "sw":
        deleteFile(os.path.join(settings.outdir, basefilename + "_1_beschriftungenhalo.png"))
        deleteFile(os.path.join(settings.outdir, basefilename + "_1_beschriftungenhalo.pngw"))
    # create a vrt file referencing all the finished tif files
    logging.debug("Create vrt file:")
    cmd = "gdalbuildvrt -q " + os.path.join(settings.outdir, "bpav" + str(settings.scale) + settings.colortype + ".vrt") + " " + os.path.join(settings.outdir, "bpav" + str(settings.scale) + settings.colortype + "_*[!ni].tif") # *[!ni] excludes the *_liegenschaften.tif and *_72ppi.tif files
    logging.debug(cmd)
    if not settings.simulate:
      os.system(cmd)
  finally:
    # remove the vrt files
    if not settings.simulate and not settings.keep_tempfiles:
      deleteFile(os.path.join(settings.outdir, basefilename + "_beschriftungen.vrt"))
      if settings.colortype == "sw":
        deleteFile(os.path.join(settings.outdir, basefilename + "_beschriftungenhalo.vrt"))
      deleteFile(os.path.join(settings.outdir, basefilename + ".vrt"))
      
  # Log the processing duration for this tile
  tileprocessing_duration = datetime.datetime.now() - tileprocessing_starttime
  logging.info("Duration for processing tile " + tilenr + ": " + str(tileprocessing_duration) + " sec")
  
## Verarbeitung der Liegenschaften zu GeoTIFFs (schwarz-weiss)
def postprocessLiegenschaftenSw(settings, tileinfo, numrequests):
  tilenr = tileinfo['nummer']
  xmin = float(tileinfo['XMIN'])
  xmax = float(tileinfo['XMAX'])
  ymin = float(tileinfo['YMIN'])
  ymax = float(tileinfo['YMAX'])
  
  logging.debug("Processing tile " + tilenr + " (Liegenschaften)")
  basefilename = "bpav" + str(settings.scale) + settings.colortype + "_" + tilenr
  tileprocessing_starttime = datetime.datetime.now()

  try:
    ## In GeoTIFF konvertieren, komprimieren und Auflösungsangabe (PPI) korrigieren
    logging.debug("Convert file to GeoTIFF:")
    cmd = "gdal_translate -q -a_nodata 0 -a_srs EPSG:21781 -mo TIFFTAG_XRESOLUTION=508 -mo TIFFTAG_YRESOLUTION=508 -of GTiff -co 'TILED=YES' "
    if settings.colortype == "f":
      cmd += "-co 'COMPRESS=LZW' "
    else:
      cmd += "-co 'COMPRESS=CCITTFAX4' -co 'NBITS=1' "
    cmd += os.path.join(settings.outdir, basefilename + "_1_liegenschaften.png") + " " + os.path.join(settings.outdir, basefilename + "_liegenschaften.tif")
    logging.log(logging.DEBUG, cmd)
    imageprocessing_starttime = datetime.datetime.now()
    if not settings.simulate:
      os.system(cmd)
    imageprocessing_duration = datetime.datetime.now() - imageprocessing_starttime
    logging.log(logging.DEBUG, "Duration (converting to GeoTIFF): " + str(imageprocessing_duration.seconds) + " sec")
    
    ## Overviews hinzufügen
    if settings.colortype == "sw":
      logging.debug("Add overviews:")
      cmd = "gdaladdo -q -r nearest " + os.path.join(settings.outdir, basefilename + "_liegenschaften.tif") + " 2 4 8 16 32"
      logging.log(logging.DEBUG, cmd)
      imageprocessing_starttime = datetime.datetime.now()
      if not settings.simulate:
        os.system(cmd)
      imageprocessing_duration = datetime.datetime.now() - imageprocessing_starttime
      logging.log(logging.DEBUG, "Duration (adding overviews): " + str(imageprocessing_duration.seconds) + " sec")
  except:
    logging.exception("Processing of tile " + tilenr + " (Liegenschaften) failed.")
    # try to remove the resulting tif
    deleteFile(os.path.join(settings.outdir, basefilename + "_liegenschaften.tif"))
  else:
    # remove the processed png and pngw files
    if not settings.simulate and not settings.keep_tempfiles:
      deleteFile(os.path.join(settings.outdir, basefilename + "_1_liegenschaften.png"))
      deleteFile(os.path.join(settings.outdir, basefilename + "_1_liegenschaften.pngw"))
    # create a vrt file referencing all the finished tif files
    logging.debug("Create vrt file:")
    cmd = "gdalbuildvrt -q " + os.path.join(settings.outdir, "bpav" + str(settings.scale) + settings.colortype + "_liegenschaften.vrt") + " " + os.path.join(settings.outdir, "bpav" + str(settings.scale) + settings.colortype + "_*_liegenschaften.tif")
    logging.debug(cmd)
    if not settings.simulate:
      os.system(cmd)
 
  # Log the processing duration for this tile
  tileprocessing_duration = datetime.datetime.now() - tileprocessing_starttime
  logging.info("Duration for processing tile " + tilenr + " (Liegenschaften): " + str(tileprocessing_duration) + " sec")
  
  
  
  

def main():
  # read the options and arguments from the command line
  my_settings = parse_options()
  
  # check if outdir (needed for creating the logfile) exists
  checkDir = my_settings.outdir
  if not os.path.isdir(checkDir):
    errorMessage = "Error: " + checkDir + " does not exist"
    sys.exit(errorMessage)

  
  # configure logging
  FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
  logging.basicConfig(filename = my_settings.get_logfile_path(), filemode = "w", format = FORMAT, level = logging.DEBUG)
  
  # log some general information
  logging.log(logging.INFO, "Creating bpav" + str(my_settings.scale) + my_settings.colortype + " at " + str(my_settings.dpi) + " dpi")
  print "Creating bpav" + str(my_settings.scale) + my_settings.colortype + " at " + str(my_settings.dpi) + " dpi"
  logging.log(logging.INFO, "Settings: " + str(my_settings.__dict__))
  logging.log(logging.INFO, "More settings information: WMS URL: " + my_settings.get_wms_url())
  logging.log(logging.INFO, "More settings information: Cutline parameter: " + my_settings.get_clip_cutline())
  logging.log(logging.INFO, "More settings information: Cutline SQL parameter: " + my_settings.get_clip_cutlinesql())
  logging.log(logging.INFO, "Using tileindex " + my_settings.tileindex)
  logging.log(logging.INFO, "The Situation tiles are requested as " + str(my_settings.numrequests) + " partial tiles.")
  logging.log(logging.INFO, "Label layers x direction overlap: " + str(my_settings.overlapx) + ". Label layers y direction overlap: " + str(my_settings.overlapy))
  logging.log(logging.INFO, "WMS URL: " + my_settings.get_wms_url())
  logging.log(logging.INFO, "Creation of the files takes place under " + my_settings.outdir)
  if my_settings.targetdir == "":
    logging.log(logging.INFO, "No target directory selected. The tiles will remain in outdir: " + my_settings.outdir)
  else:
    logging.log(logging.INFO, "The target directory is " + my_settings.targetdir)
  starttime = datetime.datetime.now()
  logging.log(logging.INFO, "Start time is " + str(starttime))
  
  # check if numrequests is valid and reasonable
  if my_settings.numrequests < 1:
    errorMessage = "Error: Number of requests must be at least 1"
    logging.error(errorMessage)
    sys.exit(errorMessage)
  if my_settings.numrequests > 30:
    errorMessage = "Error: As a precaution the number of requests cannot be higher than 30"
    logging.error(errorMessage)
    sys.exit(errorMessage)
  
  # check if targetdir exists
  checkDir = my_settings.targetdir
  if my_settings.copy_to_targetdir and not os.path.isdir(checkDir):
    errorMessage = "Error: " + checkDir + " does not exist"
    logging.error(errorMessage)
    sys.exit(errorMessage)

  
  wms_duration = starttime - starttime
  # string containing the paths to the files that could definitely not be downloaded
  downloads_failed_definitely = ""
  
  if my_settings.no_download == False:
    # request all the map tiles from the WMS
    logging.info("Requesting the map tiles from the WMS")
    print "- Step 1/2: Requesting the map tiles from the WMS..."
    failed_downloads = {}
    try:
      with open(my_settings.tileindex, "r") as csvfile:
        csvreader = csv.DictReader(csvfile)
        logging.log(logging.DEBUG, my_settings.tileindex + " opened")
        for row in csvreader:
          if my_settings.restrict_tile == "" or my_settings.restrict_tile == row['nummer']:
            if my_settings.mode == "s" or my_settings.mode == "b":
              ## Die Situation anfordern
              failed_dl = getImages(my_settings, row, my_settings.numrequests, 0.0, 0.0, False, my_settings.get_layers_situ(), "_situation")
              failed_downloads.update(failed_dl)
              ## Die Beschriftungen anfordern (direkt als 1 Kachel, nicht in mehreren Teilen)
              failed_dl = getImages(my_settings, row, 1, my_settings.overlapx, my_settings.overlapy, my_settings.colortype == "f", my_settings.get_layers_beschr(), "_beschriftungen") ## Nur bei der farbigen Version transparent anfordern. Bei der schwarz-weissen wird die Transparenz (vorläufig) im Postprocessing hergestellt.
              failed_downloads.update(failed_dl)
              ## Für den schwarz-weissen BP-AV die Beschriftungen erneut anfordern, jedoch mit schwarzem Hintergrund für die Verwendung der Halos (direkt als 1 Kachel, nicht in mehreren Teilen)
              if my_settings.colortype == "sw":
                failed_dl = getImages(my_settings, row, 1, my_settings.overlapx, my_settings.overlapy, False, my_settings.get_layers_beschr_halo(), "_beschriftungenhalo")
                failed_downloads.update(failed_dl)
            if my_settings.mode == "l" or my_settings.mode == "b":
              ## Die Liegenschaften anfordern
              if my_settings.scale == 10000:
                logging.info("Es werden keine Liegenschaften angefordert, weil der Basisplan im Massstab 1:10000 keine Liegenschaften umfasst.")
              else:
                failed_dl = getImages(my_settings, row, 1, 0.0, 0.0, my_settings.colortype == "f", my_settings.get_layers_liegen(), "_liegenschaften") ## Nur bei der farbigen Version transparent anfordern. Bei der schwarz-weissen wird die Transparenz (vorläufig) im Postprocessing hergestellt.
                failed_downloads.update(failed_dl)
    except IOError:
      message = "Error reading tile index file " + my_settings.tileindex
      logging.exception(message)
      sys.exit(message)
    
    ## Retry the failed downloads
    if len(failed_downloads) > 0:
      sleep_duration_sec = 300
      logging.info("Some downloads failed. Going to retry after " + str(sleep_duration_sec) + " sec...")
      time.sleep(sleep_duration_sec)
      failed_def = getFailedImages(my_settings, failed_downloads)
      downloads_failed_definitely = str(failed_def.values())
    
    wms_duration = datetime.datetime.now() - starttime
    logging.log(logging.INFO, "The WMS requests are completed now. Duration: " + str(wms_duration))
    
    # log the size of outdir
    logDirectorySize(my_settings.outdir)
  else:
    logging.info("Not downloading anything from the WMS")
  
  
  ## Nochmals das CSV durchlaufen und dabei GeoTIFFs erzeugen und dabei die PNGs usw. löschen
  logging.info("Post processing the map tiles")
  print "- Step 2/2: Post processing the map tiles..."
  try:
    with open(my_settings.tileindex, "r") as csvfile:
      csvreader = csv.DictReader(csvfile)
      logging.log(logging.DEBUG, my_settings.tileindex + " opened again")
      for row in csvreader:
        if my_settings.restrict_tile == "" or my_settings.restrict_tile == row['nummer']:
          if my_settings.colortype == "sw":
            if my_settings.mode == "s" or my_settings.mode == "b":
              postprocessSituationSw(my_settings, row, my_settings.numrequests)
            if (my_settings.mode == "l" or my_settings.mode == "b") and my_settings.scale != 10000:
              postprocessLiegenschaftenSw(my_settings, row, 1)
          else:
            if my_settings.mode == "s" or my_settings.mode == "b":
              postprocessSituationF(my_settings, row, my_settings.numrequests)
            if (my_settings.mode == "l" or my_settings.mode == "b") and my_settings.scale != 10000:
              postprocessLiegenschaftenF(my_settings, row, 1)
  except IOError:
    message = "Error reading " + my_settings.tileindex
    logging.exception(message)
    sys.exit(message)
  
  postprocessing_duration = datetime.datetime.now() - starttime - wms_duration
  logging.log(logging.INFO, "The images have been post processed. Duration: " + str(postprocessing_duration))
  bpavcreation_duration = datetime.datetime.now() - starttime
  logging.log(logging.INFO, "The BP-AV has been created. Duration: " + str(bpavcreation_duration))
  
  if my_settings.copy_to_targetdir:
    logging.info("Moving the files from " + my_settings.outdir + " to " + my_settings.targetdir)
    print "- moving the files to the target directory..."
    moving_starttime = datetime.datetime.now()
    # delete existing .aux.xml files in targetdir
    auxFiles = os.listdir(my_settings.targetdir)
    for auxFile in auxFiles:
      if auxFile.endswith(".aux.xml"):
        try:
          os.remove(os.path.join(target, auxFile))
        except:
          logging.exception(auxFile + " could not be deleted")
        else:
          logging.info(auxFile + " deleted")
    
    # move files to targetdir
    bpavFiles = os.listdir(my_settings.outdir)
    for bpavFile in bpavFiles:
      if bpavFile.endswith(".tif") or bpavFile == "bpav" + my_settings.scale + my_settings.colortype + ".vrt"  or bpavFile == "bpav" + my_settings.scale + my_settings.colortype + "_liegenschaften.vrt":
        try:
          shutil.copy(os.path.join(my_settings.outdir, bpavFile), my_settings.targetdir)
        except:
          logging.exception(bpavFile + " could not be moved to " + my_settings.targetdir)
        else:
          logging.debug(bpavFile + " copied to " + my_settings.targetdir)
          try:
            os.remove(os.path.join(my_settings.outdir, bpavFile))
          except:
            logging.exception(bpavFile + " could not be deleted")
          else:
            logging.debug(bpavFile + " deleted")
    moving_duration = datetime.datetime.now() - moving_starttime
    logging.info("Duration for moving the files from " + my_settings.outdir + " to " + my_settings.targetdir + ": " + str(moving_duration))
  

  if len(downloads_failed_definitely) > 2: # downloads_failed_definitely = "[]" if no downloads failed
    print "Task completed with errors."
    logging.error("Task completed with errors.")

  overall_duration = datetime.datetime.now() - starttime
  print "Task complete. Overall duration: ",  str(overall_duration)
  logging.log(logging.INFO, "Task complete. Overall duration: " + str(overall_duration))
  logging.shutdown()
  
  ## Logfile nach targetdir kopieren
  try:
    if my_settings.copy_to_targetdir:
      shutil.copy(my_settings.get_logfile_path(), my_settings.targetdir)
  except:
    print "(", my_settings.get_logfile_path(), " could not be copied to ", my_settings.targetdir, ")"

if __name__ == "__main__":
  main()
