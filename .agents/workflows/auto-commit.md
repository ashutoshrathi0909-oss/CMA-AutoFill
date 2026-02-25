---
description: Auto-commit and push changes to GitHub after completing any task
---

# Auto-Commit to GitHub

Use this workflow after completing any task to automatically save your work to GitHub.

## Steps

1. Stage all changes:
// turbo
```bash
git add -A
```

2. Create a descriptive commit message based on what was changed:
// turbo
```bash
git commit -m "<describe what was done in this session>"
```

3. Push to the remote repository:
// turbo
```bash
git push origin main
```

4. Confirm the push was successful by checking git status:
// turbo
```bash
git status
```

## Notes
- Always run this workflow at the END of a task session
- The commit message should describe what was accomplished (e.g., "Phase 02: Create database tables and RLS policies")
- If push fails due to remote changes, run `git pull --rebase origin main` first, then push again
