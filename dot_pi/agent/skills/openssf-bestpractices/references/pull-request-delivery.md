# Pull request delivery

The pull request is the review boundary. In `pull-request` mode, create it automatically after evidence collection and validation succeed; do not add a separate pre-PR approval step. In `audit-only` mode, do not create a branch, commit, push, or pull request.

## Preconditions

- `origin` is the validated `github.com` repository.
- `gh auth status` succeeds.
- The default branch is known from GitHub.
- The worktree was clean at the start.
- The starting `HEAD` equals the fetched `origin/<default-branch>`.
- The answer file passes the bundled validator.
- Every changed path is allowed.

## Allowed paths

Always allowed:

```text
.bestpractices.json
.project.d/bestpractices.json
```

Documentation is allowed only after explicit opt-in and only when factual:

- exact root basenames `README`, `SECURITY`, `CONTRIBUTING`, `GOVERNANCE`, and `SUPPORT`, optionally followed by `.md`, `.markdown`, `.rst`, `.adoc`, or `.txt`;
- regular files below a real, non-symlinked `docs/` directory with extensions `.md`, `.markdown`, `.rst`, `.adoc`, or `.txt`;
- OpenSpec proposal artifacts only when the user separately requested OpenSpec creation.

Reject symlinks, staged symlink modes, hardlinks, special files, deceptive names such as `README.py`, and documentation paths whose resolved location leaves the repository.

Do not modify source files, source comments, tests, workflows, build files, configuration, dependency manifests, lockfiles, generated files, or GitHub settings.

When path classification is uncertain, stop and report it as a proposed remediation instead of staging it.

## Branch

Use a collision-resistant, descriptive branch name, for example:

```text
chore/openssf-best-practices-silver
chore/openssf-best-practices-silver-2
```

Create it from the already-verified starting commit. Do not force-reset or rewrite another branch.

## Staging checks

Stage explicit paths only:

```text
git add -- <answer-file> <explicit-documentation-paths...>
```

Never use `git add .` or `git add -A`.

Before committing, inspect:

- staged path names;
- staged diff statistics;
- full staged diff;
- credential and private-URL scan;
- control-character stripping, length bounds, and Markdown escaping for untrusted report or PR text;
- validator result against the frozen snapshots.

Reject any staged deletion or path outside the approved set unless it is the deliberate removal of the unused duplicate BadgeApp answer file after explicit user direction.

## Commit

Use a factual message, for example:

```text
chore: update OpenSSF best practices evidence
```

The commit body may name the target tier and validation command. Do not claim the badge has been awarded.

## Push

Push only the new branch:

```text
git push --set-upstream origin <branch>
```

Never force-push. If branch protection or authorization prevents pushing, leave the local branch intact and report the failure.

## Pull request

Create a temporary mode-`0600` body file outside the repository and use `gh pr create --body-file`. Do not interpolate repository or API text into a shell command. Treat repository, API, and Scorecard strings as plain text: strip control characters, enforce field limits, redact credential-like values, and escape Markdown metacharacters before inserting them.

Suggested title:

```text
chore: update OpenSSF Best Practices evidence for <target>
```

Required body sections:

```markdown
## Summary

## Badge target

## Known answers updated

## Existing answers incorporated

## Documentation updates

## Unknown and unmet criteria

## Scorecard context

## Validation

## Follow-up
```

State explicitly:

- Scorecard is supporting evidence only;
- Unknown criteria were omitted from the selected BadgeApp answer file;
- no application code, workflow, dependency, or repository setting changed;
- whether `/opsx-propose improve-<repo>-<target>-best-practices` is recommended.

After creation, return the PR URL, branch, commit SHA, changed paths, validator result, and residual Unknown/Unmet counts. If no known answer or allowed documentation change exists, create no empty commit or PR; return the transient remediation report instead.

## Failure handling

- Commit failure: leave unstaged/staged changes intact and report the command that failed.
- Push failure: leave the local commit and branch intact; do not force or alter remotes.
- PR failure: leave the pushed branch intact and provide a safe `gh pr create --head <branch> --base <default>` recovery outline.
- Never expose raw authentication errors if they may contain credentials.
