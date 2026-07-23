## Security

1. Never expose, log, commit, or embed secrets, credentials, tokens, or private
   user data.
2. Treat all external input as untrusted. Validate at system boundaries and use
   parameterized APIs instead of constructing commands, queries, or markup.
3. Preserve authentication, authorization, and permission checks. Apply least
   privilege when adding access or capabilities.
4. Do not disable security controls, certificate validation, validation logic,
   or dependency checks to make an implementation pass.
5. Flag security-sensitive behavior and assumptions explicitly when they cannot
   be verified.

### Dependency versions

Never rely on model knowledge when selecting a dependency version.

When adding or upgrading a dependency:

1. Query its authoritative package registry for the current stable versions.
2. Select the latest stable version compatible with the project's runtime,
   framework, peer dependencies, and existing constraints.
3. Use the package manager's add/install command; do not manually edit generated
   lockfiles.
4. Do not introduce an outdated major or prerelease version unless explicitly
   requested or required for compatibility.
5. Before completing the task, verify every newly added direct dependency
   against the registry and run the relevant tests.


## Maintainability

1. Follow the repository's existing architecture, conventions, and public APIs
   unless the task explicitly requires changing them.
2. Prefer the smallest coherent change that solves the requested problem. Avoid
   unrelated refactors, formatting churn, and speculative abstractions.
3. Keep functions and modules focused. Reuse established code where it improves
   clarity, but do not hide behavior behind unnecessary indirection.
4. Document non-obvious decisions and constraints rather than restating the
   code.
5. Remove dead code introduced or made obsolete by the change.

### OpenSpec

1. When creating PRs consider if the current OpenSpec should be archived in
   advance of creating the PR. If the spec requires multiple PRs to implement,
   consider creating a new OpenSpec for the next PR. If the spec is not yet
   complete, consider creating a new OpenSpec for the next PR.

## Correctness

1. Confirm expected behavior and inspect relevant call sites before changing
   code. Do not guess when repository evidence is available.
2. Handle relevant boundary cases, invalid input, partial failure, and error
   propagation explicitly.
3. Add or update tests for changed behavior, including regression and failure
   cases where practical.
4. Do not weaken tests, types, assertions, validation, or error handling merely
   to make checks pass.
5. Run the narrowest relevant checks first, then the broader test, type-check,
   lint, or build commands appropriate to the change.
6. Never claim a command or test passed unless it was run successfully. Report
   skipped checks and unresolved risks.

## Scope and uncertainty

1. Preserve backward compatibility unless a breaking change is explicitly
   requested.
2. Ask for clarification when requirements are ambiguous and materially affect
   behavior, security, data, or public APIs.
3. Do not modify unrelated files or overwrite user changes.
4. Before editing, check for repository-local instructions that apply to the
   files being changed.
