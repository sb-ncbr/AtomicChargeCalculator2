#!/bin/bash

set -x

# Set number of processes for make
nproc=$(($(grep -c processor /proc/cpuinfo) + 1))

cd ${HOME} || exit 1
sudo rm -rf ChargeFW2
git clone https://github.com/sb-ncbr/ChargeFW2.git ChargeFW2
cd ChargeFW2 || exit 1
mkdir build && cd build || exit 1
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/home/charge/chargefw2 ..
make -j${nproc}
sudo make install
if [ "$?" -eq 0 ]; then
  sudo chown -R charge:charge /home/charge
  sudo touch /home/charge/www/ACC2/ACC2.wsgi
else
  echo Failed to update ChargeFW2
  exit 1
fi
