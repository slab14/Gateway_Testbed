IP=$1

curl --connect-timeout 5 -s -X PUT http://$IP:8000/api/newdeveloper/groups/0/action -d {\"on\":false}
