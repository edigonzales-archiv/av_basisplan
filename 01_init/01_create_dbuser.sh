#!/bin/bash

ADMIN="bpadmin"
ADMINPWD="bpadmin"
USER="mspublic"
USERPWD="mspublic"

echo "Create database user"
sudo -u postgres psql -d postgres -c "CREATE ROLE $ADMIN CREATEDB LOGIN PASSWORD '$ADMINPWD';"
#sudo -u postgres psql -d postgres -c "CREATE ROLE $USER LOGIN PASSWORD '$USERPWD';"



