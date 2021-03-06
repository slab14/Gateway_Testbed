#!/bin/bash

DAQ_VER='2.0.6'
# Snort 3 uses different version of DAQ, ver 2.2.2
#DAQ_VER='2.2.2' 

if [ $1 == 1 ]; then
    SNORT_VER='2.9.11.1'
fi

# Bash script to install Snort
sudo apt-get update && sudo apt-get clean
sudo apt-get install -yqq build-essential autotools-dev bison flex gcc \
     libdumbnet-dev liblzma-dev libpcap-dev libpcre3-dev libssl-dev \
     libluajit-5.1-dev pkg-config make openssl wget zlib1g-dev libwloc-dev \
     cmake libtool autoconf libnetfilter-queue-dev libnghttp2-dev

#Optional 
sudo apt-get install -yqq cpputest libsqlite3-dev uuid-dev

# For documentation
sudo apt-get install -yqq asciidoc dblatex source-highlight w3m

sudo apt-get clean

mkdir ~/snort_src
cd ~/snort_src

#safec
wget https://downloads.sourceforge.net/project/safeclib/libsafec-10052013.tar.gz
tar -xzvf libsafec-10052013.tar.gz
cd libsafec-10052013
./configure && make && sudo make install
cd ..

#Ragel
cd ~/snort_src
wget http://www.colm.net/files/ragel/ragel-6.10.tar.gz
tar -xzvf ragel-6.10.tar.gz
cd ragel-6.10
./configure && make && sudo make install
cd ..

#Boost C++ Libraries
 cd ~/snort_src
wget https://dl.bintray.com/boostorg/release/1.65.1/source/boost_1_65_1.tar.gz
tar -xvzf boost_1_65_1.tar.gz
cd ..

#Hyperscan
cd ~/snort_src
wget https://github.com/intel/hyperscan/archive/v4.6.0.tar.gz
tar -xvzf v4.6.0.tar.gz
mkdir ~/snort_src/hyperscan-4.6.0-build
cd hyperscan-4.6.0-build/
cmake -DCMAKE_INSTALL_PREFIX=/usr/local -DBOOST_ROOT=~/snort_src/boost_1_65_1/ ../hyperscan-4.6.0
make && sudo make install
cd ../..

#flatbuffers
cd ~/snort_src
wget https://github.com/google/flatbuffers/archive/master.tar.gz -O flatbuffers-master.tar.gz
tar -xvzf flatbuffers-master.tar.gz
mkdir flatbuffers-build
cd flatbuffers-build
cmake ../flatbuffers-master
make && sudo make install
cd ../..

# DAQ
wget https://www.snort.org/downloads/snort/daq-${DAQ_VER}.tar.gz
tar xvfz daq-${DAQ_VER}.tar.gz
cd daq-${DAQ_VER}
./configure && make && sudo make install
cd ..

# Update shared libraries
sudo ldconfig

# Snort
if [ $1 == 1 ]; then
    cd ~/snort_src
    wget https://www.snort.org/downloads/snort/snort-${SNORT_VER}.tar.gz
    tar xvzf snort-${SNORT_VER}.tar.gz
    cd snort-${SNORT_VER}
    ./configure --enable-sourcefire && make && sudo make install
    cd ../..
elif [$1 == 3 ]; then
    cd ~/snort_src
    git clone git://github.com/snortadmin/snort3.git
    cd snort3
    ./configure_cmake.sh --prefix=/opt/snort
    cd build
    make && sudo make install
    cd ../../..
fi

sudo ln -s /opt/snort/bin/snort /usr/sbin/snort

sudo mkdir /etc/snort
sudo mkdir /etc/snort/rules
sudo mkdir /var/log/snort
