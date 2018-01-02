#!/bin/bash

sudo yum update
sudo yum install -y git java
git clone https://github.com/slab14/Gateway_Testbed.git
cd Gateway_Testbed/HotNets_Demos
tar xvzf SteveyO-Hue-Emulator.tar.gz
