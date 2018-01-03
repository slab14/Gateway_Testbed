#!/bin/bash

sudo yum update -y
sudo yum install -y git java xauth
git clone https://github.com/slab14/Gateway_Testbed.git
cd $HOME/Gateway_Testbed/HotNets_Demos
tar xvzf SteveyO-Hue-Emulator.tar.gz
