# Transient report template

Do not write this report into the audited repository by default.

```markdown
# OpenSSF Best Practices audit

## Project

- Repository: `github.com/OWNER/REPO`
- Best Practices project: `PROJECT_ID`
- Current badge: CURRENT
- Target badge: TARGET
- Repository commit: `FULL_SHA`
- Project snapshot: `SHA256` retrieved at `TIME`
- Criteria snapshots: `TIER=SHA256` entries retrieved at `TIME`
- Scorecard: VERSION, COMMIT, or unavailable with reason

## Summary

- Known criteria emitted: N
- Existing known answers incorporated: N
- Known answers changed from existing: N
- Unmet badge blockers: N
- Unknown criteria: N
- Documentation files proposed: N

## Known answers

| Criterion | Status | Evidence | Source | Notes |
|---|---|---|---|---|

## Existing answers incorporated

| Criterion | Status | Current corroboration | Notes |
|---|---|---|---|

Mark uncorroborated inherited answers clearly. Incorporation is not fresh verification.

## Unmet criteria

| Priority | Criterion | Strength | Evidence | Smallest remediation |
|---:|---|---|---|---|

## Unknown criteria

| Priority | Criterion | Why unknown | Recommended verification or remediation | OpenSpec? |
|---:|---|---|---|---|

Every row needs a concrete next step. Do not use generic text such as “investigate.”

## Scorecard context

| Check | Score | Relevant signal | Limitation | Candidate criterion |
|---|---:|---|---|---|

State: “Scorecard is supporting evidence only and did not directly determine badge statuses.”

## Documentation-only changes

- `PATH`: factual change and supporting evidence

If none, say so. Confirm that no policy or commitment was invented.

## Generated answer file

- Path: `PATH`
- Validator: PASS/FAIL
- Known statuses: N
- Justifications: N
- Existing invalid or unknown entries omitted: N

## Pull request

- Branch: `BRANCH`
- Commit: `SHA`
- URL: `PR_URL`
- Changed paths: `PATHS`

## Follow-up

Recommended command, when broader remediation is warranted:

`/opsx-propose improve-REPO-TARGET-best-practices`

Suggested proposal:

> DESCRIPTION DERIVED FROM THE UNKNOWN AND UNMET CRITERIA.

## Limitations

- Permissions or inaccessible settings
- Human attestations still required
- Private evidence intentionally excluded
- Scorecard or API partial failures
```
