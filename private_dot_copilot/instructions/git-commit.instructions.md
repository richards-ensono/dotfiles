---
applyTo: "**"
description: This file describes how to write commit and use GPG messages for the project.
---

# Git Commit Messages

Git commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This means that commit messages should be structured as follows:

```text
type(scope): subject

extended description (optional)
```

Where:

```text
type: The type of change (e.g., feat, fix, docs, style, refactor, test, chore).
scope: An optional scope that provides additional context about the change (e.g., component, module, etc.).
subject: A brief description of the change.
extended description: An optional, more detailed description of the change, which can include motivation, context, and any relevant information.
```

> [!IMPORTANT]
> If the commit fixes a vulnerability then this should be specified as text in the extended description and the commit message should include the text "fixes #<issue number>" to link the commit to the issue or "fixes <CVE identifier>" to link the commit to a specific CVE or GHSA.

# GPG Signatures

All commits must be signed with a GPG key to ensure the authenticity and integrity of the commit history. To sign a commit, use the `-S` or `--gpg-sign` option with the `git commit` command:

```sh
git commit -S -m "type(scope): subject"
```

Make sure to configure your GPG key in Git before signing commits:

```sh
git config --global user.signingkey <your-gpg-key-id>
```

> [!IMPORTANT]
> If the signing key is not configured then stop the current conversation and ask the user to configure their GPG key before proceeding with any commits.

## Handling GPG Signature Errors

If you encounter errors related to GPG signatures, ensure that your GPG key is properly configured and that you have the necessary permissions to use it. Retry the signing process once after resolving any issues with your GPG key. If the problem persists, stop the conversation and notify the user to check their GPG configuration and permissions before attempting to commit again.

> [!IMPORTANT]
> Under no circumstances should you attempt to bypass GPG signature requirements or suggest any workarounds that compromise the security of the commit history. Always encourage users to resolve GPG issues properly to maintain the integrity of the project.
