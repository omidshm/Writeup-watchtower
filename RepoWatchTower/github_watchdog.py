import requests
import time

# GitHub repository details
GITHUB_OWNER = 'arkadiyt'
GITHUB_REPO = 'bounty-targets-data'
GITHUB_TOKEN = ''  # Optional if the repo is public

# Function to get the latest commit details from GitHub
def get_latest_commit():
    print("Fetching the latest commit...")
    url = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        latest_commit = response.json()[0]
        commit_hash = latest_commit['sha']
        commit_message = latest_commit['commit']['message']
        print("Latest commit fetched successfully.")
        return commit_hash, commit_message
    else:
        print(f'Error fetching commits: {response.status_code}')
        return None, None

# Function to get detailed commit information from GitHub
def get_commit_details(commit_hash):
    print(f"Fetching details for commit: {commit_hash}...")
    url = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits/{commit_hash}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commit_data = response.json()
        files_changed = commit_data['files']
        print("Commit details fetched successfully.")
        return files_changed
    else:
        print(f'Error fetching commit details: {response.status_code}')
        return None

# Main script logic
def main():
    print("Starting GitHub repository watch...")
    last_commit, _ = get_latest_commit()
    if not last_commit:
        print("Failed to fetch the initial commit. Exiting...")
        return

    print("Initial commit fetched. Entering monitoring loop...")
    while True:
        latest_commit, latest_message = get_latest_commit()
        if latest_commit and latest_commit != last_commit:
            print(f'New commit detected: {latest_commit}')
            print(f'Commit message: {latest_message}')
            
            files_changed = get_commit_details(latest_commit)
            if files_changed:
                print('Files changed:')
                
                for file in files_changed:
                    print(f"Filename: {file['filename']}")
                    print(f"Status: {file['status']}")
                    print(f"Changes:\n{file['patch']}")
            
            last_commit = latest_commit
        else:
            print("No new commits detected.")

        time.sleep(60)  # Check every 60 seconds
if __name__ == '__main__':
    main()