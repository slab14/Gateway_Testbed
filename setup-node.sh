#!/bin/bash

# Script to setup "node" for generating/sinking IP data traffic
## Asumes on a Ubuntu machine ##

#borrowed from Jeff Helt

update() {
    echo "Updating apt-get..."
    sudo apt-get -qq update
    echo "Update Complete"
}


install_iperf() {
    echo "Installing iperf..."
    sudo apt-get -qq install -y iperf3
    echo "iperf Install Complete"
}

install_python_packages() {
    echo "Installing Python..."
    sudo apt-get -qq install -y python python-dev python-pip
    sudo pip -qq install --upgrade pip
    sudo pip -qq install ipaddress subprocess32
    echo "Python Instll Complete"
}

setup_ip_routes() {
    sudo ip route add 10.1.0.0/16 dev enp6s0f0
    sudo ip route add 192.1.0.0/16 dev enp6s0f0
}

# Install packages
echo "Beginning Node Setup..."
update
install_iperf
install_python_packages
setup_ip_routes
echo "Node Setup Complete"
