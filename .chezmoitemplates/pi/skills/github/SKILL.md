---
name: github
description: Use the GitHub CLI (`gh`) for all GitHub queries and operations, including repositories, issues, pull requests, Actions, releases, and GitHub API requests. Verify the intended host and effective account before access; switch accounts and request only necessary OAuth scopes when needed.
license: MIT
compatibility: Requires GitHub CLI (`gh`) and authentication to the target GitHub host.
metadata:
  author: rslater
  version: "1.0"
---

# GitHub via `gh`

Use `gh` for **every operation that queries or changes GitHub**. Prefer built-in
commands (`gh repo`, `gh issue`, `gh pr`, `gh run`, `gh release`, `gh search`,
etc.); use `gh api` for unsupported REST or GraphQL queries. Do not use a
browser, web search/fetch tools, `curl`, or direct HTTP clients to read GitHub
pages or APIs. A browser opened by `gh auth login` or `gh auth refresh` solely
for *authentication/authorization* is the exception, not a way to query GitHub.
Do not use `--web` variants of `gh` commands for queries.

## Before accessing GitHub

1. Determine the target **host** and **repository** from the user's request,
   local git remotes, or an explicit GitHub URL. Do not assume that the owner
   of an organization repository is the user's login. If the intended account
   is not clear from the request or available context, **ask the user which
   account to use**, especially before a write or a private-resource query.
   Do not infer it just because one account is currently active.
2. Check `gh auth status --hostname HOST` for configured accounts and the
   active one. Check whether `GH_TOKEN`, `GITHUB_TOKEN`,
   `GH_ENTERPRISE_TOKEN`, `GITHUB_ENTERPRISE_TOKEN`, `GH_HOST`, or `GH_REPO`
   are **set**; never print their values if they could contain credentials.
   Token environment variables override stored `gh` credentials, so switching
   accounts may not change which identity actually makes API calls.
3. If the intended login is stored but inactive, run
   `gh auth switch --hostname HOST --user LOGIN` (`gh auth switch`, not
   `gh switch`). If it is not configured, ask the user to authenticate that
   account with `gh auth login --hostname HOST`; do not silently choose a
   different account. If an environment token is overriding the selected
   account, resolve that override with the user (or use a credential-free
   command environment) before proceeding. Never display, copy, or persist
   token values to work around this.
4. **Verify the effective identity after switching** with
   `gh api --hostname HOST user --jq .login` and compare it with the intended
   login. If it differs, or authentication fails, stop and resolve it before
   reading private data or writing anything. Repeat the check when the host,
   account, or token environment changes. For repository commands, explicitly
   target `HOST/OWNER/REPO` with `--repo` where supported; for `gh api`, use
   `--hostname HOST` and an explicit endpoint. Do not rely on an unrelated
   working-directory remote or `GH_REPO` override.

Run `gh` on the host, not inside a sandbox that would need access to credentials.
Never expose access tokens or use `gh auth token`, `gh auth status --show-token`,
`gh api --verbose`, or other commands that print credential material.

## If an operation needs more access

First check the actual failure and the account/host. A 404 can mean the wrong
repository or a lack of access; it is not automatically a missing scope.
Inspect `gh auth status --hostname HOST` for the active account's scopes. For
an OAuth token managed by `gh`, identify the **minimum** additional scope
required by the specific API/action (check `gh <command> --help` and the
GitHub API's permission requirements using `gh` where available). Tell the
user **the exact scope, why this operation needs it, and what access it grants**;
get approval before expanding permissions. For example, managing Actions
workflows may require `workflow` (to modify workflow files); do not request it
for simply listing runs.

For an approved scope, while the correct account is active:

```sh
gh auth switch --hostname HOST --user LOGIN  # only if needed
gh auth refresh --hostname HOST --scopes SCOPE
gh api --hostname HOST user --jq .login      # verify again afterward
```

`gh auth refresh` opens GitHub's authorization flow; the user completes it.
If another account was active before a temporary switch, restore that account
with `gh auth switch --hostname HOST --user PREVIOUS_LOGIN` afterward (but
verify the intended account again before any further GitHub work).

For `GH_TOKEN`/`GITHUB_TOKEN` or enterprise token environment variables,
`gh auth refresh` **cannot expand that token**. Explain the exact fine-grained
token repository/organization permission (or classic PAT OAuth scope), why it
is needed, and the affected resources. Ask the user to edit or replace their
token in GitHub's **Settings → Developer settings → Personal access tokens**
and update the environment token through their trusted credential process;
do not ask them to paste secrets into chat or edit credentials yourself. This
settings interaction is for authorization only, not for querying GitHub. Org
SSO authorization and repository access may also be required independently of
scopes. If permission is denied or approval is not given, report the blocker;
do not try a browser or another identity to bypass it.
