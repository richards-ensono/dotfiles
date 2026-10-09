#!/usr/bin/env bash
# Validation-only installer. Digests verified against v2.73.0 release metadata.
set -euo pipefail

version=2.73.0
case "$(uname -s)" in
  Linux)
    asset="chezmoi_${version}_linux_amd64.tar.gz"
    checksum=b597729b687af4488a848240134cb633de8ca0f04e0d26d48f400ee2ac338ffa
    executable=chezmoi
    ;;
  MINGW*|MSYS*)
    asset="chezmoi_${version}_windows_amd64.zip"
    checksum=266938399108028a5b6dc7a137026e3ead747304122e5fe381d5396e496620f6
    executable=chezmoi.exe
    ;;
  *) echo "Unsupported validation platform" >&2; exit 1 ;;
esac

stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
curl --fail --location --silent --show-error \
  "https://github.com/twpayne/chezmoi/releases/download/v${version}/${asset}" \
  --output "$stage/$asset"
printf '%s  %s\n' "$checksum" "$stage/$asset" | sha256sum --check --strict
if [ "$executable" = chezmoi.exe ]; then
  unzip -q "$stage/$asset" "$executable" -d "$stage"
else
  tar -xzf "$stage/$asset" -C "$stage" "$executable"
fi
install_dir="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/dotfiles-validation-bin"
if [ "$executable" = chezmoi.exe ]; then
  install_dir="$(cygpath -u "$install_dir")"
fi
mkdir -p "$install_dir"
install -m 0755 "$stage/$executable" "$install_dir/$executable"
if [ -n "${GITHUB_PATH:-}" ]; then
  path_entry="$install_dir"
  if [ "$executable" = chezmoi.exe ]; then
    path_entry="$(cygpath -m "$install_dir")"
  fi
  printf '%s\n' "$path_entry" >> "$GITHUB_PATH"
fi
printf 'Installed verified Chezmoi %s in %s\n' "$version" "$install_dir"
