#!/bin/bash
set -x

# Upgrade to Debian buster to have updated packages
sed -i 's/stretch/buster/g' /etc/apt/sources.list
apt-get update
echo 'force-confold' >> /etc/dpkg/dpkg.cfg.d/auto
echo 'force-confdef' >> /etc/dpkg/dpkg.cfg.d/auto
export DEBIAN_FRONTEND=noninteractive
apt-get -y dist-upgrade

# Setup user charge
useradd charge
mkdir /home/charge

mkdir /home/charge/.ssh
chmod 700 /home/charge/.ssh
cp ~/.ssh/authorized_keys /home/charge/.ssh/authorized_keys

mkdir /home/charge/chargefw2
mkdir /home/charge/logs
mkdir -p /home/charge/www/ACC2

# Install necessary packages for ACC2
apt-get install -y apache2 libapache2-mod-wsgi-py3
apt-get install -y python3-magic python3-flask dos2unix openbabel

# Configure apache for ACC2 
sha256sum /etc/passwd > /etc/ACC2.conf

cat << EOF > /etc/apache2/sites-available/000-ACC2.conf
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
EOF

a2dissite 000-default
a2ensite 000-ACC2

# Install packages needed for building ChargeFW2
apt-get install -y gcc g++ cmake make gdb libtool
apt-get install -y libmkl-dev
apt-get install -y nlohmann-json3-dev libfmt-dev libnlopt-cxx-dev libeigen3-dev
apt-get install -y libboost-filesystem1.67-dev libboost-system1.67-dev libboost-program-options1.67-dev

# Set number of processes for make
nproc=$(($(grep -c processor /proc/cpuinfo) + 1))

# Install nanoflann library from source
wget 'https://github.com/jlblancoc/nanoflann/archive/v1.3.0.tar.gz' -O nanoflann.tar.gz
tar xvzf nanoflann.tar.gz
cd nanoflann-1.3.0
mkdir build && cd build
cmake ..
make -j${nproc} && make install

# Install latest version of ChargeFW2
cd
apt-get install -y git
git clone https://github.com/krab1k/ChargeFW2.git ChargeFW2
cd ChargeFW2
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/home/charge/chargefw2 -DMETA_CLOUD=1 ..
make -j${nproc}
make install

# Install ACC2
cd
git clone https://github.com/krab1k/AtomicChargeCalculator2.git ACC2
cp -r ACC2/app/* /home/charge/www/ACC2

# Install LiteMol component
cd
mkdir /home/charge/www/ACC2/static/litemol
wget http://yavanna.ncbr.muni.cz:9877/share/litemol.tar.gz
tar xvzf litemol.tar.gz -C /home/charge/www/ACC2/static/litemol

# Setup scripts for easy update
cat << EOF > /usr/local/bin/update_chargefw2
#!/bin/bash
nproc=$(($(grep -c processor /proc/cpuinfo) + 1))
cd ~/ChargeFW2
rm -r build
git pull
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/home/charge/chargefw2 -DMETA_CLOUD=1 ..
make -j${nproc}
make install
chown -R charge:charge /home/charge
touch /home/charge/www/ACC2/ACC2.wsgi
EOF

cat << EOF > /usr/local/bin/update_acc2
#!/bin/bash
cd ~/ACC2
git pull
cp -r app/* /home/charge/www/ACC2
chown -R charge:charge /home/charge
touch /home/charge/www/ACC2/ACC2.wsgi
EOF

chmod +x /usr/local/bin/update_chargefw2 /usr/local/bin/update_acc2

# Fix permissions
chown -R charge:charge /home/charge

# Clean up
apt-get -y autoremove
apt-get -y clean

# Reload apache to run ACC2
service apache2 reload
