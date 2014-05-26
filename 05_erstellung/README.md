Erstellung Basisplan
====================

Das Skript `basisplan.py` steuert die Erstellung des Basisplanes. Beispielaufruf:

```
./basisplan.py -p 3 -c sw -s 10000 --tile 1152-3 ./bpav10000_5.csv /home/stefan/tmp/bpav10000sw_sz/
```

Die CSV-Datei enthält die BBOX und die Kachelnummer und muss für jeden Kanton erstellt werden. Momentan gibts noch kein Skript dazu (wie habe ich das für SZ gemacht?). -> Doch im Ordner CSV gibts ein Groovy-Skript und für alle Kanton die CSV für die Massstäbe 1:5000 und 1:10000 -> Umschreiben nach Python.

```
basisplan.py -h
```

zeigt sämtliche Optionen.
