# Borrowed from J. Helt

import argparse
import ipaddress
import re
import shlex
import signal
import subprocess
import sys
import time


# Globals
RUNNING = True


def handler(signum, frame):
    global RUNNING
    RUNNING = False


def start_client(ip):
    cmd = '/usr/bin/iperf3 -c {}'.format(ip)
    return subprocess.Popen(shlex.split(cmd))


def start_server(ip):
    cmd = '/usr/bin/iperf3 -s -B {}'.format(ip)
    return subprocess.Popen(shlex.split(cmd))


def main():
    parser = argparse.ArgumentParser(description='Manage multiple iperf3 processes.')
    parser.add_argument('--num', '-N', required=True, type=int, help='number of processes to start')
    parser.add_argument('--startip', '-S', required=True, type=unicode, help='starting ip address')
    parser.add_argument('--type', '-T', required=True, type=str, help='server or client')
    parser.add_argument('--args', '-A', type=str, help='pass-through args for iperf')
    args = parser.parse_args()

    n_proc = args.num
    start_ip = ipaddress.ip_address(re.sub(r'/[0-9]*', '', args.startip))
    network = ipaddress.ip_network(args.startip, strict=False)
    ips = [start_ip + i for i in range(n_proc)]

    # Check that all ips are in the network
    if not all(map(lambda ip: ip in network, ips)):
        print 'ERROR: You requested more ip addresses than are available in the network.'
        sys.exit(1)

    if args.type == 'server':
        procs = map(start_server, ips)
    elif args.type == 'client':
        procs = map(start_client, ips)
    else:
        raise ValueError('Unknown type: {}'.format(args.type))


    print 'Installing signal handlers'
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    while RUNNING:
        time.sleep(10)

    print 'Cleaning up!'
    for p in procs:
        p.terminate()


if __name__ == '__main__':
    main()
