---
description: Run the local debug framework to identify and fix errors in the app
---
// turbo-all

# Debug: Identify and Fix Errors

Run this workflow whenever you hit a bug, test failure, or unexpected behaviour.

## Steps

1. Run the debug framework in verbose mode to capture all errors:
```powershell
.\debug.ps1 --fix --Verbose 2>&1 | Tee-Object debug-output\last-run.txt
```

2. Read the error log and identify the root cause:
```powershell
Get-Content debug-output\last-run.txt | Select-String "ERROR:|FIX_NEEDED:|WARN:"
```

3. Based on the errors found above, fix the specific file(s) mentioned. Rules:
   - **Backend health failed** → Check `backend/main.py` exists and `uvicorn` is installed
   - **Frontend unreachable** → Check `frontend/package.json` and `npm run dev` works
   - **Playwright test failed** → Read the specific test name and check the component it tests
   - **Pytest failed** → Read the specific test and function mentioned in the traceback
   - **Missing .env** → Create the file from `.env.example` and fill in the keys

4. After fixing, re-run the debug framework without --fix to confirm the fix worked:
```powershell
.\debug.ps1
```

5. If all tests pass, auto-commit the fix:
```powershell
git add -A
git commit -m "fix: <describe what was fixed>"
git push origin main
```

## Notes
- Logs are saved to `debug-output/` folder (gitignored)
- Run with `--BackendOnly` or `--FrontendOnly` to debug just one service
- If errors persist after 2 attempts, open the log and ask for help
