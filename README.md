docker-hosts-updater
----------
Automatic update `/etc/hosts` on start/stop containers by filter.

Requirements
-----
* **Native linux**
_This tool has no effect on macOS or windows, because docker on these OS run in
VM and you can't directly access from host to each container via ip._

Usage
-----
Start up `docker-hosts-updater`:

```bash
$ docker run -d --restart=always \
    --name docker-hosts-updater \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /etc/hosts:/opt/hosts \
    registry.develma.com/packages/util/docker-host-updater
```

Environment Variables
-----

| Variable | Description | Default |
|---|---|---|
| `NETWORK_FILTER` | Glob pattern to match Docker network names | _(empty, matches all)_ |
| `CONTAINER_FILTER` | Glob pattern to match container names | _(empty, matches all)_ |

Containers matching **both** filters are targeted. The container name is used as the hostname in `/etc/hosts`.

```bash
$ docker run -d --restart=always \
    --name docker-hosts-updater \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /etc/hosts:/opt/hosts \
    -e NETWORK_FILTER="my_project_*" \
    -e CONTAINER_FILTER="web-*" \
    registry.develma.com/packages/util/docker-host-updater
```

Custom Hostname
-----
To override the default hostname (container name), add the `dhu.hostname` label to the container:

```bash
$ docker run -d --label dhu.hostname=nginx.local nginx
$ ping nginx.local
```
