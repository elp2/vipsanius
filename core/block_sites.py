#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading

REDIRECT_IP = '0.0.0.0'

def backup_hosts_file():
    backup_path = hosts_file() + '.backup'
    if not os.path.exists(backup_path):
        shutil.copy(hosts_file(), backup_path)
        print(f"Hosts file backed up to {backup_path}")

def load_groups(file_path):
    with open(file_path, 'r') as f:
        groups = json.load(f)
    resolved_groups = {}
    for group, hosts in groups.items():
        resolved_hosts = []
        for host in hosts:
            if host in groups:
                resolved_hosts.extend(groups[host])
            else:
                resolved_hosts.append(host)
        resolved_groups[group] = resolved_hosts
    return resolved_groups

def block_group(group_name, groups):
    hosts_to_block = groups.get(group_name, [])
    if not hosts_to_block:
        print(f"No such group: {group_name}")
        return
    with open(hosts_file(), 'r+') as file:
        content = file.read()
        for host in hosts_to_block:
            entry = f"{REDIRECT_IP} {host}\n"
            # TODO make edits in a protected section of the file and overwrite entries.
            # This just appends to the end. This is not so bad for now since unblock does line by line.
            file.write(entry)
        print(f"Blocked group: {group_name}")

def unblock_group(group_name, groups):
    hosts_to_unblock = groups.get(group_name, [])
    if not hosts_to_unblock:
        print(f"No such group: {group_name}")
        return
    with open(hosts_file(), 'r') as file:
        lines = file.readlines()
    with open(hosts_file(), 'w') as file:
        for line in lines:
            if not any(host in line for host in hosts_to_unblock):
                file.write(line)
    print(f"Unblocked group: {group_name}")

def temporary_unblock(group_name, groups, duration):
    unblock_group(group_name, groups)
    flush_dns()
    print(f"Group {group_name} will be re-blocked after {duration} seconds.")

    def reblock_and_flush_dns(group_name, groups):
        block_group(group_name, groups)
        flush_dns()
    timer = threading.Timer(duration, reblock_and_flush_dns, [group_name, groups])
    timer.start()

def hosts_file():
    if os.name == 'nt':  # Windows
        return r'C:\Windows\System32\drivers\etc\hosts'
    else:  # Linux/MacOS
        return '/etc/hosts'

def flush_dns():
    if os.name == 'nt':  # Windows
        assert None, "TODO"
    else:  # Linux/MacOS
        try:
            subprocess.run(["killall", "-HUP", "mDNSResponder"], check=True)
            print("DNS cache flushed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while flushing DNS cache: {e}")

def main():
    parser = argparse.ArgumentParser(description='Block or unblock groups of websites.')
    parser.add_argument('action', choices=['block', 'unblock', 'temp_unblock', 'config'], help='Action to perform')
    parser.add_argument('--group', help='Name of the group')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds for temporary unblock')

    args = parser.parse_args()

    groups = load_groups('/Users/edwardpalmer/dev/vipsanius/core/sample_groups.json')

    backup_hosts_file()

    if args.action == 'block':
        block_group(args.group, groups)
    elif args.action == 'unblock':
        unblock_group(args.group, groups)
    elif args.action == 'temp_unblock':
        temporary_unblock(args.group, groups, args.duration)
    elif args.action == 'config':
        print(json.dumps(groups))

if __name__ == '__main__':
    main()
