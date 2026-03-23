# GitHub Repository Fetcher

A Python script that retrieves and displays comprehensive information about a GitHub user's repositories, including repository metadata and README content. This tool provides a convenient way to audit, analyze, or document repository collections through the GitHub API.

### Features

- **Complete Repository Listing** - Fetches all repositories for any public GitHub user with automatic pagination support (handles up to 100 repositories per page)
- **Detailed Repository Information** - Displays creation date, last update timestamp, visibility status (public/private), star count, and fork count for each repository
- **README Content Extraction** - Automatically retrieves and displays the content of each repository's README.md file (when available)
- **Authentication Support** - Optional GitHub personal access token for higher API rate limits and access to private repositories (with appropriate permissions)
- **Interactive Mode** - User-friendly command-line interface with example usage and graceful exit options
- **Rate Limit Handling** - Detects and reports GitHub API rate limit status with helpful error messages

### Requirements

- Python 3.x
- `requests` library (`pip install requests`)

### Usage

Run the script and enter a GitHub username when prompted:

```
python github_repo_fetcher.py
```

**Basic usage (public repositories only):**
```
GitHub username: octocat
```

**With authentication token (higher limits + private repos):**
```
GitHub username: octocat --token ghp_xxxxxxxxxxxx
```

**Interactive commands:**
- Type `quit`, `exit`, or `q` to exit the program
- Press `Ctrl+C` for graceful termination

### Authentication Token

To obtain a GitHub personal access token:
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate a new token with `repo` scope for private repositories or `public_repo` for public repos only
3. Tokens are optional but recommended for users with many repositories or frequent API calls

### Output Example

```
================================================================================
Repository #1: awesome-project
Created: 2023-01-15T10:30:00Z
Last Updated: 2024-03-20T14:45:00Z
Private: No
Stars: 42 | Forks: 8
--------------------------------------------------------------------------------
README.md Content:
----------------------------------------
# Awesome Project

A project that does amazing things...

## Installation
pip install awesome-project
...
```

### API Rate Limits

- **Unauthenticated requests**: 60 requests per hour
- **Authenticated requests**: 5,000 requests per hour

The script automatically paginates through results, so users with many repositories may need to use authentication to avoid rate limiting.

### Error Handling

- Handles network errors and invalid usernames gracefully
- Reports rate limit exceedance with remaining request counts
- Provides clear error messages for HTTP status codes

### Use Cases

- Repository inventory and documentation
- Open source project discovery
- Backup verification
- Portfolio review
- Compliance auditing

### License

MIT License. *Happiness to everyone!*
