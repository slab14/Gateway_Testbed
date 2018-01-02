#!/bin/bash

sudo yum update -y
sudo yum install -y git squid httpd-tools
git clone https://github.com/slab14/Gateway_Testbed.git

touch /etc/squid/passwd && chown squid /etc/squid/passwd
htpasswd /etc/squid/passwd tommy

cp $HOME/Gateway_Testbed/HotNets_Demos/Matt_Repeat/psi_squid.conf.1 /etc/squid/squid.conf
sudo systemctl restart squid

