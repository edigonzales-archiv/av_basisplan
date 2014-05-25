#!/bin/bash

ADMIN="bpadmin"
ADMINPWD="bpadmin"
USER="mspublic"
USERPWD="mspublic"

DB_NAME="bpav_sz"

CONTOUR_SHP="/home/stefan/tmp/bpav_sz/dtm_roh/contour.shp"

#sudo -u postgres psql -d $DB_NAME -c "CREATE SCHEMA av_dtm_dom AUTHORIZATION $ADMIN;"
#sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA av_dtm_dom TO $ADMIN;"
#sudo -u postgres psql -d $DB_NAME -c "GRANT USAGE ON SCHEMA av_dtm_dom TO $USER;"

shp2pgsql -s 21781 -I $CONTOUR_SHP av_dtm_dom.contour_10m | sudo -u postgres psql -d $DB_NAME
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON TABLE av_dtm_dom.contour_10m TO $ADMIN;"
sudo -u postgres psql -d $DB_NAME -c "GRANT SELECT ON TABLE av_dtm_dom.contour_10m TO $USER;"


