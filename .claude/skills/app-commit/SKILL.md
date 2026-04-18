---
name: app-commit
description: Generate a commit message for this repo. Use when user asks to commit, write a commit, or generate a commit message.
user-invocable: true
---

Generate a commit message for staged changes, then commit.

## Steps

1. Run `git diff --staged` to inspect staged changes
2. If nothing staged, run `git status` and ask user what to stage
3. Generate commit message following the rules below
4. Run `git commit -m "..."` — pre-commit hooks fire automatically (ruff_fix → ruff → mypy → pytest)
5. If commit fails, identify which hook failed and follow the recovery steps below
6. After fixing, retry from step 4 — repeat until commit succeeds or you cannot fix the error

## Hook failure recovery

**ruff_fix modified files** (hook exits non-zero because files were reformatted):
Run the fix-up script — do NOT read it, just execute it with the same message:
```
bash .claude/skills/app-commit/fix-and-commit.sh "<commit message>"
```

**mypy type errors** (output contains `error:` lines):
- Read each error, fix the type annotation or logic issue in the source file
- Re-stage the fixed files with `git add <files>`
- Retry the commit

**pytest failures** (output contains `FAILED` or `ERROR`):
- Read the failure output to identify the broken test and cause
- Fix the source code or test that is failing
- Re-stage the fixed files with `git add <files>`
- Retry the commit

**Cannot fix** (error requires user decision, e.g. ambiguous type, intentionally broken test):
- Stop, report the exact error output to the user, and ask how to proceed

## Hard rules

- NEVER use `--no-verify` unless the user explicitly says so

## Rules

- Conventional Commits format: `type(scope): subject`
- Subject: one sentence, ≤72 chars, imperative mood, no period
- No body — subject only
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `style`
- Scope: optional, use the main module/area changed (e.g. `auth`, `db`, `router`)

## Examples

```
feat(auth): add JWT token validation middleware
fix(repo): raise NotFoundException when record not found
refactor(settings): split db config into separate module
test(infra): add health check endpoint tests
chore: rename docker-compose files from yaml to yml
```
