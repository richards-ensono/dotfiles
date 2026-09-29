---
name: podman-containers
description: Run containerised workloads with rootless Podman using the hardened podman-run.sh wrapper, and discover the correct DOCKER_HOST socket from the podman CLI rather than guessing. Use when running untrusted or unreviewed code in a container, when a tool needs DOCKER_HOST or a Docker-compatible socket (Testcontainers, docker compose, CI emulators), or when a docker command fails with a socket permission error.
license: MIT
compatibility: Linux only. Requires podman >= 4 (rootless recommended) and subuid/subgid ranges.
metadata:
  author: rslater
  version: "1.0"
---

# Rootless Podman

Podman is the container runtime on this host. `docker` is a shim that execs
`podman`, so "docker" commands are Podman commands - the Docker daemon and its
root socket are not present.

Container tooling is never wrapped in Bubblewrap (see the `bubblewrap-sandbox`
skill, sections 2.2-2.3: nesting would require handing back user namespaces,
`newuidmap`, `/dev/fuse`, and cgroup delegation). **The container runtime is the
security boundary instead, which means its flags have to carry the weight.** Use
the wrapper below rather than hand-rolling `podman run`.

## 1. Use `podman-run.sh`

`podman-run.sh`, beside this file, applies the hardened defaults and refuses the
dangerous flags outright. Read it before first use.

```sh
podman-run.sh [options] -- IMAGE [COMMAND...]

  --rw PATH           Bind PATH read-write (repeatable); refuses sensitive paths
  --ro PATH           Bind PATH read-only (repeatable)
  --net none|private  Default none; host is refused
  --env NAME[=VALUE]  Forward one variable; refuses secret-looking names
  --memory SIZE       Default 2g
  --pids-limit N      Default 512
  --timeout SECONDS   Default 900
  --allow-tag         Permit a non-digest-pinned image
  --as-root           Root inside the container (warns; still rootless on host)
  --dry-run           Print a redacted invocation and exit
```

Defaults it applies: `--rm --read-only --tmpfs /tmp --cap-drop=ALL
--security-opt no-new-privileges --userns=keep-id --network=none`, with `$PWD`
mounted **read-only** at `/workspace`.

Typical uses:

```sh
# Run a test suite offline against a digest-pinned image
podman-run.sh -- docker.io/library/node@sha256:... npm test

# Allow writes to the build output directory only (create dist on the host first)
mkdir -p dist
podman-run.sh --rw "$PWD/dist" -- <image@sha256:...> npm run build

# Network needed for a dependency fetch - state the reason when you do this
podman-run.sh --net private -- <image@sha256:...> go mod download
```

Escalate deliberately, one flag at a time, and say why in your report. If the
wrapper refuses something, that refusal is the finding - do not bypass it by
calling `podman run` directly.

### Why these defaults

- **`--userns=keep-id`, not `--user $(id -u)`.** In rootless Podman a container
  UID maps through `/etc/subuid`, so `--user 1000` becomes host UID 101000 and
  **cannot write bind mounts at all** (verified: `touch` fails with permission
  denied). `keep-id` maps the container user onto your host UID, giving both a
  non-root container process and correctly owned files. Omitting both leaves you
  as root-in-container, which works for ownership but keeps the capability
  surface.
- **`--read-only` plus `--tmpfs /tmp`** stops writes to the image filesystem while
  leaving scratch space. The wrapper overlays explicitly writable project paths
  at their corresponding `/workspace/...` locations; the rest stays read-only.
- **`--cap-drop=ALL`** yields `CapEff: 0000000000000000`.
- **`--network=none` by default** because most builds and test suites do not need
  the network, and one that unexpectedly does is a finding.
- **Digest pinning** - tags are mutable, so `--allow-tag` requires a stated reason.
- **Podman does not inherit the host environment.** Variables reach the container
  only via `--env`; never use `--env-host`.
- `:Z` relabelling is applied only when SELinux is actually enabled.
- The wrapper refuses a rootful Podman runtime, sensitive mounts (even read-only),
  and Unix sockets. Its status log redacts environment values and payload arguments.

## 2. Never pass these

- `--privileged` - equivalent to root on the host.
- `-v /:/host`, `-v $HOME:...`, or any mount of `~/.ssh`, `~/.gnupg`, `~/.aws`,
  `~/.kube`, `~/.config/gh`, `~/.npmrc`, `~/.local/share/chezmoi`.
- Mounting a container socket into a container (`podman.sock`, `docker.sock`) -
  container escape by design.
- `--userns=host`, `--pid=host`, `--ipc=host`, `--net=host` as a default.
- `--cap-add`, `--security-opt seccomp=unconfined`, `--security-opt label=disable`,
  `--security-opt apparmor=unconfined`.
- `--device` for anything the task does not demonstrably need.
- `--env-host`.

Do not quietly widen a container to make a command pass. Report the effective
network and mount permissions, without printing environment values or payload
arguments that could carry credentials.

## 3. Finding the correct `DOCKER_HOST`

Some tools (Testcontainers, `docker compose`, CI emulators, IDE plugins) need a
Docker-compatible socket. Derive it from the `podman` CLI - never hardcode
`/var/run/docker.sock` and never guess.

**Step 1 - check for configured connections.**

```sh
podman system connection list --format json
```

- **Empty (`[]`)** - no remote connections are configured, so this is a purely
  local rootless setup. Go to step 2. (That is the current state on this host.)
- **Non-empty** - find the entry with `"Default": true` and read its `URI`:
  - `unix://...` - local; safe to use.
  - `ssh://...` or `tcp://...` - **remote. Do not set `DOCKER_HOST` to it.**
    Per the repository security rules, only the current user's local rootless
    socket may be used. Report the remote connection and ask.

**Step 2 - ask Podman for the local socket path.**

```sh
podman info --format '{{.Host.RemoteSocket.Path}}'   # e.g. /run/user/1000/podman/podman.sock
podman info --format '{{.Host.RemoteSocket.Exists}}' # must be true
podman info --format '{{.Host.Security.Rootless}}'   # expect true
```

**Step 3 - export it, derived rather than typed.**

```sh
export DOCKER_HOST="unix://$(podman info --format '{{.Host.RemoteSocket.Path}}')"
# equivalently: unix:///run/user/$(id -u)/podman/podman.sock
```

**Step 4 - if the socket does not exist, start the user service.**

```sh
systemctl --user enable --now podman.socket
systemctl --user is-active podman.socket   # expect: active
```

Verify with `podman --remote info >/dev/null && echo ok`, or
`curl --unix-socket "${DOCKER_HOST#unix://}" http://d/_ping`.

### Rules for `DOCKER_HOST`

- Only ever the **current user's rootless socket** under `/run/user/$(id -u)/`.
- **Never** `/run/podman/podman.sock` (the rootful socket) and never a `tcp://`
  endpoint - unauthenticated TCP is remote root-equivalent access.
- **Never** a remote or untrusted endpoint, including one already present in
  `podman system connection list`.
- Do not mount the socket into a container to satisfy a tool. If something
  genuinely needs Docker-in-Docker semantics, raise it rather than mounting.
- Set it in the environment of the command that needs it; do not persist it into
  shell startup files without asking.

Related Testcontainers settings, when that is the caller:

```sh
export DOCKER_HOST="unix://$(podman info --format '{{.Host.RemoteSocket.Path}}')"
export TESTCONTAINERS_RYUK_DISABLED=true          # Ryuk needs the socket mounted
export TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock
```

Disabling Ryuk means containers are not reaped automatically - clean up with
`podman ps -a` / `podman rm` afterwards.

## 4. Troubleshooting

- **`permission denied` on the socket** - inspect `podman system connection list`
  first, then fall back to the local rootless socket as in §3. Do not `sudo`, and
  do not point at another user's socket.
- **`"/" is not a shared mount`** warning - benign for most workloads; it affects
  mount propagation for rootless containers.
- **Files owned by 101000+ after a run** - a container UID leaked through the
  subuid mapping; use `--userns=keep-id`. Fix ownership with
  `podman unshare chown -R 0:0 <path>`.
- **`newuidmap: write to uid_map failed`** - `/etc/subuid` and `/etc/subgid` lack
  a range for the user. Report it; it needs administrator action.
- **Image pull fails with the network disabled** - pull on the host first, then
  run with `--net none`.
