# BadgeApp contract

Use this reference when freezing project data, classifying criteria, generating rules, merging an existing answer file, or validating `.bestpractices.json`.

## Authoritative inputs

For numeric project `PROJECT_ID` and target tier `TIER`, fetch the project record and every criteria page from Passing through `TIER`:

```text
https://www.bestpractices.dev/en/projects/PROJECT_ID.json
https://www.bestpractices.dev/en/criteria/0?details=true&rationale=true
https://www.bestpractices.dev/en/criteria/1?details=true&rationale=true
https://www.bestpractices.dev/en/criteria/2?details=true&rationale=true
```

Fetch only the tier URLs at or below the target. A Gold maintenance audit uses all three.

Tier values are:

| Tier | Value | Prerequisite |
|---|---:|---|
| Passing | 0 | None |
| Silver | 1 | Passing |
| Gold | 2 | Silver |

Freeze both responses once per run. Derive field names and criterion behavior from those snapshots, not from model memory.

## Repository answer files

BadgeApp reads proposed answers from either:

```text
.bestpractices.json
.project.d/bestpractices.json
```

A repository answer file is a JSON object containing criterion fields. The public project JSON may also contain IDs, user information, timestamps, percentages, lock versions, saved flags, and other server-managed values. Do not copy those values into the repository answer file.

Recognized criterion fields end in:

```text
_status
_justification
```

A candidate key is valid only when the exact key also exists in the frozen project JSON and the corresponding criteria snapshot identifies it as a criterion.

## Status values

Emit these exact strings:

```text
Met
Unmet
N/A
```

BadgeApp automation treats `?` and `unknown` as no proposed value. This skill records such cases in the transient report and omits them from the generated answer file.

Do not emit numeric status values even if a public project response contains legacy numeric serialization.

## Justification rules

- A justification must be a non-empty string no longer than 8192 Unicode code points.
- Emit a justification only with its corresponding status.
- A `Met` answer must include a justification when the criterion requires one.
- A `Met` answer must contain a direct public URL when the criterion requires a URL.
- Prefer HTTPS URLs pinned to a repository commit where possible.
- Do not include credentials, URL user information, private network addresses, local paths, or private-only evidence.
- A SHOULD criterion answered `Unmet` requires a justification of at least five characters.
- A SUGGESTED criterion may be `Unmet` without a justification, though a useful explanation is preferred.
- A MUST criterion answered `Unmet` remains a badge blocker.
- `N/A` is valid only when the current criterion explicitly permits it and the report records evidence of non-applicability.
- An `N/A` answer must include a justification when the current criterion marks N/A justification as required.

## Rules file

The validator accepts a transient rules object keyed by criterion name without a suffix:

```json
{
  "contribution": {
    "strength": "MUST",
    "allow_na": false,
    "na_requires_justification": false,
    "met_requires_url": true,
    "met_requires_justification": false
  },
  "sites_password_security": {
    "strength": "MUST",
    "allow_na": true,
    "na_requires_justification": true,
    "met_requires_url": false,
    "met_requires_justification": true
  }
}
```

Each rule must contain:

| Field | Type | Meaning |
|---|---|---|
| `strength` | string | `MUST`, `SHOULD`, or `SUGGESTED` |
| `allow_na` | boolean | Whether the criterion permits N/A |
| `na_requires_justification` | boolean | Whether N/A requires a non-empty justification |
| `met_requires_url` | boolean | Whether a Met justification must include a public HTTPS URL |
| `met_requires_justification` | boolean | Whether Met requires non-empty explanatory text |

Build this object only from the complete frozen Passing-through-target criteria snapshot set. Include rules for every existing known answer retained in the output as well as every newly proposed answer. If a rule cannot be determined, keep a new criterion Unknown; do not silently discard an existing known answer, but stop and report that it cannot yet be validated.

## Canonical ordering

Canonical output sorts criteria lexicographically by base name. For each criterion, `_status` precedes `_justification`.

Example:

```json
{
  "contribution_status": "Met",
  "contribution_justification": "Documented at https://github.com/example/project/blob/COMMIT/CONTRIBUTING.md",
  "license_location_status": "Met",
  "license_location_justification": "The license is at https://github.com/example/project/blob/COMMIT/LICENSE"
}
```

Use UTF-8, two-space indentation, and one final newline.

## Sources

- [Repository JSON behavior](https://github.com/ossf/best-practices-badge/blob/424f55aff728c97d55a3df53b2d04deef3bcb0d9/docs/bestpractices-json.md#L3-L31)
- [Criterion field validation](https://github.com/ossf/best-practices-badge/blob/424f55aff728c97d55a3df53b2d04deef3bcb0d9/app/lib/criterion_field_validator.rb#L13-L60)
- [Badge sufficiency](https://github.com/ossf/best-practices-badge/blob/424f55aff728c97d55a3df53b2d04deef3bcb0d9/app/models/project.rb#L1240-L1251)
- [Unmet handling](https://github.com/ossf/best-practices-badge/blob/424f55aff728c97d55a3df53b2d04deef3bcb0d9/app/models/project.rb#L1311-L1322)
- [Passing criteria](https://www.bestpractices.dev/en/criteria/0?details=true&rationale=true)
- [Silver criteria](https://www.bestpractices.dev/en/criteria/1?details=true&rationale=true)
- [Gold criteria](https://www.bestpractices.dev/en/criteria/2?details=true&rationale=true)
