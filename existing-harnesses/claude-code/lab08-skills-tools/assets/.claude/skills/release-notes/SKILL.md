---
name: release-notes
description: Draft release notes from git history. Use when the user asks for release notes, a changelog entry, or "what changed since the last tag".
allowed-tools: Bash(git log *) Bash(git describe *) Bash(git tag *) Read Edit Write
---

# Release notes

1. Find the previous tag with `git describe --tags --abbrev=0 HEAD~1`
   (if there is none, use the first commit).
2. List commits since that tag with `git log --no-merges --pretty=format:"%h %s" <tag>..HEAD`.
3. Group them by Conventional Commit type, in this order: **Features**
   (`feat`), **Fixes** (`fix`), **Tests** (`test`), **Other**. Rewrite
   each subject as a short user-facing sentence and keep the short hash in
   parentheses.
4. Prepend a new section to `CHANGELOG.md` (create it if missing):

   ```markdown
   ## <today's date, YYYY-MM-DD>

   ### Features
   - Customers can apply discount codes at checkout (a1b2c3d)
   ```

5. Do not invent changes that are not in the log. Do not commit; show the
   new section and stop.
