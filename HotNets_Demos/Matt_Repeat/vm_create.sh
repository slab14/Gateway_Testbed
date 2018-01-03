#!/bin/bash

# Take one argument from the commandline: VM name
if ! [ $# -eq 1 ]; then
    echo "Usage: $0 <node-name>"
    exit 1
fi

# Check if domain already exists
sudo virsh dominfo $1 > /dev/null 2>&1
if [ "$?" -eq 0 ]; then
    echo -n "[WARNING] $1 already exists.  "
    read -p "Do you want to overwrite $1 [y/N]? " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
    else
        echo -e "\nNot overwriting $1. Exiting..."
        exit 1
    fi
fi

# Directory to store images
DIR=~/virt/images

# Location of cloud image
IMAGE=$DIR/CentOS-7-x86_64-GenericCloud.qcow2

# Amount of RAM in MB
MEM=8192

# Number of virtual CPUs
CPUS=4

# Cloud init files
USER_DATA=user-data
META_DATA=meta-data
CI_ISO=$1-cidata.iso
DISK=$1.qcow2

# Bridge for VMs (default on Fedora is virbr0)
BRIDGE=virbr0

# Start clean
sudo rm -rf $DIR/$1
mkdir -p $DIR/$1

pushd $DIR/$1 > /dev/null

    # Create log file
    touch $1.log

    # Remove domain with the same name
    sudo virsh destroy $1 >> $1.log 2>&1
    sudo virsh undefine $1 >> $1.log 2>&1

    # cloud-init config: set hostname, remove cloud-init package,
    # and add ssh-key

    SSH_KEY=$(<$HOME/.ssh/id_rsa.pub)
    
    cat > $USER_DATA << _EOF_
#cloud-config

# Hostname management
preserve_hostname: False
hostname: $1
fqdn: $1.example.local

# Remove cloud-init when finished with it
runcmd:
  - [ yum, -y, remove, cloud-init ]

# Configure where output will go
output: 
  all: ">> /var/log/cloud-init.log"

# configure interaction with ssh server
ssh_svcname: ssh
ssh_deletekeys: True
ssh_genkeytypes: ['rsa', 'ecdsa']

# Install my public ssh key to the first user-defined user configured 
# in cloud.cfg in the template (which is centos for CentOS cloud images)
ssh_authorized_keys:
 - ${SSH_KEY}
_EOF_

    echo "instance-id: $1; local-hostname: $1" > $META_DATA

    cp $IMAGE $DISK

    # Create CD-ROM ISO with cloud-init config
    genisoimage -output $CI_ISO -volid cidata -joliet -r $USER_DATA $META_DATA &>> $1.log

    sudo virt-install --import --name $1 --ram $MEM --vcpus $CPUS --disk \
    $DISK,format=qcow2,bus=virtio --disk $CI_ISO,device=cdrom --network \
    bridge=virbr0,model=virtio --os-type=linux --os-variant=rhel6 \
    --noautoconsole 

    # Eject cdrom
    sudo virsh change-media $1 hda --eject --config >> $1.log

    # Remove the unnecessary cloud init files
    sudo rm $USER_DATA $CI_ISO

popd > /dev/null
