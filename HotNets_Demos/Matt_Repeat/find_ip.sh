#!/bin/bash

MAC=$(virsh dumpxml $1 | awk -F\' '/mac address/ {print $2}')

while true
do
    IP=$(grep -B1 $MAC /var/lib/libvirt/dnsmasq/virbr0.status | head -n 1 | awk '{print $2}' | sed -e s/\"//g -e s/,//)
    if [ "$IP" = "" ]
    then
	sleep 1
    else
	break
    fi
done

echo $IP
