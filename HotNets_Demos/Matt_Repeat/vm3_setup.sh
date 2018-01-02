#!/bin/bash

sudo yum update
sudo yum install -y git squid
git clone https://github.com/slab14/Gateway_Testbed.git
cd Gateway_Testbed/HotNets_Demos/Matt_Repeat

cp psi_squid.conf.1 /etc/squid/squid.conf
sudo systemctl restart squid

