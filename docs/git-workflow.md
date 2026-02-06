# Git Workflow

Branch model:
- `main` is always release-ready
- `feature/*` for feature work
- `fix/*` for bug fixes
- `release/*` for release preparation

Pull requests:
- Require CI green
- Squash or rebase for clean history
- Use clear titles and descriptions

Release flow:
1. Create `release/x.y.z` from `main`
2. Update version numbers and docs
3. Run `just ci`
4. Merge to `main`
5. Tag `vX.Y.Z` on `main`
6. Push tags to trigger release workflows
