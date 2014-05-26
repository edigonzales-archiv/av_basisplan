#!/bin/bash

ADMIN="bpadmin"
ADMINPWD="bpadmin"
USER="mspublic"
USERPWD="mspublic"

DB_NAME="bpav_sz"
KANTON="sz"

MASK_SHP="../../../00_data/masken/kanton_$KANTON.shp"

shp2pgsql -s 21781 -I $MASK_SHP av_basisplan.maske_kanton | sudo -u postgres psql -d $DB_NAME
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON TABLE av_basisplan.maske_kanton TO $ADMIN;"
sudo -u postgres psql -d $DB_NAME -c "GRANT SELECT ON TABLE av_basisplan.maske_kanton TO $USER;"


