#!/bin/bash
set -x

# This script is used to deploy ACC2 on Metacentrum server.
# Assumes Ubuntu 22.04

ACC2_DEPENDENCIES="
  apache2
  dos2unix
  libapache2-mod-wsgi-py3
  python3-flask
  python3-magic
  python3-gemmi
"
CHARGEFW2_DEPENDENCIES="
  cmake
  g++
  gemmi-dev
  git
  libnanoflann-dev
  libboost-filesystem-dev
  libboost-program-options-dev
  libboost-system-dev
  libeigen3-dev
  libfmt-dev
  libstb-dev
  nlohmann-json3-dev
  python3-dev
  pybind11-dev
  tao-pegtl-dev
"

# upgrade packages and install dependencies
sudo apt update && sudo apt -y upgrade
sudo apt install -y ${ACC2_DEPENDENCIES} ${CHARGEFW2_DEPENDENCIES}

# create directories
sudo mkdir -p /home/charge/{chargefw2,logs,www/ACC2,.ssh}

# Setup user charge
sudo useradd charge
sudo chmod 700 /home/charge/.ssh
sudo cp ~/.ssh/authorized_keys /home/charge/.ssh/authorized_keys

# Configure apache for ACC2 
sudo sha256sum /etc/passwd > /etc/ACC2.conf
sudo cp 000-ACC2.conf /etc/apache2/sites-available/000-ACC2.conf

sudo a2dissite 000-default
sudo a2ensite 000-ACC2

# install external dependencies
bash update_chargefw2.sh
bash update_acc2.sh

# Setup scripts for easy update
sudo cp update_chargefw2.sh /usr/local/bin/update_chargefw2
sudo cp update_acc2.sh /usr/local/bin/update_acc2
sudo chmod +x /usr/local/bin/{update_chargefw2,update_acc2}

# Fix permissions
sudo chown -R charge:charge /home/charge

# Clean up
sudo apt-get -y autoremove
sudo apt-get -y clean

# Reload apache to run ACC2
sudo service apache2 reload
