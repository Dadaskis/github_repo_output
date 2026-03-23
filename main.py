import requests
from datetime import datetime
import base64

def get_repositories(username, token=None):
    """
    Fetch repository information with pagination support.
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
        
        while True:
            # Add pagination parameters
            params = {
                'page': page,
                'per_page': 100,  # Maximum allowed per page
                'sort': 'created',
                'direction': 'asc'
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
            
            # Check if we've reached the last page
            if len(repositories_page) < 100:
                break
                
            page += 1
        
        if not all_repositories:
            print("No repositories found.")
            return
        
        # Sort manually by creation date (oldest first)
        all_repositories.sort(key=lambda repo: repo['created_at'])
        
        print(f"\n{'='*80}")
        print(f"Total repositories found: {len(all_repositories)}")
        print(f"Oldest repository: {all_repositories[0]['created_at'][:10]}")
        print(f"Newest repository: {all_repositories[-1]['created_at'][:10]}")
        print(f"{'='*80}\n")
        
        # Display each repository
        for idx, repo in enumerate(all_repositories, 1):
            print("=" * 80)
            print(f"Repository #{idx}: {repo['name']}")
            print(f"Created: {repo['created_at']}")
            print(f"Last Updated: {repo['updated_at']}")
            print(f"Private: {'Yes' if repo['private'] else 'No'}")
            print(f"Stars: {repo['stargazers_count']} | Forks: {repo['forks_count']}")
            print("-" * 80)
            
            # Try to fetch README.md
            readme_url = f"https://api.github.com/repos/{username}/{repo['name']}/readme"
            readme_response = session.get(readme_url)
            
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                # README content is base64 encoded
                content = base64.b64decode(readme_data['content']).decode('utf-8')
                print("README.md Content:")
                print("-" * 40)
                print(content)
            else:
                print(f"README.md: Not found. Status code: {readme_response.status_code}")
            
            print("\n")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    try:
        while True:
            print("\n" + "="*80)
            print("GitHub Repository Fetcher")
            print("="*80)
            print("Usage examples:")
            print("  - Just username: Dadaskis")
            print("  - With token: Dadaskis --token ghp_xxxxxxxxxxxx")
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
                get_repositories(username, token)
            else:
                print("Please enter a valid username.")
                
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        quit()

if __name__ == "__main__":
    main()