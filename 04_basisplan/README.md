Basisplan
=========

Zusätzliche Views
-----------------
Für die Darstellung in QGIS werden einige zusätzliche Views verwendet, die im Schema *av_basisplan* erzeugt werden.

Koordinatenkreuze
-----------------
Die Koordinatenkreuze wurden einmalig (mit QGIS) erzeugt und liegen jetzt als Shapedatei vor und werden mit dem Skript `import_koordinatenkreuze.sh` importiert. Verwendet wird `shp2pgsql` und es wird immer die ganze Schweiz importiert (ev. vorgängig clippen mit ogr2ogr).

Felsschraffuren
---------------
Die Felsschraffuren werden von der V+D zur Verfügung gestellt. Mit folgendem Befehl wird ein VRT erstellt:

```
gdalbuildvrt -a_srs epsg:21781  felsschraffuren.vrt *.tif
```

Overviews werden keine erstellt (-> Performanz im Auge behalten).

QGIS
----
### Fonts
Der *Cadastra*-Font muss installiert sein. Unter Ubuntu wie folgt installieren:

```
cd /usr/share/fonts/truetype
cp /path/to/fonts/*.ttf .
sudo fc-cache -f -v
```

### Symbole
Originale sind auf [GitHub](https://github.com/edigonzales/qgis_svg) zu finden.

Wie folgt installieren:

```
cd /usr/local/qgis/qgis_enterprise/share/qgis/svg/
sudo cp -r /path/to/grundbuchplan-dir/ .
```

Im QGIS svg-Ordner mit den vielen SVG-Unterordner sollte jetzt ein *grundbuchplan*-Unterordner sein.

### Masken
Es sind pro Kanton drei Polygone notwendig:

* Hintergrundfläche
* Kantonsfläche
* Maske (Hintergrundfläche minus Kantonsfläche)

Zur Zeit werden diese drei Polygone manuell erzeugt und müssen mit dem Skript `import_masks.sh` importiert werden. 

### QGS
Pro Kanton werden die QGIS-Projekte erstellt. So wird das Zuschneiden/Maskieren (falls das überhaupt gewünscht wird einfacher). Benennung der Dateien:

* bpav_10000f_sz.qgs = Masstab 1:10'000 / farbig / Kanton Schwyz
* bpav_10000sw_sz.qgs = Masstab 1:10'000 / schwarz-weiss / Kanton Schwyz
* bpav_5000f_sz.qgs = Masstab 1:5'000 / farbig / Kanton Schwyz
* bpav_5000sw_sz.qgs = Masstab 1:5'000 / farbig / Kanton Schwyz

Im QGIS-Projekt muss nur der Datenbankname angepasst werden.
