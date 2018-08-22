IP=$1
PROXY=$2

time curl --proxy http://$PROXY:13128 --proxy-digest --proxy-user tommy:iotsec --connect-timeout 5 -s -X PUT http://$IP:8000/api/newdeveloper/groups/0/action -d {\"on\":true}


#time curl -U tommy:iotsec --connect-timeout 5 -s -X PUT http://$IP:8000/api/newdeveloper/groups/0/action -d {\"on\":true}
