Import Amtliche Vermessung
==========================

**Voraussetzung:** Die Daten müssen im Datenmodell **DM01AVSO24D** vorliegen.

Die Daten der amtlichen Vermessung werden mit `itf2avdpoolng_catais` importiert. Da die Namensgebung wahrscheinlich von unserer abweicht, wird eine neue *Import_data*-Klasse erstellt (und eine neue "Start"-Klasse, die im properties-File gesetzt werden kann). 

Annahme: Die ITF heissen *lisag_XXXX_lY.itf*, wobei XXXX die BfS-Nummer und Y die Losnummer ist. Dies entspricht der Namensgebung aus dem AV-Geoportal.

Das Schema und die Tabellen werden mit dem SQL-Skript `01_create_schema_tables.sql` erzeugt. Das Skript `02_zusaetzliche_index.sql` generiert einige weitere Indizes, die nicht direkt aus dem Datenmodell abgeleitet werden können.


