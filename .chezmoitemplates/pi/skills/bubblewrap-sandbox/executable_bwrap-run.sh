#!/usr/bin/env bash
# Minimal deny-by-default Bubblewrap wrapper.
#
# Usage: bwrap-run.sh [options] -- COMMAND [ARGS...]
#
#   --net                  Allow network access (default: network unshared)
#   --rw PATH              Bind PATH read-write inside the sandbox (repeatable)
#   --ro PATH              Bind PATH read-only inside the sandbox (repeatable)
#   --env NAME[=VALUE]     Pass an environment variable through (repeatable).
#                          Refuses obvious secret names.
#   --timeout SECONDS      Kill the sandbox after SECONDS (default: 900)
#   --dry-run              Print a redacted invocation instead of running it
#
# Never use this for host-identity tools (git, gpg, ssh, gh, chezmoi, sudo),
# privileged-delegation clients (docker, kubectl, systemctl), or nested-isolation
# launchers (podman, buildah, bwrap). See SKILL.md sections 2 and 6.
set -euo pipefail

die() { printf 'bwrap-run: %s\n' "$*" >&2; exit 2; }

command -v bwrap >/dev/null || die "bwrap not found"

net=0
timeout_secs=900
dry_run=0
rw_paths=()
ro_paths=()
env_names=()

while [ $# -gt 0 ]; do
  case "$1" in
    --net) net=1; shift ;;
    --rw) [ $# -ge 2 ] || die "--rw needs a path"; rw_paths+=("$2"); shift 2 ;;
    --ro) [ $# -ge 2 ] || die "--ro needs a path"; ro_paths+=("$2"); shift 2 ;;
    --env) [ $# -ge 2 ] || die "--env needs a name"; env_names+=("$2"); shift 2 ;;
    --timeout) [ $# -ge 2 ] || die "--timeout needs seconds"; timeout_secs="$2"; shift 2 ;;
    --dry-run) dry_run=1; shift ;;
    --) shift; break ;;
    *) die "unknown option: $1" ;;
  esac
done

[ $# -gt 0 ] || die "no command given"
[[ "$timeout_secs" =~ ^[1-9][0-9]*$ ]] || die "--timeout must be a positive number of seconds"

case "${1##*/}" in
  # Class A - host-identity tools: need credentials that would defeat the sandbox
  git|pre-commit|gpg|gpg2|ssh|ssh-add|scp|sudo|chezmoi|gh|op)
    die "refusing to sandbox '$1' - host-identity tool, run it on the host (SKILL.md 2.1)" ;;
  # Class B - privileged-delegation clients: sandbox contains the client, not the effect
  docker|kubectl|helm|systemctl|flatpak)
    die "refusing to sandbox '$1' - privileged-delegation client (docker may also be a Podman shim); harden the runtime instead (SKILL.md 2.2, 2.3, 6)" ;;
  # Class C - nested-isolation launchers: would need userns/newuidmap/fuse back
  podman|buildah|nerdctl|bwrap)
    die "refusing to sandbox '$1' - nested-isolation launcher; harden the runtime instead (SKILL.md 2.3, 6)" ;;
  # Hybrid dispatchers: correct to sandbox for local contexts, will fail for container contexts
  eirctl|taskctl|make|just|act|earthly|devcontainer)
    printf 'bwrap-run: warning: %s is a task dispatcher; this sandbox only suits local/shell contexts. Container-backed contexts must run on the host (SKILL.md 2.4).\n' "${1##*/}" >&2 ;;
esac

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
  # A read-only mount of a Unix socket still permits sending requests to it.
  [ ! -S "$abs" ] || die "refusing to mount a Unix socket: $abs"
  if [ -d "$abs" ]; then
    local sockets
    sockets="$(find "$abs" -type s -print -quit)" || die "cannot inspect mount for sockets: $abs"
    [ -z "$sockets" ] || die "refusing to mount a directory containing Unix sockets: $abs"
  fi
}

safe_mount "$workdir"

args=(
  --unshare-all
  --unshare-user
  --die-with-parent
  --new-session
  --cap-drop ALL
  --disable-userns
  --assert-userns-disabled
  --clearenv
  --setenv HOME /sandbox/home
  --setenv PATH /usr/local/bin:/usr/bin:/bin
  --setenv TMPDIR /tmp
  --setenv LANG C.UTF-8
  --setenv TERM dumb
  --proc /proc
  --dev /dev
  --size 1073741824 --tmpfs /tmp
  --ro-bind /usr /usr
  --ro-bind-try /bin /bin
  --ro-bind-try /sbin /sbin
  --ro-bind-try /lib /lib
  --ro-bind-try /lib64 /lib64
  --ro-bind-try /etc/ssl /etc/ssl
  --ro-bind-try /etc/ca-certificates /etc/ca-certificates
  --ro-bind-try /etc/pki /etc/pki
  --ro-bind-try /etc/passwd /etc/passwd
  --ro-bind-try /etc/group /etc/group
  --dir /sandbox/home
)

if [ "$net" -eq 1 ]; then
  args+=(--share-net --ro-bind-try /etc/resolv.conf /etc/resolv.conf)
fi

# Bind the project first. More specific writable mounts are applied afterward;
# explicit read-only mounts come last so they cannot be masked by a writable parent.
args+=(--ro-bind "$workdir" "$workdir")
mounted=("$workdir")
for p in "${rw_paths[@]}"; do
  [ -e "$p" ] || die "no such path: $p"
  abs="$(realpath -- "$p")"
  safe_mount "$abs"
  for target in "${mounted[@]}"; do
    [ "$abs" != "$target" ] || die "duplicate mount destination (use a writable child, not the workdir): $abs"
  done
  mounted+=("$abs")
  args+=(--bind "$abs" "$abs")
done
for p in "${ro_paths[@]}"; do
  [ -e "$p" ] || die "no such path: $p"
  abs="$(realpath -- "$p")"
  safe_mount "$abs"
  for target in "${mounted[@]}"; do
    [ "$abs" != "$target" ] || die "duplicate mount destination: $abs"
  done
  mounted+=("$abs")
  args+=(--ro-bind "$abs" "$abs")
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
    args+=(--setenv "$key" "${!key-}")
  else
    args+=(--setenv "$key" "${name#*=}")
  fi
done

args+=(--chdir "$workdir" --)
printf 'bwrap-run: network=%s ro=%d rw=%d env=%d; command and values redacted\n' "$net" "${#ro_paths[@]}" "${#rw_paths[@]}" "${#env_names[@]}" >&2
[ "$dry_run" -eq 1 ] && exit 0

exec timeout --signal=TERM --kill-after=10s "$timeout_secs" bwrap "${args[@]}" "$@"
