# Configuration

Configuration priority:
1. CLI arguments
2. Environment variables
3. INI file

Environment variables are listed in `.env.example`.

INI configuration example:

```
[DEFAULT]
username = username
data_dir = /path/to/instagram-export/data
download_dir = /path/to/output
state_dir = ./state
request_delay = 1.0
max_retries = 3
retry_delay = 5.0
timeout = 60
log_level = INFO
csv_export = true
```
