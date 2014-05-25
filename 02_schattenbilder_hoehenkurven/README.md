Schattenbilder & Höhenkurven aus DTM-AV 2m-Grid
===============================================

Mit zwei Python-Skripts werden sowohl die Schattenbilder (das Relief) wie auch die Höhenkurven aus dem DTM-AV 2m-Grid gerechnet. Neu ist es auch effizient möglich aus den DTM-Rohdaten die Produkte zu erzeugen. `gdal_grid` ist sehr langsam wenn **nicht** *nearest* als Interpolationsalgorithmus verwendet wird und/oder wenn der Suchradius sehr gross wird. Neu wird jetzt auf für Rohdaten *nearest* verwendet. Die *nodata*-Rasterzellen werden anschliessend mit `gdal_fillnodata.py` gefüllt.

Es werden Shapes mit den Kantonsgrenzen und der Tileindex des DTM/DOM verwendet. Der Pfad ist in den Skripten hardcodiert. 

xyz2tif.py
----------
Erstellt aus einem DTM (swisstopo-Format) eine DTM und Schattenbilder (grau und gelblich für Basisplan) jeweils im GeoTIFF-Format. In ein schreibbares Verzeichnis (=Arbeitsverzeichnis) werden die *.xyz.gz-Datei manuell kopiert. In diesem Arbeitsverzeichnis werden automatisch beim Ausführen des Skriptes weitere Verzeichnisse erstellt, in denen die Resultate gespeichert werden. 

Im gleichen Verzeichnis in dem das Skript liegt, muss es auch ausgeführt werden, da zwei Dateien benötigt werden (ramp.txt und dtm_xzy.vrt). Die beiden Dateien werden jeweils verändert und in das Arbeitsverzeichnis kopiert.

Eventuell muss der Basisnamen für die DTM angepasst werden. Bedingung ist aber, dass alle Kacheln das gleiche Namensschema verwenden.


tif2contour.py
--------------
Bedingung ist das Vorhandensein der DTM-Kacheln (siehe `xyz2tif.py`). Es werden kachelweise (mit 50 Meter Buffer um schöne Übergänge zu erhalten) die Höhenkurven gerechnet und anschliessend mit der Kachel und der Kantonsgrenze geklippt. Kurze Höhenkurven (< 100 Meter) werden gelöscht.

Werden nur einzelne Kacheln eines Kantons gerechnet, sind hässliche Artefakte am Rand nicht zu vermeiden.


Datenimport
-----------
Die Höhenkurven werden in das Schema `av_dtm_dom` mit dem Skript `create_dtm_schema_and_import.sh` importiert. Für das Relief muss mit `gdal_buildvrt` ein VRT erstellt werden.

