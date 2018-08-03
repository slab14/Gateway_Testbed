#!/bin/bash

IP=$1
if [ -z $IP ]; then
    IP="10.1.1.2"
fi

httping -i 0.1 -G -c 15000 $IP:8000 
