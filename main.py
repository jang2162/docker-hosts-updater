import docker
import fnmatch
import os

HOSTNAME_LABEL = 'dhu.hostname'
MARKER = '#### DOCKER HOSTS UPDATER ####'
HOSTS_PATH = '/opt/hosts'
NETWORK_FILTER = os.environ.get('NETWORK_FILTER', '')
CONTAINER_FILTER = os.environ.get('CONTAINER_FILTER', '')


def listen():
    for event in docker.events(decode=True):
        if 'container' == event.get('Type') and event.get('Action') in ["start", "stop", "die"]:
            handle()


def matches_filter(name, pattern):
    if not pattern:
        return True
    return fnmatch.fnmatch(name, pattern)


def scan():
    containers = []
    for container in docker.containers.list():
        networks = container.attrs.get('NetworkSettings', {}).get('Networks', {})

        network_match = any(
            matches_filter(net_name, NETWORK_FILTER) for net_name in networks
        )
        container_match = matches_filter(container.name, CONTAINER_FILTER)

        if not (network_match and container_match):
            continue

        labels = container.attrs.get('Config', {}).get('Labels', {})
        hostname = labels.get(HOSTNAME_LABEL, container.name)

        # Find IP from matching network, or first available
        ip = None
        for net_name, net_info in networks.items():
            if NETWORK_FILTER and fnmatch.fnmatch(net_name, NETWORK_FILTER):
                ip = net_info.get('IPAddress')
                break
        if not ip:
            ip = next(iter(networks.values()), {}).get('IPAddress')

        if ip:
            containers.append({
                'ip': ip,
                'hosts': [hostname],
                'createdAt': container.attrs.get('Created'),
            })

    return containers


def update(items):
    f = open(HOSTS_PATH, 'r+')
    lines = []
    skip_lines = False
    for line in f.read().split('\n'):
        if line == MARKER:
            skip_lines = not skip_lines
            continue

        if not skip_lines:
            lines.append(line)

    if items:
        lines.append(MARKER)
        for ip, value in items.items():
            line = '{} {}'.format(ip, ' '.join(value))
            lines.append(line)
            print(line)
        lines.append(MARKER)

    summary = '\n'.join(lines)

    f.seek(0)
    f.truncate()
    f.write(summary)
    f.close()


def handle():
    print('Recompiling...')
    items = scan()

    summary = {}
    for item in items:
        ip = item.get('ip')
        for host in item.get('hosts'):
            if ip not in summary:
                summary[ip] = []
            summary[ip].append(host)

    update(summary)


docker = docker.from_env()
handle()
listen()
