IP=$1
NUM=$2

for i in (1..$NUM);
do
    curl --connect-timeout 5 -s -X PUT http://$IP:8000/api/newdeveloper/groups/0/action -d {\"on\":true};
    curl --connect-timeout 5 -s -X PUT http://$IP:8000/api/newdeveloper/groups/0/action -d {\"on\":false};
done

