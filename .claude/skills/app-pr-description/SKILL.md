---
name: app-pr-description
description: Generate a PR description for this repo. Use when user asks to write a PR description, open a PR, or create a pull request.
user-invocable: true
allowed-tools: Bash(git log *) Bash(git diff *) Bash(git branch *) Bash(gh pr *)
---

Generate a concise PR description based on commits since branching from main, then create the PR.

## Steps

1. Run `git log main..HEAD --oneline` to get commits
2. Run `git diff main..HEAD --stat` to see changed files
3. Generate description following the rules below
4. Run `gh pr create --title "..." --body "..."`

## Rules

- Title: Conventional Commits format, ≤72 chars
- Body: max 2 sections, each a bullet list of ≤5 items, no numbered lists unless order matters
- Only include sections that have substance — omit empty ones
- No boilerplate, no checklist, no "this PR..."

## Template

```markdown
## What
- <what changed and why, one bullet per logical change>

## Notes
- <migration steps, breaking changes, manual testing steps — only if needed>
```

## Example

```markdown
## What
- Add JWT authentication middleware for all protected routes
- New `/auth/login` endpoint returns access + refresh tokens
- Migration: adds `tokens` table for refresh token storage

## Notes
- Run `alembic upgrade head` before deploying
- Existing sessions are not affected
```
