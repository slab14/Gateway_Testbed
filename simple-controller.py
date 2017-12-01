# Goal: Create simple controller for v0 demo (1 device to container, change policy)

import argparse
import ipaddress
import json
import subprocess
import shlex
import itertools
import os

# TODO:
# - Setup-flow
# -- Take output from Get-FSM_DAG, create corresponding dataplane
# - Transition
# -- tear down existing flow, setup new flow based upon transition in FSM
# - Clean-up
# -- Clear flows setup


## Future Updates
# - Rx_Container
# -- Process messages from containers (to call transitions)
# - Update-FSM_DAG
# -- recognize updates to "policy" and update accordingly
# - Verify


# Get-FSM_DAG
def Get_FSM_DAG(fd):
    with open(fd, 'r') as f:
        json_data = json.load(f)
    f.close

    dev_policy = {}
    dev_policy['policy_description'] = json_data['description']
    dev_policy['nf_platform'] = json_data['nf_platform']
    in_ip = ipaddress.ip_address(json_data['in_port'])
    out_ip = ipaddress.ip_address(json_data['out_port'])
    dev_policy['in_ip'] = json_data['in_port']
    dev_policy['out_ip'] = json_data['out_port']
    dev_policy['n_devices'] = json_data['n_devices']
    FSM_defs = json_data['FSM_defs']
    DAG_defs = json_data['DAG_defs']
    policy = json_data['policy']

    i = 0
    for device in policy:
        dev_policy[i] = {}
        dev_policy[i]['SM'] = policy[device]['state_machine']
        dev_policy[i]['states'] = []
        for j in range(0, int(FSM_defs[dev_policy[i]['SM']]['n'])):
            dev_policy[i]['states'].append(FSM_defs[dev_policy[i]['SM']][str(j)])
        dev_policy[i]['DAG'] = policy[device]['DAG']
        dev_policy[i]['flow'] = {}
        for k in dev_policy[i]['states']:
            dev_policy[i]['flow'][k] = DAG_defs[dev_policy[i]['DAG']][k]
        i=+1

    return dev_policy


#Start-up NF Container
def start_nf_container(init_mbox, name):
    cmd = ('/usr/bin/sudo /usr/bin/docker run -itd --rm ' +
           '--network=none --name {} {}')
    cmd = cmd.format(name, init_mbox)
    subprocess.check_call(shlex.split(cmd))


def add_nf_flow(bridge, name, interfaces):
    for interface in interfaces:
        cmd = '/usr/bin/sudo /usr/bin/ovs-docker add-port {} {} {}'
        cmd = cmd.format(bridge, interface, name)
        subprocess.check_call(shlex.split(cmd))
    
def find_of_port(bridge, name, interface):
    cmd = '/usr/bin/sudo '
    cmd += '/usr/bin/ovs-vsctl --data=bare --no-heading --columns=name find \
    interface external_ids:container_id={} external_ids:container_iface={}'
    cmd = cmd.format(name, interface)
    ovs_port = subprocess.check_output(shlex.split(cmd))
    ovs_port = ovs_port.strip()

    cmd = '/usr/bin/sudo /usr/bin/ovs-ofctl show {} | grep {} '
    cmd = cmd.format(bridge, ovs_port)
    cmd += "| awk -F '(' '{ print $1 }'"
    of_port = subprocess.check_output(cmd, shell=True)
    of_port = of_port.strip()

    return of_port


def pairwise(iterable):
    's -> (s0, s1), (s2, s3), (S4, s5), ...'
    a = iter(iterable)
    return itertools.izip(a,a)


def install_route(bridge, name, interfaces, in_ip, out_ip):
    interfaces = ('eth0', 'eth1')
    of_ports = []
    of_ports += [find_of_port(bridge, name, interface) for interface in interfaces]
    of_ports = [1] + of_ports + [2]

    # From device to mbox to outside
    for in_port, out_port in pairwise(of_ports):
        cmd = '/usr/bin/sudo /usr/bin/ovs-ofctl add-flow {} '.format(bridge)
        cmd+='"priority=100 ip in_port={} nw_src={}"'.format(in_port, in_ip)
        cmd+='" nw_dst={} actions=output:{}"'.format(out_ip, out_port)
        subprocess.check_call(shlex.split(cmd))

    # From outside to mbox to device
    for in_port, out_port in pairwise(reversed(of_ports)):
        cmd = '/usr/bin/sudo /usr/bin/ovs-ofctl add-flow {} '.format(bridge)
        cmd+='"priority=100 ip in_port={} nw_src={}"'.format(in_port, out_ip)
        cmd+='" nw_dst={} actions=output:{}"'.format(in_ip, out_port)
        subprocess.check_call(shlex.split(cmd))

    # All other traffic bypass mbox
    cmd = ('/usr/bin/sudo /usr/bin/ovs-ofctl add-flow {} ' +
           '"priority=0 in_port=1 actions=output:2"').format(bridge)
    subprocess.check_call(shlex.split(cmd))
    cmd = ('/usr/bin/sudo /usr/bin/ovs-ofctl add-flow {} ' +
           '"priority=0 in_port=2 actions=output:1"').format(bridge)
    subprocess.check_call(shlex.split(cmd))


# Setup-flow
# -- input is output of Get-FSM_DAG (or the variable that it creates).
def setup_flow(states, flow, in_ip, out_ip, bridge):
    interfaces = ('eth0', 'eth1')
    init_mbox = flow[states[0]]
    name = states[0]
    start_nf_container(init_mbox, name)
    add_nf_flow(bridge, name, interfaces)
    install_route(bridge, name, interfaces, in_ip, out_ip)

def main():
    parser = argparse.ArgumentParser(description='Run PSI demo, json policy')
    parser.add_argument('--policy', '-P', required=True, type=str,
                        help='path to json policy file')
    parser.add_argument('--bridge', '-B', required=True, type=str,
                        help='bridge name')
    args = parser.parse_args()
    
    policy = {}
    policy = Get_FSM_DAG(args.policy)
    for i in range(0, policy['n_devices']):
        setup_flow(policy[i]['states'], policy[i]['flow'],
                   policy['in_ip'], policy['out_ip'], args.bridge)
    stamp=os.stat(args.policy).st_mtime

if __name__== '__main__':
    main()
