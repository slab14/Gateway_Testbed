# Goal: Create simple controller for v0 demo (1 device to container, change policy)

import ipaddress
import json
import subprocess
import shlex

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
    

# Setup-flow
# -- input is output of Get-FSM_DAG (or the variable that it creates).
def setup_flow(states, flow):
    init_mbox = flow[states[0]]
    name = states[0]
    start_nf_container(init_mbox, name)
    

def main():
    policy = {}
    policy = Get_FSM_DAG('exp/policy1.json')
    for i in range(0, policy['n_devices']):
        setup_flow(policy[i]['states'], policy[i]['flow'])

if __name__== '__main__':
    main()
