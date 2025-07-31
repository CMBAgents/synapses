import requests
import json
import re
import csv
from time import sleep
from typing import Set, Tuple, List
from tqdm import tqdm
from multiprocessing import Pool, Manager
from functools import partial
import random

def download_ascl_data():
    """Download JSON data from ASCL"""
    url = "https://ascl.net/code/json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def extract_github_repos(data) -> Set[str]:
    """Extract unique GitHub repository paths from the data"""
    github_pattern = r'github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)'
    repos = set()
    
    # Convert data to string to search through all content
    data_str = json.dumps(data)
    
    # Find all GitHub URLs
    matches = re.findall(github_pattern, data_str, re.IGNORECASE)
    
    for match in matches:
        # Clean up the repository path
        repo_path = match.strip()
        # Remove any trailing characters that shouldn't be there
        repo_path = re.sub(r'["\],\s]+$', '', repo_path)
        # Remove any trailing .git
        if repo_path.endswith('.git'):
            repo_path = repo_path[:-4]
        # Convert to lowercase for deduplication
        repos.add(repo_path.lower())
    
    return repos

def get_github_stars_with_delay(repo_with_index: Tuple[int, str]) -> Tuple[str, int]:
    """Get star count for a GitHub repository with random delay to avoid rate limiting"""
    index, repo_path = repo_with_index
    
    # Add random delay to spread out requests across workers
    sleep(random.uniform(0.1, 0.5))
    
    url = f"https://github.com/{repo_path}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Look for the star count in the HTML
            # Pattern: "Star this repository (NUMBER)"
            star_pattern = r'Star this repository \((\d+)\)'
            match = re.search(star_pattern, response.text)
            if match:
                return (f"github.com/{repo_path}", int(match.group(1)))
            else:
                # Try alternative pattern for already starred repos
                # Pattern: aria-label="NUMBER users starred this repository"
                alt_pattern = r'aria-label="(\d+) users? starred this repository"'
                match = re.search(alt_pattern, response.text)
                if match:
                    return (f"github.com/{repo_path}", int(match.group(1)))
                return (f"github.com/{repo_path}", 0)
        else:
            return (f"github.com/{repo_path}", -1)
    except Exception:
        return (f"github.com/{repo_path}", -1)

def update_progress(result, pbar):
    """Update progress bar callback"""
    pbar.update(1)
    return result

def main():
    # Download and extract repositories
    print("Downloading ASCL data...")
    data = download_ascl_data()
    
    print("Extracting GitHub repositories...")
    repos = sorted(extract_github_repos(data))  # Sort alphabetically
    print(f"Found {len(repos)} unique repositories")
    
    # Prepare repos with indices for processing
    repos_with_indices = list(enumerate(repos))
    
    # Fetch star counts in parallel
    print("Fetching star counts with 4 parallel workers...")
    results = []
    
    with Manager() as manager:
        # Create progress bar
        with tqdm(total=len(repos_with_indices), desc="Processing repositories") as pbar:
            # Process in parallel with 4 workers
            with Pool(processes=4) as pool:
                # Use imap_unordered for better performance
                for result in pool.imap_unordered(get_github_stars_with_delay, repos_with_indices):
                    results.append(result)
                    pbar.update(1)
    
    # Sort results alphabetically by URL
    results.sort(key=lambda x: x[0])
    
    # Save to CSV
    with open('ascl_repos_with_stars.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['github_url', 'stars'])
        writer.writerows(results)
    
    print(f"\nSaved {len(results)} repositories to ascl_repos_with_stars.csv")
    
    # Get top 100 repositories
    get100()

    # Show statistics
    valid_stars = [stars for _, stars in results if stars >= 0]
    if valid_stars:
        print(f"Average stars: {sum(valid_stars) / len(valid_stars):.1f}")
        print(f"Max stars: {max(valid_stars)}")
        print(f"Repositories with star data: {len(valid_stars)}/{len(results)}")

if __name__ == "__main__":
    main()