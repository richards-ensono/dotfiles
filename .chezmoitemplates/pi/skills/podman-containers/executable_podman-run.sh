#!/usr/bin/env bash
# Hardened rootless Podman runner for untrusted or unreviewed workloads.
#
# Usage: podman-run.sh [options] -- IMAGE [COMMAND...]
#
#   --rw PATH          Bind PATH read-write (repeatable). Refuses sensitive paths.
#   --ro PATH          Bind PATH read-only (repeatable).
#   --net MODE         none (default) | private | host (host is refused)
#   --env NAME[=VALUE] Pass one variable in (repeatable). Refuses secret-ish names.
#   --memory SIZE      Memory cap (default 2g)
#   --pids-limit N     Pid cap (default 512)
#   --timeout SECONDS  Kill the container after SECONDS (default 900)
#   --allow-tag        Permit a non-digest-pinned image reference
#   --as-root          Run as root inside the container (still rootless on host)
#   --dry-run          Print a redacted invocation instead of running it
#
# Defaults: --rm --read-only --tmpfs /tmp --cap-drop=ALL
#           --security-opt no-new-privileges --userns=keep-id --network=none
#           $PWD mounted read-only at /workspace
#
# The container runtime is the security boundary here; do not also wrap this in
# bwrap. See the bubblewrap-sandbox skill, sections 2.3 and 6.
set -euo pipefail

die() { printf 'podman-run: %s\n' "$*" >&2; exit 2; }

command -v podman >/dev/null || die "podman not found"

net=none
memory=2g
pids_limit=512
timeout_secs=900
allow_tag=0
as_root=0
dry_run=0
rw_paths=()
ro_paths=()
env_names=()

while [ $# -gt 0 ]; do
  case "$1" in
    --rw) [ $# -ge 2 ] || die "--rw needs a path"; rw_paths+=("$2"); shift 2 ;;
    --ro) [ $# -ge 2 ] || die "--ro needs a path"; ro_paths+=("$2"); shift 2 ;;
    --net) [ $# -ge 2 ] || die "--net needs a mode"; net="$2"; shift 2 ;;
    --env) [ $# -ge 2 ] || die "--env needs a name"; env_names+=("$2"); shift 2 ;;
    --memory) [ $# -ge 2 ] || die "--memory needs a size"; memory="$2"; shift 2 ;;
    --pids-limit) [ $# -ge 2 ] || die "--pids-limit needs a count"; pids_limit="$2"; shift 2 ;;
    --timeout) [ $# -ge 2 ] || die "--timeout needs seconds"; timeout_secs="$2"; shift 2 ;;
    --allow-tag) allow_tag=1; shift ;;
    --as-root) as_root=1; shift ;;
    --dry-run) dry_run=1; shift ;;
    --) shift; break ;;
    *) die "unknown option: $1" ;;
  esac
done

[ $# -gt 0 ] || die "no image given"
image="$1"; shift
[[ "$timeout_secs" =~ ^[1-9][0-9]*$ ]] || die "--timeout must be a positive number of seconds"
[[ "$pids_limit" =~ ^[1-9][0-9]*$ ]] || die "--pids-limit must be positive"
[[ "$memory" =~ ^[1-9][0-9]*[kKmMgG]?$ ]] || die "--memory must be a positive size"

# IMAGE must not be interpreted as another podman run option. Constrain the
# reference even with --allow-tag (which only relaxes digest pinning).
[[ "$image" =~ ^[A-Za-z0-9][A-Za-z0-9._:/-]*(@sha256:[[:xdigit:]]{64})?$ ]] || die "invalid image reference"

case "$net" in
  none|private) ;;
  host) die "--net host is refused: it exposes host loopback services and metadata endpoints. Use 'private' and state why the network is needed." ;;
  *) die "--net must be none, private, or host" ;;
esac

if [ "$allow_tag" -eq 0 ] && [[ ! "$image" =~ @sha256:[[:xdigit:]]{64}$ ]]; then
  die "image is not digest-pinned; resolve it with podman image inspect or explicitly pass --allow-tag"
fi

# Never silently use a rootful Podman connection for untrusted workloads.
[ "$(podman info --format '{{.Host.Security.Rootless}}')" = true ] || die "rootless Podman is required"
# SELinux relabelling is meaningful only where SELinux is enforcing.
relabel=""
if [ "$(podman info --format '{{.Host.Security.SELinuxEnabled}}')" = true ]; then
  relabel=",Z"
fi

args=(
  run --rm
  --read-only
  --tmpfs /tmp
  --cap-drop=ALL
  --security-opt no-new-privileges
  --pids-limit "$pids_limit"
  --memory "$memory"
  "--network=$net"
)

# Rootless Podman: --user $(id -u) maps to a SUBUID and cannot write bind mounts.
# keep-id maps the container user to the host uid, which is what bind mounts need.
if [ "$as_root" -eq 1 ]; then
  printf 'podman-run: warning: running as root inside the container; capability surface is larger.\n' >&2
else
  args+=("--userns=keep-id")
fi

workdir="$(pwd -P)"
home="$(realpath -- "$HOME")"

safe_mount() {
  local abs="$1"
  case "$home" in
    "$abs"/*) die "refusing to mount a parent of the home directory: $abs" ;;
  esac
  local protected
  for protected in "$home"/{.ssh,.gnupg,.aws,.kube,.docker,.npmrc,.netrc,.config/gh,.config/op,.local/share/chezmoi,.pi/agent}; do
    case "$protected" in
      "$abs"/*) die "refusing to mount a parent of a credential path: $abs" ;;
    esac
  done
  case "$abs" in
    /|/etc|/etc/*|/proc|/proc/*|/sys|/sys/*|/dev|/dev/*|/run|/run/*|/var|/var/*)
      die "refusing to mount system path: $abs" ;;
    "$home"|"$home"/.local/share/chezmoi|"$home"/.local/share/chezmoi/*|"$home"/.pi/agent|"$home"/.pi/agent/*)
      die "refusing to mount private home path: $abs" ;;
    */.ssh|*/.ssh/*|*/.gnupg|*/.gnupg/*|*/.aws|*/.aws/*|*/.kube|*/.kube/*|*/.docker|*/.docker/*|*/.config/gh|*/.config/gh/*|*/.config/op|*/.config/op/*|*/.npmrc|*/.netrc|*/.env|*/.env.*)
      die "refusing to mount credential path: $abs" ;;
  esac
  [ ! -S "$abs" ] || die "refusing to mount a Unix socket: $abs"
  if [ -d "$abs" ]; then
    local sockets
    sockets="$(find "$abs" -type s -print -quit)" || die "cannot inspect mount for sockets: $abs"
    [ -z "$sockets" ] || die "refusing to mount a directory containing Unix sockets: $abs"
  fi
  case "$abs" in
    *:*) die "cannot represent a colon in a Podman volume path: $abs" ;;
  esac
}

mount_destination() {
  case "$1" in
    "$workdir") printf '/workspace' ;;
    "$workdir"/*) printf '/workspace/%s' "${1#"$workdir"/}" ;;
    *) printf '%s' "$1" ;;
  esac
}

safe_mount "$workdir"
args+=(-v "$workdir:/workspace:ro$relabel")
mounted=(/workspace)
for p in "${rw_paths[@]}"; do
  [ -e "$p" ] || die "no such path: $p"
  abs="$(realpath -- "$p")"
  safe_mount "$abs"
  dest="$(mount_destination "$abs")"
  for target in "${mounted[@]}"; do
    [ "$dest" != "$target" ] || die "duplicate mount destination (use a writable child, not the workdir): $dest"
  done
  mounted+=("$dest")
  args+=(-v "$abs:$dest:rw$relabel")
done
for p in "${ro_paths[@]}"; do
  [ -e "$p" ] || die "no such path: $p"
  abs="$(realpath -- "$p")"
  safe_mount "$abs"
  dest="$(mount_destination "$abs")"
  for target in "${mounted[@]}"; do
    [ "$dest" != "$target" ] || die "duplicate mount destination: $dest"
  done
  mounted+=("$dest")
  args+=(-v "$abs:$dest:ro$relabel")
done

for name in "${env_names[@]}"; do
  key="${name%%=*}"
  [[ "$key" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]] || die "invalid environment variable name: $key"
  upper="${key^^}"
  case "$upper" in
    *TOKEN*|*SECRET*|*PASSWORD*|*KEY*|*CREDENTIAL*|*AUTH*|GPG_*|AWS_*|OP_*|GH_*|GITHUB_*|NPM_*)
      die "refusing to forward possible secret: $key" ;;
  esac
  if [ "$name" = "$key" ]; then
    args+=(--env "$key=${!key-}")
  else
    args+=(--env "$name")
  fi
done

args+=(-w /workspace -- "$image")
printf 'podman-run: network=%s ro=%d rw=%d env=%d; command and values redacted\n' "$net" "${#ro_paths[@]}" "${#rw_paths[@]}" "${#env_names[@]}" >&2
[ "$dry_run" -eq 1 ] && exit 0

exec timeout --signal=TERM --kill-after=10s "$timeout_secs" podman "${args[@]}" "$@"
