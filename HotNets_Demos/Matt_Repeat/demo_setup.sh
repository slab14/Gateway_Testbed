#!/bin/bash

VERSION=$(sudo cat /etc/*-release | grep '^NAME="' | awk -F '"' '{ print $2 }')

if [[ $VERSION =~ "CentOS" ]]; then
    sudo yum update -y
    sudo yum install -yqq libvirt libvirt-client libvirt-python qemu-kvm \
	 virt-manager qemu-img genisoimage bridge-utils xauth
fi

if [[ $VERSION =~ "Ubuntu" ]]; then
    sudo apt-get update -y
    sudo apt-get install -yqq kvm cloud-utils genisoimage wget virt-manager \
	 libvirt-bin qemu-kvm bridge-utils
fi

sudo systemctl restart libvirtd

# Create place for VM images to reside
mkdir -p ~/virt/images
cd ~/virt/images

# Download VM image
IMAGE=CentOS-7-x86_64-GenericCloud.qcow2

if [ ! -f "$IMAGE" ]; then
    wget http://cloud.centos.org/centos/7/images/$IMAGE.xz
    xz --decompress $IMAGE.xz
fi

cd $HOME/Gateway_Testbed/HotNets_Demos/Matt_Repeat

# Setup SSH for VMs
PUBKEY="$HOME/.ssh/id_rsa.pub"

if [ ! -f $PUBKEY ]; then
    ssh-keygen -t rsa -q -N
fi

SSH_KEY=$(<$PUBKEY)

# Generate VMs
./vm_create.sh $1
./vm_create.sh $2
./vm_create.sh $3

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


