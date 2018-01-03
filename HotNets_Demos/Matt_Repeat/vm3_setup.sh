#!/bin/bash

sudo yum update -y
sudo yum install -y git squid httpd-tools
git clone https://github.com/slab14/Gateway_Testbed.git

sudo touch /etc/squid/passwd && sudo chown squid /etc/squid/passwd
sudo htpasswd /etc/squid/passwd tommy

sudo cp $HOME/Gateway_Testbed/HotNets_Demos/Matt_Repeat/psi_squid.conf.2 /etc/squid/squid.conf
sudo systemctl restart squid

