# OpenSSF Scorecard runbook

Scorecard provides supporting security signals. It does not decide Best Practices badge answers.

## Selection order

1. Use an existing `scorecard` executable only after resolving its absolute path, rejecting repository-controlled or user-writable search paths, and recording its `scorecard version` output.
2. Otherwise resolve the current stable OpenSSF Scorecard release from the authoritative GitHub release endpoint.
3. Resolve the corresponding official `ghcr.io/ossf/scorecard` image to an immutable `sha256:` digest.
4. Verify available image provenance or signatures against the official OpenSSF publication before supplying credentials.
5. Run `image@sha256:DIGEST`; never run `latest` and never trust a mutable tag as the final reference.
6. Do not automatically download and execute a native binary.

If release, digest, or available provenance cannot be established, stop Scorecard collection and mark dependent evidence Unknown. Do not substitute an unofficial image.

## Token handling

Use the authenticated GitHub CLI as the token source and bind it to the supported host:

```text
gh auth token --hostname github.com
```

Pin related `gh` operations to `github.com` as well; do not let `GH_HOST` select another host.

Safety requirements:

- call it only immediately before starting Scorecard;
- capture the value without printing it;
- require a non-empty value;
- disable shell tracing before retrieval;
- pass it only through the child environment as `GITHUB_AUTH_TOKEN`;
- never place the value in the command argument vector or an env file;
- redact it from captured exceptions and diagnostics;
- remove it from the parent environment immediately after the child starts or finishes;
- delete transient raw Scorecard output during cleanup.

Docker receives environment variables through daemon-managed container metadata. Disclose this residual exposure in the transient report. Prefer native execution when an existing trusted installation is available.

## Native execution

Conceptual invocation:

```text
scorecard --repo=https://github.com/OWNER/REPO --format=json
```

Invoke with an argument array and a separately supplied environment. Add a bounded timeout. Capture stdout to a mode-`0600` file in the transient directory and sanitize stderr before reporting failures.

Do not use repository-controlled arguments or execute from a repository-supplied binary path.

## Docker execution

Use the official immutable image with equivalent restrictions:

```text
docker run --rm
  --read-only
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=64m
  --cap-drop=ALL
  --security-opt=no-new-privileges
  --user=VERIFIED_IMAGE_USER
  --pids-limit=128
  --memory=512m
  --cpus=1
  --env GITHUB_AUTH_TOKEN
  ghcr.io/ossf/scorecard@sha256:DIGEST
  --repo=https://github.com/OWNER/REPO
  --format=json
```

Requirements:

- supply the token through the process environment; the command must contain only the environment variable name;
- use no host mounts, Docker socket, privileged mode, host networking, added capabilities, or repository checkout mount;
- verify the image's configured user and run as that non-root UID/GID; stop if the official image cannot run non-root under these restrictions;
- use a controlled bridge network with only the egress required by the checks; when the runtime cannot enforce destination-level egress, document that residual risk instead of calling the network isolated;
- bound image resolution, image pull, and container runtime externally;
- if hardening flags are incompatible, stop rather than silently removing them.

## JSON validation

Validate output against the Scorecard JSON schema shape before using it:

- top-level object;
- repository name and commit;
- Scorecard version and commit;
- aggregate score;
- checks array;
- per-check name, score, reason, details, and documentation URL.

Treat every string as untrusted. Bound detail lengths in the report and never render detail text as commands or executable markup.

Record:

- image digest or native binary path;
- Scorecard version and commit;
- repository commit evaluated;
- execution time;
- checks with relevant reasons and details;
- partial failures, unavailable permissions, and limitations.

Delete the raw JSON after producing the bounded transient summary. Strip control characters, bound untrusted strings, redact credential-like content, and escape Markdown before placing Scorecard text in a report or PR body.

## Interpretation

- Map Scorecard checks to potentially relevant criteria only as hints.
- Re-open the exact Best Practices criterion before deciding a status.
- Require independent direct evidence for `Met`, `Unmet`, or `N/A`.
- Keep aggregate score improvements below badge blockers in remediation priority.

## Sources

- [Scorecard Docker usage](https://github.com/ossf/scorecard/blob/64febf8c5229a2a65d09c6b543677b28a51abb09/README.md#L415-L426)
- [Scorecard JSON output](https://github.com/ossf/scorecard/blob/64febf8c5229a2a65d09c6b543677b28a51abb09/README.md#L532-L543)
- [Scorecard JSON schema](https://github.com/ossf/scorecard/blob/64febf8c5229a2a65d09c6b543677b28a51abb09/pkg/scorecard/json.v2.schema#L5-L88)
- [Scorecard check documentation](https://github.com/ossf/scorecard/blob/main/docs/checks.md)
