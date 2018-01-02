#!/bin/bash

virsh destroy $1 $2 $3
virsh undefine $1 $2 $3
rm -rf $HOME/virt/images/$1 $HOME/virt/images/$2 $HOME/virt/images/$3
