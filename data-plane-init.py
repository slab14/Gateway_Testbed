#!/bin/bash

BRIDGE_NAME=br0
NODE_0=192.1.1.1
NODE_1=10.1.1.1

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

    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

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

disable_gro() {
    local client_side_if=$(find_interface_for_ip $CLIENT_SIDE_IP)
    local server_side_if=$(find_interface_for_ip $SERVER_SIDE_IP)
    sudo ethtool -K $client_side_if gro off
    sudo ethtool -K $server_side_if gro off
}


setup_bridge() {
    echo "Setting up basic Bridge..."
    sudo ovs-vsctl --may-exist add-br $BRIDGE_NAME
    sudo ip link set $BRIDGE_NAME up

    local node_0_if=$(find_interface_for_ip $NODE_0)
    local node_1_if=$(find_interface_for_ip $NODE_1)
    
    sudo ovs-vsctl --may-exist add-port $BRIDGE_NAME $node_0_if \
	 -- set Interface $node_0_if ofport_request=1
    sudo ovs-ofctl mod-port $BRIDGE_NAME $node_0_if up

    sudo ovs-vsctl --may-exist add-port $BRIDGE_NAME $node_1_if \
	 -- set Interface $node_1_if ofport_request=2
    sudo ovs-ofctl mod-port $BRIDGE_NAME $node_1_if up
    echo "Bridge Setup Complete"
}

# Install packages
echo "Beginning Dataplane Setup..."
update
install_docker
install_ovs
install_python_packages

# Setup
disable_gro
setup_bridge
echo "Dataplane Ready"

