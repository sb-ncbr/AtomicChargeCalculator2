#!/bin/bash
set -x

# Assumes Ubuntu 22.04

# Upgrade packages to latest versions
sudo apt-get update
sudo apt-get -y upgrade

# Setup user charge
sudo useradd charge
sudo mkdir /home/charge

sudo mkdir /home/charge/.ssh
sudo chmod 700 /home/charge/.ssh
sudo cp ~/.ssh/authorized_keys /home/charge/.ssh/authorized_keys

sudo mkdir /home/charge/chargefw2
sudo mkdir /home/charge/logs
sudo mkdir -p /home/charge/www/ACC2

# Install necessary packages for ACC2
sudo apt-get install -y apache2 libapache2-mod-wsgi-py3
sudo apt-get install -y python3-magic python3-flask dos2unix openbabel

# Configure apache for ACC2 
sudo sh -c 'sha256sum /etc/passwd > /etc/ACC2.conf'

sudo sh -c 'cat << EOF > /etc/apache2/sites-available/000-ACC2.conf
<VirtualHost *:80>
        ServerName $(hostname).cerit-sc.cz
        WSGIDaemonProcess ACC2 user=charge group=charge home=/home/charge/www/
        WSGIScriptAlias / /home/charge/www/ACC2/ACC2.wsgi
        WSGIScriptReloading On
        CustomLog /home/charge/logs/access_log common
        ErrorLog /home/charge/logs/error_log
        <Directory /home/charge/www/ACC2>
                WSGIProcessGroup ACC2
                WSGIApplicationGroup %{GLOBAL}
                Require all granted
        </Directory>
</VirtualHost>
EOF'

sudo a2dissite 000-default
sudo a2ensite 000-ACC2

# Install packages needed for building ChargeFW2
sudo apt-get install -y git g++ cmake libnanoflann-dev gemmi-dev tao-pegtl-dev
sudo apt-get install -y nlohmann-json3-dev libfmt-dev libeigen3-dev python3-dev
sudo apt-get install -y libboost-filesystem-dev libboost-system-dev libboost-program-options-dev pybind11-dev

# Set number of processes for make
nproc=$(($(grep -c processor /proc/cpuinfo) + 1))

# Install latest version of ChargeFW2
cd || exit 1
git clone https://github.com/krab1k/ChargeFW2.git ChargeFW2
cd ChargeFW2 || exit 1
mkdir build && cd build || exit 1
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/home/charge/chargefw2 ..
make -j${nproc}
sudo make install

# Install ACC2
cd || exit 1
git clone https://github.com/krab1k/AtomicChargeCalculator2.git ACC2
sudo cp -r ACC2/app/* /home/charge/www/ACC2

# Install LiteMol component
sudo mkdir /home/charge/www/ACC2/static/litemol
wget http://yavanna.ncbr.muni.cz:9877/share/litemol.tar.gz
sudo tar xvzf litemol.tar.gz -C /home/charge/www/ACC2/static/litemol

# Setup scripts for easy update
sudo sh -c 'cat << EOF > /usr/local/bin/update_chargefw2
#!/bin/bash
set -x
nproc=\$((\$(grep -c processor /proc/cpuinfo) + 1))
cd ~/ChargeFW2
sudo rm -rf build
git pull
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/home/charge/chargefw2 ..
make -j\${nproc}
sudo make install
if [ "\$?" -eq 0 ]; then
  sudo chown -R charge:charge /home/charge
  sudo touch /home/charge/www/ACC2/ACC2.wsgi
else
  echo Failed to update ChargeFW2
  exit 1
fi
EOF'

sudo sh -c 'cat << EOF > /usr/local/bin/update_acc2
#!/bin/bash
set -x
cd ~/ACC2
git pull
sudo rm -rf /home/charge/www/ACC2/*
sudo cp -r app/* /home/charge/www/ACC2
sudo mkdir /home/charge/www/ACC2/static/litemol
wget http://yavanna.ncbr.muni.cz:9877/share/litemol.tar.gz -O /tmp/litemol.tar.gz
sudo tar xvzf /tmp/litemol.tar.gz -C /home/charge/www/ACC2/static/litemol
sudo chown -R charge:charge /home/charge
sudo touch /home/charge/www/ACC2/ACC2.wsgi
EOF'

sudo chmod +x /usr/local/bin/update_chargefw2 /usr/local/bin/update_acc2

# Fix permissions
sudo chown -R charge:charge /home/charge

# Clean up
sudo apt-get -y autoremove
sudo apt-get -y clean

# Reload apache to run ACC2
sudo service apache2 reload
