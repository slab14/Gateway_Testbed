IP=$1
NUM=$2
OUTPUT=$3

for i in `seq 1 $NUM`
do
    { time curl -U tommy:iotsec --connect-timeout 5 -s -X PUT http://$IP:8000/api/newdeveloper/groups/0/action -d {\"on\":true} --silent --output /dev/null ; } 2>> $OUTPUT
    { time curl -U tommy:iotsec --connect-timeout 5 -s -X PUT http://$IP:8000/api/newdeveloper/groups/0/action -d {\"on\":false} --silent --output /dev/null ; } 2>> $OUTPUT
done
