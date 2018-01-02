#!/bin/bash

# Download required packages for running VMs
sudo yum install -y libvirt-client virt-install genisoimage

# Create place for VM images to reside
mkdir -p ~/virt/images
cd virt/images

# Download VM image
IMAGE=CentOS-7-x86_64-GenericCloud.qcow2

if [ ! -f "$IMAGE" ]; then
    wget http://cloud.centos.org/centos7/images/$IMAGE.xz
    xz --decompress $IMAGE.xz
fi

# Setup SSH for VMs
PUBKEY="$HOME/.ssh/id_rsa.pub"

if [ ! -f PUBKEY ]; then
    echo "place the below ssh key into vm installer script \n"
    ssh-keygen -t rsa
fi

SSH_KEY=$(<$PUBKEY)

# Generate VMs
./vm_create.sh $1
./vm_create.sh $2
./vm_Create.sh $3

# VM IP addresses for SSH
VM1_IP=$(./find_ip.sh $1)
VM2_IP=$(./find_ip.sh $2)
VM3_IP=$(./find_ip.sh $3)
echo "VM $1 is at $VM1_IP"
echo "VM $2 is at $VM2_IP"
echo "VM $3 is at $VM3_IP"

## Setup VMs
# VM1 = user/attacker (name is $1)
touch temp_vm1.txt
echo "touch device_ip.txt
echo "$VM2_IP" > device_ip.txt
export http_server=http://$VM3_IP:3128" > temp_VM1.txt

echo temp_VM1.txt >> vm1_setup.sh
chmod +x vm1_setup.sh

cat vm1_setup.sh | ssh centos@$VM1_IP sh

# VM2 = device (software emulation, name is $2)
cat vm2_setup.sh | ssh centos@$VM2_IP sh

# VM3 = Squid proxy server (name is $3)
cat vm3_setup.sh | ssh centos@$VM3_IP sh


