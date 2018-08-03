#!/bin/bash

IP=$1
if [ -z $IP ]; then
    IP="10.1.1.2"
fi

sudo hping3 -i u50 -S $IP
