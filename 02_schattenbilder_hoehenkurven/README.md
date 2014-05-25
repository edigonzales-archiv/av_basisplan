Schattenbilder & Höhenkurven aus DTM-AV 2m-Grid
===============================================

Mit zwei Python-Skripts werden sowohl die Schattenbilder (das Relief) wie auch die Höhenkurven aus dem DTM-AV 2m-Grid gerechnet. Neu ist es auch effizient möglich aus den DTM-Rohdaten die Produkte zu erzeugen. `gdal_grid`

* Daten: DTM-AV. Besser bereits 2m Grid ansonsten dauert der GeoTIFF Prozess länger.
* Kopieren der *.gz Dateien in ein tmp-working-Directory. 
* Anschliessend werden die Files durchgenudelt.
* dtm_xyz.vrt muss im Skriptverzeichnis sein und es wird dann kopiert. schöner wenn es selber erzeugt würde. ist ja nicht viel
* dito für ramp.txt

* skript muss im verzeichnis ausgeführt werden wo dtm_xyz.vrt und ramp.txt sind.
* achtung: u.U. Heissen dann die DTM-Rohdaten nicht genau gleich!?
