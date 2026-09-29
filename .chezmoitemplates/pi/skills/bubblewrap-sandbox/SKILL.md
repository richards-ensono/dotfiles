---
name: bubblewrap-sandbox
description: Run untrusted or side-effecting commands (builds, test suites, generated code, freshly installed dependencies, unreviewed scripts) inside an unprivileged Bubblewrap (bwrap) sandbox. Use when executing code you did not review, when a command may touch the network or the home directory, or when the user asks to sandbox, isolate, or contain a command. Also defines what must NEVER be sandboxed - git, dependency resolution, and container tooling - and how to harden the container runtime that replaces the sandbox.
license: MIT
compatibility: Linux only. Requires bubblewrap >= 0.8 (`bwrap`) and unprivileged user namespaces.
metadata:
  author: rslater
  version: "1.2"
---

# Bubblewrap sandboxing

Bubblewrap (`bwrap`) is an unprivileged, setuid-free container launcher. It is the
default containment mechanism for running code in this environment when a full
container runtime is unnecessary or unavailable.

Use it to bound the blast radius of commands. Do not use it as a substitute for
reviewing what a command does.

## 1. Decide first: sandbox, or not?

| Command class | Where it runs | Why |
| --- | --- | --- |
| Build, compile, bundle, transpile | **Sandbox** | Arbitrary code from the repo and its dependency tree. |
| Test suites, linters, formatters, codegen | **Sandbox** | Same; also frequently network-happy. |
| Running freshly installed dependencies for the first time | **Sandbox** | Supply-chain risk is highest here. |
| Any script the agent generated or downloaded | **Sandbox** | Unreviewed by definition. |
| `git` (all subcommands) | **Host, never sandboxed** | Class A, §2. |
| `pre-commit`, commit hooks | **Host** | Class A: they drive `git` and signing. |
| Dependency install / update / resolution | **Host, with `--ignore-scripts`** | See §3. |
| `podman`, `docker`, `buildah`, `nerdctl` | **Host, never sandboxed** | Classes B and C, §2. Harden the runtime instead (§6). |
| `chezmoi apply`, `sudo`, credential tools | **Host** | Class A: sandboxing them is either pointless or broken. |
| Task runners (`eirctl`, `make`, `just`, `npm run`) | **Depends on dispatch** | §2.4. |

If the command is not on this list, default to sandboxing it.

## 2. Commands that must not be sandboxed

Three distinct failure classes. Identify which one applies before exempting
anything - "it is already containerised" is **not** a valid reason on its own,
because a container is a boundary, not a statement that the payload is trusted.

### 2.1 Class A - host-identity tools

`git`, `gpg`, `ssh`, `ssh-add`, `gh`, `chezmoi`, `sudo`, `op`, cloud CLIs.

These authenticate *as the user*. The only way to make them work inside a sandbox
is to hand the sandbox the credentials that make the sandbox pointless.

For `git` specifically, all of these are hard failures inside a namespace:

- **GPG/YubiKey commit signing.** Signing needs `gpg-agent` and the `scdaemon`
  socket plus PC/SC access to the hardware token. A sandbox that can reach those
  is not meaningfully sandboxed.
- **SSH authentication.** Push/fetch needs `SSH_AUTH_SOCK`, which is a YubiKey
  agent here. Binding an agent socket into a sandbox hands the sandbox the ability
  to authenticate as the user, defeating the sandbox.
- **Credential helpers** (`gh auth`, libsecret, keyring) need the session D-Bus and
  the user's secret store.
- **Hook and config resolution.** `core.hooksPath`, `includeIf`, global and system
  config live outside the repo and silently vanish inside a minimal namespace,
  producing wrong-but-successful results.
- **Worktrees, submodules, and alternates** commonly point outside the bind mount.

Corollary rules:

- Never bind `SSH_AUTH_SOCK`, `~/.gnupg`, `~/.ssh`, `/run/user/*/gnupg`, or the
  session D-Bus socket into a `bwrap` sandbox.
- If signing fails, ask the user to retry and touch the token. Never fall back to
  `--no-gpg-sign` or `--no-verify`.
- A sandboxed build that needs version metadata should receive it as an
  environment variable computed on the host (`git describe` on the host,
  `--setenv GIT_DESCRIBE ...` into the sandbox), not by running `git` inside.

### 2.2 Class B - privileged-delegation clients

`docker` against a daemon, `podman --remote`, `kubectl`, `helm`, `systemctl`,
`flatpak`.

The CLI is a thin client; the privileged work happens in a more-privileged
service or on a remote cluster. Sandboxing the client contains the client, not
the effect - and the only way to make it "work" is to bind the API socket, which
is root-equivalent on the host (or account-equivalent on the cluster). This is
*worse* than not sandboxing, because it manufactures the appearance of
containment. Apply the controls at the service instead (§6).

### 2.3 Class C - nested-isolation launchers

`podman`, `buildah`, `nerdctl`, `bwrap` itself, `nix build`.

These build their own isolation and need back exactly what the sandbox removes.
Rootless Podman requires: its own user namespace (directly contradicting
`--disable-userns --assert-userns-disabled`), the setuid `newuidmap`/`newgidmap`
helpers to map the `/etc/subuid` range (setuid is neutralised under
`no_new_privs` and inside a fresh userns), `/run/user/$UID` for the runtime
directory and cgroup delegation, `/dev/fuse` for `fuse-overlayfs`, and its graph
store under `~/.local/share/containers`. Granting all of that leaves a sandbox in
name only. Let the runtime be the boundary and configure it properly (§6).

Note: on this host `docker` is a Podman shim, so `docker` is usually Class C
rather than Class B. The conclusion is the same either way.

### 2.4 Hybrid dispatchers - decide per invocation

`eirctl`, `make`, `just`, `npm run`, `act`, `earthly`, `devcontainer`.

These are not inherently container tools; they are task runners that *may*
dispatch to a container. The exemption follows the dispatch target, never the
binary name:

- Running a **container context** (for example an `eirctl` context backed by a
  container image, or `eirctl shell`) - host, as Class B/C.
- Running a **local/shell context** - this is arbitrary code from a
  repository-supplied config file. Treat it as untrusted and sandbox it.

Never grant a blanket exemption by binary name to a general-purpose task runner:
that lets any repository opt itself out of the sandbox simply by shipping an
`eirctl.yaml` or a `Makefile`. Check the task definition first; if you cannot
tell which context a task uses, sandbox it or ask.

## 3. Package updates run on the host, always with `--ignore-scripts`

Dependency resolution needs registry auth, proxy settings, lockfile writes, and
often the network. Run it on the host. Neutralise the dangerous part instead:
lifecycle scripts.

```sh
npm install  --ignore-scripts
npm update   --ignore-scripts
npm ci       --ignore-scripts
pnpm install --ignore-scripts
pnpm update  --ignore-scripts
yarn install --mode=skip-build          # Yarn Berry
yarn install --ignore-scripts           # Yarn Classic
bun install  --ignore-scripts
pip install  --only-binary :all: --no-build-isolation   # avoid setup.py execution
cargo fetch  --locked                   # resolution only; build.rs runs at build time
go mod download                         # then build in the sandbox
composer update --no-scripts --no-plugins
bundle lock --update                    # resolution only
```

Notes and follow-through:

- **`--ignore-scripts` is mandatory, not optional.** It is the difference between
  "downloaded a tarball" and "executed an unreviewed `postinstall` as your user".
- Prefer making it the persistent default so a forgotten flag cannot bite:
  `npm config set ignore-scripts true` (`ignore-scripts=true` in `~/.npmrc`);
  pnpm `onlyBuiltDependencies` in `pnpm-workspace.yaml` for an explicit allowlist.
- Packages that genuinely need a build step (native addons, `node-gyp`) get that
  step **run inside the sandbox afterwards**, e.g. `npm rebuild <pkg>` under
  `bwrap`, after you have read why it needs to compile.
- Follow the repository's version policy: query the authoritative registry for the
  current stable version, use the package manager's add/install command, and never
  hand-edit lockfiles.
- After a host-side install with scripts suppressed, treat `node_modules` (or the
  venv, or the module cache) as untrusted content: every subsequent command that
  executes it belongs in the sandbox.

## 4. Baseline invocation

Start from deny-all and add only what the command provably needs.

```sh
# Network remains unshared. --size must precede the --tmpfs it sizes.
bwrap \
  --unshare-all --unshare-user \
  --die-with-parent --new-session \
  --cap-drop ALL \
  --disable-userns --assert-userns-disabled \
  --clearenv \
  --setenv HOME /sandbox/home \
  --setenv PATH /usr/bin:/bin \
  --setenv TERM dumb \
  --setenv LANG C.UTF-8 \
  --proc /proc --dev /dev \
  --size 1073741824 --tmpfs /tmp \
  --ro-bind /usr /usr \
  --ro-bind-try /bin /bin \
  --ro-bind-try /lib /lib \
  --ro-bind-try /lib64 /lib64 \
  --ro-bind-try /sbin /sbin \
  --ro-bind /etc/ssl /etc/ssl \
  --ro-bind-try /etc/ca-certificates /etc/ca-certificates \
  --dir /sandbox/home \
  --ro-bind "$PWD" /workspace \
  --chdir /workspace \
  -- sh -c 'echo sandbox ready'
```

A ready-made wrapper implementing this with a small option surface lives beside
this file: `bwrap-run.sh`. Read it before using it, and prefer editing its
allowlists over adding ad-hoc binds at the call site.

Flag rationale:

- `--unshare-all` unshares user, IPC, PID, net, UTS, and cgroup namespaces.
  Re-add only `--share-net` when the task truly needs the network; a build that
  reaches the network unexpectedly is a finding, not an inconvenience.
- `--die-with-parent` prevents orphaned sandboxes surviving a cancelled run.
- `--new-session` allocates a new session so the payload cannot inject keystrokes
  into the controlling terminal via `TIOCSTI`. Omit it only for genuinely
  interactive commands, and then understand the risk.
- `--disable-userns --assert-userns-disabled` stops nested user namespaces being
  used to weaken the sandbox, and fails loudly if that cannot be enforced. It
  requires an explicit `--unshare-user` (`--unshare-all` only implies
  `--unshare-user-try`). Drop both flags if the payload legitimately nests
  sandboxes, and say that you did.
- `--clearenv` plus explicit `--setenv` is the only reliable way to keep tokens
  (`GITHUB_TOKEN`, `NPM_TOKEN`, `AWS_*`, `OP_*`) out of the sandbox.
- `--proc`/`--dev` provide minimal pseudo-filesystems; never `--dev-bind /dev`
  or `--dev-bind / /` "to make it work".

## 5. Additional controls

**Filesystem**

- Bind the single project directory, not `$HOME` and not `/`.
- Bind read-only by default; promote to `--bind` only the directories that must be
  written (build output, cache), ideally one at a time.
- Give the sandbox a throwaway `HOME` (`--dir` on a tmpfs), so tool config written
  by the payload never lands in the real home directory.
- Cap tmpfs growth with `--size` so a runaway job cannot exhaust memory.
- Explicitly keep out: `~/.ssh`, `~/.gnupg`, `~/.aws`, `~/.kube`, `~/.docker`,
  `~/.config/gh`, `~/.config/op`, `~/.netrc`, `~/.npmrc` and any other token file,
  `~/.local/share/chezmoi`, and the whole of `/etc` beyond the few files above.
- Never bind a container socket (`/var/run/docker.sock`,
  `/run/user/$(id -u)/podman/podman.sock`). Access to it is equivalent to root on
  the host.

**Process and runtime**

- Add `timeout <seconds>` around `bwrap` so a hung or spinning payload terminates.
- Constrain resources from the caller: `systemd-run --user --scope -p MemoryMax=… -p CPUQuota=…`
  or `ulimit -v/-u/-f` in the launching shell. bwrap itself does not set limits.
- Attach a seccomp filter with `--seccomp`/`--add-seccomp-fd` for high-risk
  payloads if a suitable BPF blob is available; otherwise say so rather than
  implying syscall filtering is in place.
- Keep the sandbox uid/gid as the invoking user (default). Do not chase root
  inside the namespace; it adds capability surface for no benefit.

**Network**

- Default to `--unshare-net`. If a build needs a registry, prefer priming the
  cache on the host (with `--ignore-scripts`) and running the build offline
  (`npm ci --offline`, `cargo build --offline`, `go build -mod=mod` with a warm
  module cache).
- There is no per-host filtering in bwrap: `--share-net` means full host network
  reachability, including localhost services and link-local metadata endpoints.
  Treat it as an explicit trust decision and state it.

**Hygiene**

- Never pass `--not-a-security-boundary`; it downgrades setup failures to warnings.
- Do not silently widen the sandbox to make a command pass. If a command needs
  more access, say what it needs and why, and get agreement.
- Report the effective network and mount permissions without printing environment
  values or payload arguments (which may contain secrets). The wrapper logs a
  redacted invocation; `--dry-run` does not print raw credentials.
- Verify the sandbox before trusting it, e.g.
  `bwrap … -- sh -c 'ls ~/.ssh'` should fail, and `ip addr` should show only
  loopback when the network is unshared.

## 6. If you exempt it, harden the runtime

Exempting container tooling from the sandbox moves the security boundary; it does
not remove the need for one. Without this section the exemption is the largest
hole in this skill, because `podman run -v /:/host` is a one-line full-host escape
from any bwrap policy.

**Prefer the `podman-containers` skill and its `podman-run.sh` wrapper**, which
applies everything below and refuses the dangerous flags. The section stays here
as the rationale and as the rule for any hand-written invocation.

**Required for any container that runs untrusted or unreviewed code:**

```sh
# Use a verified digest for IMAGE before running. Networking is disabled.
podman run --rm \
  --network=none \
  --read-only --tmpfs /tmp \
  --cap-drop=ALL \
  --security-opt no-new-privileges \
  --userns=keep-id \
  --pids-limit 512 --memory 2g \
  -v "$PWD:/workspace:ro" -w /workspace \
  -- "$IMAGE" true
```

- Prefer rootless Podman over a root daemon.
- Pin images by digest (`image@sha256:...`), not by mutable tag.
- Use `--userns=keep-id` for bind mounts. Under rootless Podman,
  `--user "$(id -u):$(id -g)"` maps the container UID through `/etc/subuid` to a
  different host UID, and the container then **cannot write the bind mount at
  all**. `keep-id` maps the container user onto the host UID, giving a non-root
  container process *and* correct file ownership.
- `podman run` does not inherit the host environment; pass variables explicitly
  with `--env` and never use `--env-host`.
- Add `:Z` to volume mounts only where SELinux is actually enabled.
- Mount the project read-only unless the task must write; then mount the single
  output directory read-write.
- Drop `--network=none` only when the task provably needs the network, and say so.

**Forbidden unless the user explicitly agrees, with the reason stated:**

- `--privileged` - equivalent to root on the host.
- `-v /:/host`, `-v $HOME:...`, or any mount of `~/.ssh`, `~/.gnupg`, `~/.aws`,
  `~/.config/gh`, `~/.npmrc`, `~/.local/share/chezmoi`.
- Mounting a container socket into a container (`/var/run/docker.sock`,
  `/run/user/$(id -u)/podman/podman.sock`) - container escape by design.
- `--userns=host`, `--pid=host`, `--ipc=host`.
- `--net=host` as a default (it exposes localhost services and metadata endpoints).
- `--cap-add`, `--security-opt seccomp=unconfined`, `--security-opt label=disable`,
  `--security-opt apparmor=unconfined`.
- `--device` for anything other than a device the task demonstrably needs.

The same rule as for bwrap applies: do not quietly widen the container to make a
command pass. Report the effective network and mount permissions, but redact
secret-bearing environment values and payload arguments.

For `DOCKER_HOST` discovery and Podman-specific troubleshooting, see the
`podman-containers` skill.

## 7. Troubleshooting

- `bwrap: No permissions to creating new namespace` - unprivileged user
  namespaces are restricted. Check `sysctl kernel.unprivileged_userns_clone` and
  `kernel.apparmor_restrict_unprivileged_userns` (Ubuntu 24.04+ blocks it by
  default and needs an AppArmor profile). Report the limitation; do not
  work around it with `sudo`.
- TLS failures inside the sandbox - the CA bundle was not bound; add the distro's
  certificate directory read-only.
- "command not found" - the interpreter or toolchain lives outside `/usr`
  (`~/.nvm`, `~/.cargo`, `~/.local/share/mise`). Bind that specific directory
  read-only rather than binding `$HOME`.
- Hostname/user lookups failing - bind `/etc/passwd` and `/etc/group` read-only,
  or set `--hostname sandbox` with `--unshare-uts`.

## 8. Pre-flight checklist

1. Which bucket is this? Class A/B/C or a hybrid dispatcher (§2) -> host, not
   sandbox. Dependency resolution -> host with `--ignore-scripts` (§3).
2. If it is exempt because it is container tooling, apply §6 to the runtime.
3. Does it need the network? If unsure, run with `--unshare-net` first.
4. What is the minimum writable set? Everything else read-only or absent.
5. `--clearenv` plus an explicit, secret-free environment allowlist.
6. No agent sockets, no credential directories, no container sockets.
7. `--die-with-parent`, `--new-session`, `--cap-drop ALL`, `--disable-userns`,
   `timeout`.
8. Record and report the exact invocation.
