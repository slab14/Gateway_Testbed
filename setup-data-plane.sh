#!/bin/bash

#borrowed form Jeff Helt

BRIDGE_NAME=br0
CLIENT_SIDE_IP=192.1.1.1
SERVER_SIDE_IP=10.1.1.1

update() {
    echo "Updating apt-get..."
    sudo apt-get -qq update
    echo "Update complete"
}

install_docker() {
    echo "Installing Docker..."
    sudo apt-get -yqq install docker-compose 

    sudo apt-get -yqq install apt-transport-https ca-certificates \
	 curl software-properties-common

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
	| sudo apt-key add -

    loc="deb [arch=amd64] https://download.docker.com/linux/ubuntu "
    loc+="$(lsb_release -cs) stable"
    sudo add-apt-repository $loc

    sudo apt-get -qq update
    sudo apt-get -yqq install docker-ce

    sudo systemctl start docker
    sudo systemctl enable docker
    echo "Docker Install Complete"
}

install_python_packages() {
    echo "Installing Python..."
    sudo apt-get -yqq install python python-ipaddress python-subprocess32 \
	 python-pip
    echo "Python Install Complete"
}

install_ovs() {
    echo "Installing OVS..."
    sudo apt-get -yqq install openvswitch-common openvswitch-switch \
	 openvswitch-dbg
    sudo systemctl start openvswitch-switch
    sudo systemctl enable openvswitch-switch
    echo "OVS Install Complete"

}

find_interface_for_ip() {
  local ip="$1"

  local interface=$(ip -o addr | grep "inet $ip" | awk -F ' ' '{ print $2 }')
  if [[ -z $interface ]]; then
    return 1
  else
    echo $interface
    return 0
  fi
}

setup_bridge() {
    echo "Setting up basic Bridge..."
    sudo ovs-vsctl --may-exist add-br $BRIDGE_NAME
    sudo ip link set $BRIDGE_NAME up

    local client_side_if=$(find_interface_for_ip $CLIENT_SIDE_IP)
    local server_side_if=$(find_interface_for_ip $SERVER_SIDE_IP)
    
    sudo ovs-vsctl --may-exist add-port $BRIDGE_NAME $client_side_if \
	 -- set Interface $client_side_if ofport_request=1
    sudo ovs-ofctl mod-port $BRIDGE_NAME $client_side_if up

    sudo ovs-vsctl --may-exist add-port $BRIDGE_NAME $server_side_if \
	 -- set Interface $server_side_if ofport_request=2
    sudo ovs-ofctl mod-port $BRIDGE_NAME $server_side_if up
    echo "Bridge Setup Complete"
}

# Install packages
echo "Beginning Dataplane Setup..."
update
install_docker
install_ovs
install_python_packages

# Setup
setup_bridge
echo "Dataplane Ready"
