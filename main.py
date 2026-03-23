import requests
from datetime import datetime
import base64
import time

def get_repository_commits(username, repo_name, session, token=None):
    """
    Fetch recent commits for a specific repository.
    
    Args:
        username: GitHub username
        repo_name: Repository name
        session: Requests session
        token: Optional GitHub token
        max_commits: Maximum number of commits to fetch
    
    Returns:
        List of commit objects
    """
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
    
    try:
        # Try to get commits from default branch
        params = {
            'per_page': 100,  # Fetch only what we need
            'page': 1
        }

        all_commits = []

        while True:
            response = session.get(commits_url, params=params)
        
            if response.status_code == 200:
                response_commits = response.json()
            
                if not response_commits:
                    break
                
                all_commits.extend(response_commits)

                if len(response_commits) < 100:
                    break
                
                params['page'] += 1
            elif response.status_code == 409:
                # Empty repository
                return []
            else:
                return None
        
        return all_commits
            
    except Exception as e:
        print(f"  Error fetching commits: {str(e)}")
        return None

def display_commits(commits, repo_name):
    """
    Display commit information in a formatted way.
    """
    if commits is None:
        print(f"Unable to fetch commits for {repo_name}")
        return
    
    if not commits:
        print(f"No commits found in {repo_name}")
        return
    
    print(f"\nCommits:")
    print("  " + "-" * 70)
    
    for i, commit in enumerate(commits):
        commit_data = commit.get('commit', {})
        author = commit_data.get('author', {}).get('name', 'Unknown')
        date_str = commit_data.get('author', {}).get('date', '')
        message = commit_data.get('message', '').split('\n')[0]  # First line only
        sha = commit.get('sha', '')[:7]
        
        # Format date
        if date_str:
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                formatted_date = date.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = date_str[:16]
        else:
            formatted_date = 'Unknown date'
        
        print(f"  {i:2}. [{sha}] {author} ({formatted_date})")
        print(f"      {message}")

def get_repositories(username, token=None, show_commits=True):
    """
    Fetch repository information with pagination support and optional commits.
    """
    print(f"Fetching repositories for user: {username}\n")
    
    # GitHub API endpoint for user repositories
    url = f"https://api.github.com/users/{username}/repos"
    
    try:
        session = requests.sessions.Session()
        if token is not None:
            session.headers["Authorization"] = f"Bearer {token}"
        
        all_repositories = []
        page = 1
        rate_limit_warning_shown = False

        # Get the authenticated user's login
        is_authenticated_user = False
        user_response = session.get("https://api.github.com/user")
        if user_response.status_code == 200:
            authenticated_username = user_response.json()['login'].lower()
            if username == authenticated_username:
                is_authenticated_user = True
                url = "https://api.github.com/user/repos"
                print(f"Authenticated as {username} - will fetch all repositories (public + private)\n")
            else:
                print(f"Authenticated but viewing {username}'s public repositories only\n")
        else:
            print("Could not verify authenticated user\n")
        
        while True:
            # Add pagination parameters
            params = {
                'page': page,
                'per_page': 100,  # Maximum allowed per page
                'sort': 'created',
                'direction': 'asc',
                'type': 'all'
            }
            
            response = session.get(url, params=params)
            
            if response.status_code != 200:
                if response.status_code == 403:
                    print("Rate limit exceeded! Try again later or use authentication for higher limits.")
                    print(f"Rate limit info: {response.headers.get('X-RateLimit-Remaining', 'N/A')} requests remaining")
                else:
                    print(f"Error: Status code {response.status_code}")
                    print(response.json().get('message', 'Unknown error'))
                return
            
            repositories_page = response.json()
            
            if not repositories_page:
                break
            
            all_repositories.extend(repositories_page)
            print(f"Fetched page {page}: {len(repositories_page)} repositories (Total: {len(all_repositories)})")
            
            # Check rate limit status
            remaining = response.headers.get('X-RateLimit-Remaining')
            if remaining and int(remaining) < 10 and not rate_limit_warning_shown and not token:
                print(f"Low rate limit: {remaining} requests remaining. Consider using a token for higher limits.")
                rate_limit_warning_shown = True
            
            # Check if we've reached the last page
            if len(repositories_page) < 100:
                break
                
            page += 1
            
            # Add small delay to avoid rate limiting
            if token is None:
                time.sleep(0.2)
        
        if not all_repositories:
            print("No repositories found.")
            return
        
        # Sort manually by creation date (oldest first)
        all_repositories.sort(key=lambda repo: repo['created_at'])

        # Count forks
        total_forks = sum(1 for repo in all_repositories if repo.get('fork', False))
        
        print(f"\n{'='*80}")
        print(f"Total repositories found: {len(all_repositories)}")
        print(f"Oldest repository: {all_repositories[0]['created_at'][:10]}")
        print(f"Newest repository: {all_repositories[-1]['created_at'][:10]}")
        print(f"Forked repositories: {total_forks}")
        print(f"{'='*80}\n")
        
        # Display each repository
        for idx, repo in enumerate(all_repositories, 1):
            is_fork = repo.get('fork', False)

            print("=" * 80)
            print(f"Repository #{idx}: {repo['name']}")
            print(f"Created: {repo['created_at']}")
            print(f"Last Updated: {repo['updated_at']}")
            print(f"Private: {'Yes' if repo['private'] else 'No'}")
            print(f"Stars: {repo['stargazers_count']} | Forks: {repo['forks_count']}")
            print(f"Language: {repo['language'] if repo['language'] else 'Not specified'}")
            print(f"Size: {repo['size']} KB")

            if is_fork:
                print(f"Type: Fork (original: {repo.get('parent', {}).get('full_name', 'unknown')})")
            else:
                print(f"Type: Original Repository")

            print("-" * 80)
            
            # Try to fetch README.md
            readme_url = f"https://api.github.com/repos/{username}/{repo['name']}/readme"
            readme_response = session.get(readme_url)
            
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                # README content is base64 encoded
                content = base64.b64decode(readme_data['content']).decode('utf-8')
                print("README.md Preview:")
                print("-" * 40)
                print(content)
            else:
                print(f"README.md: Not found")
            
            # Fetch and display commits if requested
            if show_commits and not is_fork:
                # Add a small delay to avoid rate limiting
                if token is None:
                    time.sleep(0.3)
                
                commits = get_repository_commits(username, repo['name'], session, token)
                display_commits(commits, repo['name'])
            
            print("\n")
            
        # Print summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total repositories processed: {len(all_repositories)}")
        print("=" * 80)
            
    except Exception as e:
        print(f"get_repositories Error: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    try:
        while True:
            print("\n" + "="*80)
            print("GitHub Repository & Commit Fetcher")
            print("="*80)
            print("Usage examples:")
            print("  - Just username: octocat")
            print("  - With token: octocat --token ghp_xxxxxxxxxxxx")
            print("  - Type 'quit' or 'exit' to leave")
            print("-"*80)
            
            user_input = input("GitHub username (or 'quit' to exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            token = None
            if "--token" in user_input:
                parts = user_input.split("--token", 1)
                username = parts[0].strip()
                token = parts[1].strip()
                print(f"Using token for user: {username}")
            else:
                username = user_input
            
            if username:
                # Ask about commit display
                print("\nCommit options:")
                show_commits_input = input("Show commits? (y/n, default: y): ").strip().lower()
                show_commits = show_commits_input != 'n'
                
                get_repositories(username, token, show_commits)
            else:
                print("Please enter a valid username.")
                
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        quit()

if __name__ == "__main__":
    main()