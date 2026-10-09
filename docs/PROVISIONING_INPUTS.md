# Reviewed provisioning inputs

This inventory is the review record for externally resolved inputs managed by the home profile. It deliberately excludes distribution-managed APT packages. Sources below were checked on 2026-08-17.

## Baseline before this change

| Component | Observed state |
| --- | --- |
| Ansible | `ansible-core 2.19.4`; user collection path had `ansible.posix 2.2.0` and `community.general 13.0.0` |
| .NET | `~/.dotnet/dotnet --version` reported `10.0.103`; role selected the mutable `10.0` channel through `https://dot.net/v1/dotnet-install.sh` |
| Podman | `podman version 6.0.2`; the role fetched `default-policy.json` and `registries.conf` from `containers/image`'s mutable `main` branch |
| Neovim | `lazy-lock.json` was valid JSON (SHA-256 `95442aebc7c8f080fa57946707411890beef78f859e2844fc8051464f1f567da`); bootstrap cloned lazy.nvim's mutable `stable` tag |

## Reviewed inputs

| Component | Selected identity | Authoritative source | Integrity mechanism | Supported architectures / exception |
| --- | --- | --- | --- | --- |
| `ansible.posix` | `2.2.2` | [Galaxy release metadata](https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/ansible/posix/versions/2.2.2/) | Galaxy artifact SHA-256 `00a58c5d804c9adc99c3c3dc1b9f2246f4bb5f7337941440e0956f0e31c3b82b`; requires Ansible `>=2.16.0` | Compatible with repository Ansible 2.19.4 |
| `community.general` | `13.3.0` | [Galaxy release metadata](https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/index/community/general/versions/13.3.0/) | Galaxy artifact SHA-256 `46506254911a675da601abe0adce1bc5d00886ec9c6edb71e930244db7ed9f4d`; requires Ansible `>=2.18.0` | Compatible with repository Ansible 2.19.4 |
| mise | `v2026.9.1` | [Official GitHub release](https://github.com/jdx/mise/releases/tag/v2026.9.1) | GitHub release-asset `digest` values (SHA-256) enforced by Ansible `get_url` before installation | Linux `x86_64` (`mise-v2026.9.1-linux-x64`) and `aarch64` (`mise-v2026.9.1-linux-arm64`) only; all other architectures fail before download |
| .NET SDK | `10.0.400` | [Microsoft release metadata](https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/10.0/releases.json) | Publisher SHA-512 verified before extraction | Linux `x86_64` and `aarch64` only |
| .NET SDK Linux x64 | `dotnet-sdk-10.0.400-linux-x64.tar.gz` | Microsoft release metadata above | SHA-512 `1033977dd837150e0814cf0c5d5b17ceb63925fda7ba2158b47258a4bd7c048cf82eac3bc1166f3146f53124a3f5fba09db1de1260d2ce96399860303b404b48` | `x86_64` |
| .NET SDK Linux arm64 | `dotnet-sdk-10.0.400-linux-arm64.tar.gz` | Microsoft release metadata above | SHA-512 `a1b45da58e5591fff909a6126ac6bfc1ef9c12bc72c0625f7815e83a82be1a902317ee96926cbbf81324a45c6abf2ed8102a216d0507879cc166159af78d1b77` | `aarch64` |
| Podman container-image defaults | `containers/image` commit `08ce6b4207e7b151ea1c2830cdb1d4473cfd12aa` (annotated release tag `v5.36.0`) | [Official repository tag](https://github.com/containers/image/tree/v5.36.0) | Immutable full Git commit in HTTPS URL | The upstream project publishes no authoritative checksum for these individual raw files. The immutable commit and TLS are the documented integrity boundary. |
| Podman network-helper compatibility set | Podman `v6.1.1`, Netavark `v2.1.0`, Aardvark-DNS `v2.1.0` | [Podman v6.1.1 release](https://github.com/containers/podman/releases/tag/v6.1.1), [Netavark v2.1.0 release](https://github.com/containers/netavark/releases/tag/v2.1.0), and [Aardvark-DNS v2.1.0 release](https://github.com/containers/aardvark-dns/releases/tag/v2.1.0) | Podman 6 requires the 2.x network stack. Netavark and Aardvark-DNS use matching `2.1` major-minor releases. | This reviewed artifact pair is Linux `x86_64` only. Unsupported architectures fail before download. |
| Netavark helper | `netavark.gz` from `v2.1.0` | [Official immutable release asset](https://github.com/containers/netavark/releases/download/v2.1.0/netavark.gz) | Publisher SHA-256 `39fb540daf7578a793510b27b592b10f17b5d9aa3b07bc5c3f40881f12d590bd`, verified before decompression and installation | Linux `x86_64` only |
| Aardvark-DNS helper | `aardvark-dns.gz` from `v2.1.0` | [Official immutable release asset](https://github.com/containers/aardvark-dns/releases/download/v2.1.0/aardvark-dns.gz) | Publisher SHA-256 `a7bc5252ee0e083f3f46d5bb9dc5f0abdbaa31a70a5a19012412dc8055ac2976`, verified before decompression and installation | Linux `x86_64` only |
| lazy.nvim bootstrap | `85c7ff3711b730b4030d03144f6db6375044ae82` (the reviewed `stable` tag target) | [Official repository commit](https://github.com/folke/lazy.nvim/commit/85c7ff3711b730b4030d03144f6db6375044ae82) | Immutable full Git commit; clone then detached checkout | No publisher archive checksum applies to this Git source. |
| CopilotChat.nvim | `451d365928a994cda3505a84905303f790e28df8` | [Official repository commit](https://github.com/CopilotC-Nvim/CopilotChat.nvim/commit/451d365928a994cda3505a84905303f790e28df8) | Immutable full Git commit in declaration and lockfile | Git-source exception; no publisher archive checksum. |
| nvim-treesitter | `074aa4422bf029908338e855d0c0f71470a971bb` | [Official repository commit](https://github.com/nvim-treesitter/nvim-treesitter/commit/074aa4422bf029908338e855d0c0f71470a971bb) | Immutable full Git commit in declaration and lockfile | Git-source exception; no publisher archive checksum. |
| telescope.nvim | `a0bbec21143c7bc5f8bb02e0005fa0b982edc026` (tag `0.1.8`) | [Official repository commit](https://github.com/nvim-telescope/telescope.nvim/commit/a0bbec21143c7bc5f8bb02e0005fa0b982edc026) | Immutable full Git commit in declaration and lockfile | Git-source exception; no publisher archive checksum. |
| neo-tree.nvim | `ebd66767191714e008ce73b769518a763ff31bdc` | [Official repository commit](https://github.com/nvim-neo-tree/neo-tree.nvim/commit/ebd66767191714e008ce73b769518a763ff31bdc) | Immutable full Git commit in declaration and lockfile | Git-source exception; no publisher archive checksum. |

The Galaxy metadata and Microsoft release manifest are publisher-controlled records. The Git identities were resolved directly from each publisher's official repository immediately before this change. No checksum is invented where the upstream publisher does not provide one.

## Podman helper migration safety

On the reviewed Debian host, `apt-cache rdepends --installed` showed only the mutual `netavark`/`aardvark-dns` relationship (and the non-installed `golang-github-containers-common`) for these helper packages. The role therefore installs and validates the compatible `/usr/local/libexec/podman` helpers before removing the distribution packages. It never invokes `podman system reset` and does not delete Podman storage; a helper integrity or version failure leaves the prior managed helper untouched and stops the role before package removal.
