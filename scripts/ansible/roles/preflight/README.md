# Ansible Role: Preflight

This role performs lightweight validation before the rest of the playbook runs.

## Checks

- Supported OS family
- Expected package manager
- Required commands on `PATH`
- Minimum free disk space for local source builds

## Variables

```yaml
preflight_supported_os_families:
  - Debian

preflight_required_package_manager: apt

preflight_required_commands:
  - git
  - curl
  - python3

preflight_disk_check_path: /tmp
preflight_min_disk_kb: 2097152
```

## Notes

Keep role-local assumptions aligned with this shared baseline instead of duplicating ad hoc checks across install roles.
