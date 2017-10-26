# Gateway_Testbed
PSI Re-implementation using Containers

1. Initially develop files for running gateway on CloudLab
2. Port files to run on RaspberryPi

For Cloudlab Operations:
1. Run setup-node.sh on each node (one is the client--packet generator, the other is the server--packet sink)
2. Run setup-data-plane.sh on the dataplane node (will serve as the bridge between the client & server)
3. Can generate TCP messages using muti_iperf3_*.py files
