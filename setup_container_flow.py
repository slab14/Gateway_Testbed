# Borrowed from J. Helt

# invocation example
## python setup_container_flow.py -E exp/001.json -B br0 -T setup


import argparse
import ipaddress
import itertools
import json
import shlex
import subprocess

def get_nf_id(chain_prefix, i):
    return '{}_{}'.format(chain_prefix, i)

def start_nfs(nf_platform, chain, chain_prefix):
    i = 0
    for nf in chain:
        nf_id = get_nf_id(chain_prefix, i)
        if nf_platform == 'docker':
            cmd = ('/usr/bin/sudo /usr/bin/docker run -itd --rm ' +
                   '--network=none --name {} {}')
            cmd = cmd.format(nf_id, nf['tag'])
            subprocess.check_call(shlex.split(cmd))
        else:
            raise ValueError('Unknown nf platform: {}'.format(nf_platform))

        i += 1

def attach_nfs(network_platform, nf_platform, bridge, chain, chain_prefix):
    interfaces = ('eth0', 'eth1')
    
    i = 0
    for nf in chain:
        nf_id = get_nf_id(chain_prefix, i)
        if network_platform == 'ovs' and nf_platform == 'docker':
            for interface in interfaces:
                cmd = '/usr/bin/sudo /usr/bin/ovs-docker add-port {} {} {}'
                cmd = cmd.format(bridge, interface, nf_id)
                subprocess.check_call(shlex.split(cmd))
        else:
            raise ValueError('Unknown combination: '+
                             '{} and {}'.format(network_platform,
                                                nf_platform))

        i += 1


# TODO: Move this to ovs-docker lib
# Adapted from ovs-docker
def find_openflow_port_for_container_interface(bridge, nf_id, interface):
    cmd = '/usr/bin/sudo /usr/bin/ovs-vsctl --data=bare --no-heading \
                                            --columns=name find \
                 interface external_ids:container_id={}  \
                 external_ids:container_iface={}'

    cmd = cmd.format(nf_id, interface)
    ovs_port = subprocess.check_output(shlex.split(cmd))
    ovs_port = ovs_port.strip()

    cmd = '/usr/bin/sudo /usr/bin/ovs-ofctl show {} | grep {}'.format(bridge, ovs_port) + " | awk -F '(' '{ print $1 }'"
    of_port = subprocess.check_output(cmd, shell=True) #No shlex w/shell=True
    of_port = of_port.strip()

    if not of_port:
        raise ValueError('Could not find OF port for: '+
                         '{} {} {}'.format(bridge, nf_id, interface))

    return of_port

def pairwise(iterable):
    's -> (s0, s1), (s2, s3), (s4, s5), ...'
    a = iter(iterable)
    return itertools.izip(a, a)


def install_route(network_platform, nf_platform, bridge, chain, chain_prefix, client_ip, server_ip):
    interfaces = ('eth0', 'eth1')
    nf_ids = [get_nf_id(chain_prefix, i) for i in range(len(chain))]

    if network_platform == 'ovs' and nf_platform == 'docker':
        of_ports = []
        for nf_id in nf_ids:
            of_ports += [find_openflow_port_for_container_interface(bridge, nf_id, interface) for interface in interfaces]

        # Client-side is assumed to be of_port 1 and server-side is assumed to be of_port 2            
        of_ports = [1] + of_ports + [2]

        # Client to server
        for in_port,out_port in pairwise(of_ports):
            cmd = '/usr/bin/sudo /usr/bin/ovs-ofctl add-flow {} "priority=100 ip in_port={} nw_src={} nw_dst={} actions=output:{}"'
            cmd = cmd.format(bridge, in_port, client_ip, server_ip, out_port)
            subprocess.check_call(shlex.split(cmd))

        # Server to client
        for in_port,out_port in pairwise(reversed(of_ports)): # NOTE: reversed
            cmd = '/usr/bin/sudo /usr/bin/ovs-ofctl add-flow {} "priority=100 ip in_port={} nw_src={} nw_dst={} actions=output:{}"'
            cmd = cmd.format(bridge, in_port, server_ip, client_ip, out_port) # NOTE: ips swapped
            subprocess.check_call(shlex.split(cmd))

        # Allow other traffic to bypass data plane
        cmd = ('/usr/bin/sudo /usr/bin/ovs-ofctl add-flow {} '+
               '"priority=0 in_port=1 actions=output:2"')
        cmd = cmd.format(bridge)
        subprocess.check_call(shlex.split(cmd))
        cmd = ('/usr/bin/sudo /usr/bin/ovs-ofctl add-flow {} '+
               '"priority=0 in_port=2 actions=output:1"')
        cmd = cmd.format(bridge)
        subprocess.check_call(shlex.split(cmd))

    else:
        raise ValueError('Unknown combination: {} and {}'.format(network_platform, nf_platform))


def start_chain(bridge, network_platform, nf_platform, client_ip, server_ip, chain, chain_prefix):
    start_nfs(nf_platform, chain, chain_prefix)
    attach_nfs(network_platform, nf_platform, bridge, chain, chain_prefix)
    install_route(network_platform, nf_platform, bridge, chain, chain_prefix, client_ip, server_ip)

def teardown_chain(bridge, network_platform, nf_platform, chain, chain_prefix):
    interfaces = ('eth0', 'eth1')
    nf_ids = [get_nf_id(chain_prefix, i) for i in range(len(chain))]

    if network_platform == 'ovs' and nf_platform == 'docker':
        for nf_id in nf_ids:
            cmd = '/usr/bin/sudo /usr/bin/ovs-docker del-ports {} {}'
            cmd = cmd.format(bridge, nf_id)
            subprocess.check_call(shlex.split(cmd))

            cmd = '/usr/bin/sudo /usr/bin/docker kill {}'
            cmd = cmd.format(nf_id)
            subprocess.check_call(shlex.split(cmd))

        cmd = '/usr/bin/sudo /usr/bin/ovs-ofctl del-flows {}'
        cmd = cmd.format(bridge)
        subprocess.check_call(shlex.split(cmd))
        
    else:
        raise ValueError('Unknown combination: {} and {}'.format(network_platform, nf_platform))

def parse_chains(route_defs, chain_defs):
    chains = []
    for d in route_defs:
        c = d['chain_id']
        n = d['n']
        chains += [chain_defs[c] for i in range(n)]

    return chains

def parse_chain_prefixes(route_defs):
    chain_prefixes = []
    for d in route_defs:
        c = d['chain_id']
        n = d['n']
        chain_prefixes += ['{}_{}'.format(c, i) for i in range(n)]

    return chain_prefixes

def main():
    parser = argparse.ArgumentParser(description='Setup an experiment from a json definition')
    parser.add_argument('--exp', '-E', required=True, type=str, help='path to experiment definition')
    parser.add_argument('--bridge', '-B', required=True, type=str, help='bridge name')
    parser.add_argument('--type', '-T', required=True, type=str, help='setup or teardown')
    args = parser.parse_args()

    with open(args.exp, 'r') as f:
        exp_def = json.load(f)

    route_defs = exp_def['routes']
    chain_defs = exp_def['chains']
    nf_platform = exp_def['nf_platform']
    network_platform = exp_def['network_platform']
    client_startip = ipaddress.ip_address(exp_def['client_startip'])
    server_startip = ipaddress.ip_address(exp_def['server_startip'])
    bridge = args.bridge
    etype = args.type

    n_routes = sum(map(lambda d: d['n'], route_defs))
    client_ips = [client_startip + i for i in range(n_routes)]
    server_ips = [server_startip + i for i in range(n_routes)]
    chains = parse_chains(route_defs, chain_defs)
    chain_prefixes = parse_chain_prefixes(route_defs)

    for i in range(n_routes):
        client_ip = client_ips[i]
        server_ip = server_ips[i]
        chain = chains[i]
        chain_prefix = chain_prefixes[i]
        if etype == 'setup':
            start_chain(bridge, network_platform, nf_platform, client_ip, server_ip, chain, chain_prefix)
        else:
            teardown_chain(bridge, network_platform, nf_platform, chain, chain_prefix)


if __name__ == '__main__':
    main()
