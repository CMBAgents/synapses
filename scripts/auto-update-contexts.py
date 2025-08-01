#!/usr/bin/env python3
"""
Automated context update system.
Checks every hour for missing contexts or new commits on repositories.
"""

import os
import json
import subprocess
import time
import logging
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import schedule
import threading

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_update.log'),
        logging.StreamHandler()
    ]
)

class AutoContextUpdater:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.context_dir = self.base_dir / "app" / "context"
        self.data_dir = self.base_dir / "app" / "data"
        self.public_context_dir = self.base_dir / "public" / "context"
        self.temp_dir = self.base_dir / "temp" / "contexts"
        self.repos_dir = self.base_dir / "temp" / "repos"
        self.state_file = self.base_dir / "context_update_state.json"
        
        # Create directories if they don't exist
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.public_context_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        
        # Load state
        self.state = self.load_state()
        
        # GitHub headers for API calls
        self.github_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # GitHub token for rate limiting
        self.github_token = os.getenv('GITHUB_TOKEN')
        if self.github_token:
            self.github_headers['Authorization'] = f'token {self.github_token}'

    def load_state(self) -> Dict:
        """Loads the update state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading state: {e}")
        
        return {
            "last_check": None,
            "repository_hashes": {},
            "last_update": None,
            "update_count": 0
        }

    def save_state(self):
        """Saves the current state to file."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    def get_existing_contexts(self) -> Dict[str, List[str]]:
        """Gets the list of existing contexts by domain."""
        existing_contexts = {}
        
        for domain_dir in self.context_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                existing_contexts[domain] = []
                
                for context_file in domain_dir.glob("*.txt"):
                    lib_name = context_file.stem.replace("-context", "")
                    existing_contexts[domain].append(lib_name)
        
        return existing_contexts

    def load_libraries_data(self) -> Dict[str, List[Dict]]:
        """Loads library data from JSON files."""
        libraries = {}
        
        # Load astronomy-libraries.json
        astronomy_file = self.data_dir / "astronomy-libraries.json"
        if astronomy_file.exists():
            with open(astronomy_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                libraries['astronomy'] = data.get('libraries', [])
        
        # Load finance-libraries.json
        finance_file = self.data_dir / "finance-libraries.json"
        if finance_file.exists():
            with open(finance_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                libraries['finance'] = data.get('libraries', [])
        
        # Load libraries.json for other domains
        libraries_file = self.data_dir / "libraries.json"
        if libraries_file.exists():
            with open(libraries_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for domain, libs in data.items():
                    if domain not in libraries:
                        libraries[domain] = libs
        
        return libraries

    def extract_repo_info(self, github_url: str) -> Optional[Dict]:
        """Extracts repository information from GitHub URL."""
        try:
            url = github_url.strip()
            if not url.startswith('http'):
                url = f"https://{url}"
            
            if 'github.com' in url:
                parts = url.split('/')
                if len(parts) >= 2:
                    owner = parts[-2]
                    repo_name = parts[-1]
                    if repo_name.endswith('.git'):
                        repo_name = repo_name[:-4]
                    return {
                        'owner': owner,
                        'repo': repo_name,
                        'url': url
                    }
            else:
                parts = url.split('/')
                if len(parts) >= 2:
                    return {
                        'owner': parts[-2],
                        'repo': parts[-1],
                        'url': f"https://github.com/{parts[-2]}/{parts[-1]}"
                    }
        except Exception as e:
            logging.error(f"Error extracting repo info from {github_url}: {e}")
        
        return None

    def get_repository_hash(self, owner: str, repo: str) -> Optional[str]:
        """Gets the latest commit hash for a repository."""
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/commits"
            response = requests.get(url, headers=self.github_headers, timeout=10)
            
            if response.status_code == 200:
                commits = response.json()
                if commits and len(commits) > 0:
                    return commits[0]['sha']
            else:
                logging.warning(f"Failed to get commits for {owner}/{repo}: {response.status_code}")
                
        except Exception as e:
            logging.error(f"Error getting repository hash for {owner}/{repo}: {e}")
        
        return None

    def has_repository_changed(self, owner: str, repo: str) -> bool:
        """Checks if a repository has new commits."""
        repo_key = f"{owner}/{repo}"
        current_hash = self.get_repository_hash(owner, repo)
        
        if not current_hash:
            return False
        
        stored_hash = self.state.get("repository_hashes", {}).get(repo_key)
        
        if stored_hash != current_hash:
            logging.info(f"Repository {repo_key} has changed: {stored_hash} -> {current_hash}")
            return True
        
        return False

    def clone_repository(self, owner: str, repo: str, package_name: str) -> bool:
        """Clones the GitHub repository."""
        repo_path = self.repos_dir / package_name
        
        # Remove existing repo for fresh clone
        if repo_path.exists():
            try:
                import shutil
                shutil.rmtree(repo_path)
                logging.info(f"Removed old repo: {repo_path}")
            except Exception as e:
                logging.warning(f"Unable to remove old repo: {e}")
        
        try:
            clone_url = f"https://github.com/{owner}/{repo}.git"
            cmd = ["git", "clone", clone_url, str(repo_path)]
            
            logging.info(f"Cloning {clone_url} to {repo_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logging.info(f"Repository cloned successfully: {package_name}")
                return True
            else:
                logging.error(f"Error cloning {package_name}")
                logging.error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout cloning {package_name}")
            return False
        except Exception as e:
            logging.error(f"Exception cloning {package_name}: {e}")
            return False

    def generate_context_with_contextmaker(self, package_name: str, lib_name: str) -> Optional[str]:
        """Generates context using the contextmaker package."""
        logging.info(f"Generating context for {package_name} with contextmaker")
        
        repo_path = self.repos_dir / package_name
        if not repo_path.exists():
            logging.error(f"Repository {package_name} not found in {repo_path}")
            return None
        
        temp_output_path = self.temp_dir / f"{package_name}_context"
        temp_output_path.mkdir(exist_ok=True)
        
        try:
            cmd = [
                "python", "-c", 
                f"import contextmaker; contextmaker.make('{package_name}', output_path='{temp_output_path}')"
            ]
            
            logging.info(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                logging.info(f"Contextmaker succeeded for {package_name}")
                
                context_files = list(temp_output_path.glob("*.txt"))
                if context_files:
                    context_file = context_files[0]
                    
                    with open(context_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    enhanced_content = self.enhance_context_content(content, package_name, lib_name)
                    
                    logging.info(f"Context generated for {package_name}: {len(content)} characters")
                    return enhanced_content
                else:
                    logging.warning(f"No .txt file found in {temp_output_path}")
                    return None
            else:
                logging.error(f"Contextmaker error for {package_name}")
                logging.error(f"STDOUT: {result.stdout}")
                logging.error(f"STDERR: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout for {package_name} (more than 5 minutes)")
            return None
        except Exception as e:
            logging.error(f"Exception during generation for {package_name}: {e}")
            return None
        finally:
            try:
                import shutil
                shutil.rmtree(temp_output_path)
            except Exception as e:
                logging.warning(f"Unable to clean {temp_output_path}: {e}")

    def enhance_context_content(self, content: str, package_name: str, lib_name: str) -> str:
        """Enhances context content with metadata."""
        enhanced_parts = []
        enhanced_parts.append(f"# Documentation for {lib_name}")
        enhanced_parts.append(f"Package: {package_name}")
        enhanced_parts.append(f"Generated with: contextmaker")
        enhanced_parts.append(f"Auto-updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        enhanced_parts.append("")
        enhanced_parts.append("=" * 80)
        enhanced_parts.append("")
        enhanced_parts.append(content)
        
        return "\n".join(enhanced_parts)

    def save_context_file(self, domain: str, lib_name: str, content: str):
        """Saves the context file."""
        domain_dir = self.context_dir / domain
        domain_dir.mkdir(exist_ok=True)
        
        filename = f"{lib_name}-context.txt"
        filepath = domain_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"Context saved: {filepath}")
        
        # Copy to public/context
        public_filepath = self.public_context_dir / filename
        with open(public_filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def sync_to_cloud(self):
        """Synchronizes contexts to cloud."""
        try:
            from scripts.cloud_sync_contexts import CloudContextSync
            syncer = CloudContextSync(str(self.base_dir))
            syncer.sync_contexts_to_cloud()
            logging.info("Cloud synchronization completed")
        except Exception as e:
            logging.error(f"Error during cloud synchronization: {e}")

    def check_contextmaker_available(self) -> bool:
        """Checks if contextmaker is available."""
        try:
            result = subprocess.run(
                ["python", "-c", "import contextmaker"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logging.info("✅ contextmaker package available")
                return True
            else:
                logging.error("❌ contextmaker package not available")
                return False
        except Exception as e:
            logging.error(f"Error checking contextmaker: {e}")
            return False

    def check_git_available(self) -> bool:
        """Checks if git is available."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logging.info("✅ Git available")
                return True
            else:
                logging.error("❌ Git not available")
                return False
        except Exception as e:
            logging.error(f"Error checking git: {e}")
            return False

    def update_repository_hash(self, owner: str, repo: str):
        """Updates the stored hash for a repository."""
        repo_key = f"{owner}/{repo}"
        current_hash = self.get_repository_hash(owner, repo)
        
        if current_hash:
            if "repository_hashes" not in self.state:
                self.state["repository_hashes"] = {}
            self.state["repository_hashes"][repo_key] = current_hash
            logging.info(f"Updated hash for {repo_key}: {current_hash}")

    def update_config_from_contexts(self):
        """Updates config.json when context files are updated."""
        try:
            logging.info("🔄 Updating config.json from context changes...")
            
            # Import and run the config updater
            config_updater_script = self.base_dir / "scripts" / "update-config-from-contexts.py"
            
            if config_updater_script.exists():
                result = subprocess.run(
                    ["python3", str(config_updater_script)],
                    capture_output=True,
                    text=True,
                    cwd=self.base_dir
                )
                
                if result.returncode == 0:
                    logging.info("✅ Config.json updated successfully")
                    if result.stdout:
                        logging.info(f"Config update output: {result.stdout.strip()}")
                else:
                    logging.error(f"❌ Error updating config.json: {result.stderr}")
            else:
                logging.warning("⚠️ Config updater script not found")
                
        except Exception as e:
            logging.error(f"❌ Error in update_config_from_contexts: {e}")

    def check_and_update_contexts(self):
        """Main function to check and update contexts."""
        logging.info("🔄 Starting automated context check and update")
        
        # Check prerequisites
        if not self.check_contextmaker_available():
            logging.error("Cannot continue without contextmaker")
            return
        
        if not self.check_git_available():
            logging.error("Cannot continue without git")
            return
        
        # Load data
        existing_contexts = self.get_existing_contexts()
        libraries_data = self.load_libraries_data()
        
        updates_made = 0
        
        for domain, libraries in libraries_data.items():
            logging.info(f"Processing domain: {domain}")
            
            existing_libs = existing_contexts.get(domain, [])
            
            for lib in libraries:
                lib_name = lib.get('name', '').replace('/', '-').replace('_', '-')
                github_url = lib.get('github_url', '')
                
                if not github_url:
                    continue
                
                repo_info = self.extract_repo_info(github_url)
                if not repo_info:
                    continue
                
                package_name = repo_info['repo']
                owner = repo_info['owner']
                repo = repo_info['repo']
                
                needs_update = False
                
                # Check if context is missing
                if lib_name not in existing_libs:
                    logging.info(f"Missing context for {lib_name}, will generate")
                    needs_update = True
                
                # Check if repository has new commits
                elif self.has_repository_changed(owner, repo):
                    logging.info(f"Repository {owner}/{repo} has new commits, will update")
                    needs_update = True
                
                if needs_update:
                    # Clone repository
                    if not self.clone_repository(owner, repo, package_name):
                        continue
                    
                    # Generate context
                    content = self.generate_context_with_contextmaker(package_name, lib_name)
                    
                    if content:
                        # Save context
                        self.save_context_file(domain, lib_name, content)
                        updates_made += 1
                        
                        # Update repository hash
                        self.update_repository_hash(owner, repo)
                        
                        # Pause to avoid overload
                        time.sleep(2)
                    else:
                        logging.warning(f"Failed to generate context for {lib_name}")
        
        # Update state
        self.state["last_check"] = datetime.now().isoformat()
        if updates_made > 0:
            self.state["last_update"] = datetime.now().isoformat()
            self.state["update_count"] = self.state.get("update_count", 0) + updates_made
            
            # Sync to cloud if updates were made
            self.sync_to_cloud()
            
            # Update config.json if contexts were updated
            self.update_config_from_contexts()
        
        self.save_state()
        
        logging.info(f"✅ Automated check complete. {updates_made} contexts updated.")

    def run_scheduler(self):
        """Runs the scheduler."""
        logging.info("🚀 Starting automated context updater scheduler")
        
        # Schedule hourly checks
        schedule.every().hour.do(self.check_and_update_contexts)
        
        # Run initial check
        self.check_and_update_contexts()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function."""
    updater = AutoContextUpdater()
    
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        # Run once
        updater.check_and_update_contexts()
    else:
        # Run scheduler
        updater.run_scheduler()

if __name__ == "__main__":
    import sys
    main() 