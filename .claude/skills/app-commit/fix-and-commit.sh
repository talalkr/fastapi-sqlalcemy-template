#!/usr/bin/env bash
# Re-stages files modified by pre-commit hooks (e.g. ruff_fix auto-formatting)
# and retries the commit with the same message.
# Usage: fix-and-commit.sh <commit-message>

set -euo pipefail

MSG="$1"

# Re-stage only tracked files that were modified (by hooks like ruff_fix)
git add -u

# Retry commit — pre-commit will run again; if hooks pass this time, we're done
git commit -m "$MSG"
