#!/bin/sh
# Install repo-side git hooks (idempotent). Run once per clone:
#   sh ops/git-hooks/install.sh
set -e
core=$(git rev-parse --git-dir)
mkdir -p "$core/hooks"
for hook in post-checkout; do
  cp "ops/git-hooks/$hook" "$core/hooks/$hook"
  chmod +x "$core/hooks/$hook"
done
echo "installed: post-checkout (branch-switch audit)"
