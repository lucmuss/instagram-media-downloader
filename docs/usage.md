# Usage

Run the CLI with uv:

```
uv run python -m instagram_downloader --help
```

Commands:
- `saved` downloads saved posts
- `liked` downloads liked posts
- `own` downloads your own posts
- `all` downloads all categories

Examples:

```
uv run python -m instagram_downloader saved
uv run python -m instagram_downloader liked --delay 2.0
uv run python -m instagram_downloader all --log-level DEBUG
```
