#!/bin/bash

MAC=$(virsh dumpxml $1 | awk -F\' '/mac address/ {print $2}')
IP=$(grep -B1 $MAC /var/lib/libvirt/dnsmasq/virbr0.status | head -n 1 | awk '{print $2}' | sed -e s/\"//g -e s/,//)

echo $IP
