#!/bin/bash

IP=$1
if [ -z $IP ]; then
    $IP=10.1.1.2
fi

httping -i 0.00001 -G -c 10000 $IP:8000 
