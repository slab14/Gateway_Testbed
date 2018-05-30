IP=$1
f=$2

httping -g $IP:8000/api/newdeveloper/groups/0 -S -v -c 100 > $f.txt
