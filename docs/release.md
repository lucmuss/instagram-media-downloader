# Release Checklist

1. Update versions
- `pyproject.toml`
- `src/instagram_downloader/__init__.py`

2. Update docs
- `README.md`
- `docs/overview.md`
- `docs/usage.md`

3. Run local checks
- `just ci`

4. Create release branch
- `release/x.y.z`

5. Tag release
- `git tag vX.Y.Z`
- `git push --tags`

6. Verify CI
- Ensure lint, typecheck, tests, build, and binary workflows pass
