#!/bin/bash

sudo virsh destroy $1
sudo virsh destroy $2
sudo virsh destroy $3
sudo virsh undefine $1
sudo virsh undefine $2
sudo virsh undefine $3
sudo rm -rf $HOME/virt/images/$1 $HOME/virt/images/$2 $HOME/virt/images/$3
