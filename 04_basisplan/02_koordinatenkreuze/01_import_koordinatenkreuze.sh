#!/bin/bash

ADMIN="bpadmin"
ADMINPWD="bpadmin"
USER="mspublic"
USERPWD="mspublic"

DB_NAME="bpav_sz"

CROSS_SHP="../../00_data/koordinatenkreuze/koordinatenkreuze.shp"

shp2pgsql -s 21781 -I $CROSS_SHP av_basisplan.koordinatenkreuz | sudo -u postgres psql -d $DB_NAME
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON TABLE av_basisplan.koordinatenkreuz TO $ADMIN;"
sudo -u postgres psql -d $DB_NAME -c "GRANT SELECT ON TABLE av_basisplan.koordinatenkreuz TO $USER;"


