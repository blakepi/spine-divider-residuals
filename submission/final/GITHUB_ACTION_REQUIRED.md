# GitHub Action Required

`gh` was not available on PATH during finalization, so no public repository, remote push, or GitHub release was created automatically.

## Manual `gh` route after installing/authenticating GitHub CLI

```powershell
cd public_release\spine-divider-residuals
git remote add origin https://github.com/<USER_OR_ORG>/spine-divider-residuals.git
git push -u origin main
gh release create v1.0.0-submission --title "v1.0.0-submission" --notes-file RELEASE_NOTES.md
```

Verify the repo is public before updating manuscript availability statements.
