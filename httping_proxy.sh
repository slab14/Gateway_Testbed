IP=$1
PROXY=$2
f=$3

httping -g $IP:8000/api/newdeveloper/groups/0 -x $PROXY:13128 --proxy-user tommy --proxy-password iotsec -S -v -c 100 > $f.txt
