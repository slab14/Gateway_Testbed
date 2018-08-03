#!/bin/bash

IP=$1

sudo hping3 -i u50 -S $IP
