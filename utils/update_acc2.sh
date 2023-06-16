#!/bin/bash

set -x

cd ${HOME} || exit 1
sudo rm -rf ACC2 /home/charge/www/ACC2/*
git clone https://github.com/sb-ncbr/AtomicChargeCalculator2.git ACC2
sudo cp -r ACC2/app/* /home/charge/www/ACC2
sudo chown -R charge:charge /home/charge
sudo touch /home/charge/www/ACC2/ACC2.wsgi
