# Borrowed from J. Helt

from os import path
import argparse
import ipaddress
import json
import shlex
import signal
import subprocess
import time

# Constants
OUT_FILE_FORMAT = '{}_{}_{}.out' # .format(user_id, chain_id, i)
SLEEP_INTERVAL_S = 5
N_OMIT = 5
MSS = 1460

# Globals
running = True

def handler(signum, frame):
    global running
    running = False

def start_client(client_ip, server_ip, n_flows, rate, out_file):
    cmd = '/usr/bin/iperf3 -V -O {} -M {} -B {} -c {} -P {} -b {}'
    cmd = cmd.format(N_OMIT, MSS, client_ip, server_ip, n_flows, rate)
    with open(out_file, 'w') as out:
        return subprocess.Popen(shlex.split(cmd), stdout=out)

def start_server(server_ip):
    cmd = '/usr/bin/iperf3 -B {} -s'.format(server_ip)
    return subprocess.Popen(shlex.split(cmd))

def set_interface_ip(interface, ips):
    for ip in ips: 
        cmd = '/usr/bin/sudo /sbin/ip addr add {}/16 dev {}'
        cmd = cmd.format(ip, interface)
        subprocess.call(shlex.split(cmd))

def parse_n_flowss(route_defs, user_defs):
    n_flowss = []
    for d in route_defs:
        n_flows = user_defs[d['user_id']]['n_flows']
        n = d['n']
        n_flowss += [n_flows for i in range(n)]

    return n_flowss

def parse_rates(route_defs, user_defs):
    rates = []
    for d in route_defs:
        u = user_defs[d['user_id']]
        if 'rate' in u:
            rate = u['rate']
        else:
            rate = 0 # Infinite
            
        n = d['n']
        rates += [rate for i in range(n)]

    return rates

def parse_out_files(out_dir, route_defs):
    out_files = []
    for d in route_defs:
        u = d['user_id']
        c = d['chain_id']
        n = d['n']
        out_files += [path.join(out_dir, OUT_FILE_FORMAT.format(u, c, i)) for i in range(n)]

    return out_files

def main():
    parser = argparse.ArgumentParser(description='Manage multiple iperf3 '
                                     'processes.')
    parser.add_argument('--exp', '-E', required=True, type=str,
                        help='path to experiment definition')
    parser.add_argument('--outdir', '-O', required=True, type=str,
                        help='path to out directory')
    parser.add_argument('--type', '-T', required=True, type=str,
                        help='client or server')
    parser.add_argument('--interface', '-I', required=True, type=str,
                        help='interface name')
    args = parser.parse_args()

    with open(args.exp, 'r') as f:
        exp_def = json.load(f)

    user_defs = exp_def['users']
    route_defs = exp_def['routes']
    client_startip = ipaddress.ip_address(exp_def['client_startip'])
    server_startip = ipaddress.ip_address(exp_def['server_startip'])
    interface = args.interface
    mtype = args.type
    out_dir = args.outdir

    n_routes = sum(map(lambda d: d['n'], route_defs))
    server_ips = [server_startip + i for i in range(n_routes)]

    if mtype == 'server':
        set_interface_ip(interface, server_ips)
        procs = map(start_server, server_ips)
    elif mtype == 'client':
        client_ips = [client_startip + i for i in range(n_routes)]
        set_interface_ip(interface, client_ips)
        n_flowss = parse_n_flowss(route_defs, user_defs)
        rates = parse_rates(route_defs, user_defs)
        out_files = parse_out_files(out_dir, route_defs)
        procs = map(start_client, client_ips, server_ips,
                    n_flowss, rates, out_files)
    else:
        raise ValueError('Unknown type: {}'.format(mtype))


    print 'Installing signal handlers'
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    while running:
        time.sleep(SLEEP_INTERVAL_S)

        # If all procs have exited
        if all(map(lambda p: p.poll() != None, procs)):
            break
        
    print 'Cleaning up!'
    for p in procs:
        # If proc hasn't exited yet
        if p.returncode == None:
            p.terminate()

if __name__ == '__main__':
    main()
