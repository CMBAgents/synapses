#!/usr/bin/env python3
"""
Script to automatically generate missing contexts
for all GitHub repositories listed in the data files.
Uses the contextmaker package for complete documentation extraction.
"""

import os
import json
import csv
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('context_generation.log'),
        logging.StreamHandler()
    ]
)

class ContextGenerator:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "app" / "data"
        self.context_dir = self.base_dir / "public" / "context"  # UNIFIED: Only public/context
        self.temp_dir = self.base_dir / "temp" / "contexts"
        self.repos_dir = self.base_dir / "temp" / "repos"
        
        # Create directories if they don't exist
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.repos_dir.mkdir(parents=True, exist_ok=True)

    def get_existing_contexts(self) -> Dict[str, List[str]]:
        """Gets the list of existing contexts by domain."""
        existing_contexts = {}
        
        for domain_dir in self.context_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                existing_contexts[domain] = []
                
                for context_file in domain_dir.glob("*.txt"):
                    # Extract library name from filename
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
        
        # Note: libraries.json a été supprimé car il était incorrect
        # On utilise maintenant uniquement les fichiers spécifiques par domaine
        
        return libraries

    def extract_repo_info(self, github_url: str) -> Optional[Dict]:
        """Extracts repository information from GitHub URL."""
        try:
            # Clean URL
            url = github_url.strip()
            if not url.startswith('http'):
                url = f"https://{url}"
            
            # Extract owner/repo
            if 'github.com' in url:
                # Format: https://github.com/owner/repo
                parts = url.split('/')
                if len(parts) >= 2:
                    owner = parts[-2]
                    repo_name = parts[-1]
                    # Clean name (remove .git if present)
                    if repo_name.endswith('.git'):
                        repo_name = repo_name[:-4]
                    return {
                        'owner': owner,
                        'repo': repo_name,
                        'url': url
                    }
            else:
                # Format: owner/repo
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

    def clone_repository(self, owner: str, repo: str, package_name: str) -> bool:
        """Clones the GitHub repository."""
        repo_path = self.repos_dir / package_name
        
        # If repo already exists, remove it for a fresh version
        if repo_path.exists():
            try:
                import shutil
                shutil.rmtree(repo_path)
                logging.info(f"Old repo deleted: {repo_path}")
            except Exception as e:
                logging.warning(f"Unable to delete old repo: {e}")
        
        try:
            # Git clone command
            clone_url = f"https://github.com/{owner}/{repo}.git"
            cmd = ["git", "clone", clone_url, str(repo_path)]
            
            logging.info(f"Cloning {clone_url} to {repo_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
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

    def generate_context_with_contextmaker(self, package_name: str, lib_name: str, domain: str) -> Optional[str]:
        """Generates context using the contextmaker package."""
        logging.info(f"Generating context for {package_name} with contextmaker")
        
        # Check that repository is cloned
        repo_path = self.repos_dir / package_name
        if not repo_path.exists():
            logging.error(f"Repository {package_name} not found in {repo_path}")
            return None
        
        # Create domain directory in context if it doesn't exist
        domain_context_dir = self.context_dir / domain
        domain_context_dir.mkdir(parents=True, exist_ok=True)
        
        # Define output path for context file
        output_filename = f"{lib_name}-context.txt"
        output_path = domain_context_dir / output_filename
        
        try:
            # Use contextmaker.make() directly with the specified structure
            import contextmaker
            
            logging.info(f"Calling contextmaker.make() for {package_name}")
            logging.info(f"  - library_name: {package_name}")
            logging.info(f"  - output_path: {output_path}")
            logging.info(f"  - input_path: {repo_path}")
            logging.info(f"  - rough: True")
            
            result = contextmaker.make(
                library_name=package_name,
                output_path=str(output_path),
                input_path=str(repo_path),
                rough=True,
            )
            
            if result and output_path.exists():
                logging.info(f"Contextmaker succeeded for {package_name}")
                
                # Read content
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add metadata
                enhanced_content = self.enhance_context_content(content, package_name, lib_name)
                
                # Save enhanced content back to the same file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                
                logging.info(f"Context generated for {package_name}: {len(enhanced_content)} characters")
                logging.info(f"Context saved to: {output_path}")
                
                return enhanced_content
            else:
                logging.warning(f"Context file not found at {output_path}")
                logging.warning(f"contextmaker result: {result}")
                return None
                
        except Exception as e:
            logging.error(f"Exception during generation for {package_name}: {e}")
            return None
        finally:
            # Clean only the temporary repository, NOT the context file
            try:
                import shutil
                shutil.rmtree(repo_path)
                logging.info(f"Temporary repository cleaned: {repo_path}")
            except Exception as e:
                logging.warning(f"Unable to clean temporary repository {repo_path}: {e}")

    def enhance_context_content(self, content: str, package_name: str, lib_name: str) -> str:
        """Enhances context content with metadata."""
        enhanced_parts = []
        enhanced_parts.append(f"# Documentation for {lib_name}")
        enhanced_parts.append(f"Package: {package_name}")
        enhanced_parts.append(f"Generated with: contextmaker")
        enhanced_parts.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        enhanced_parts.append("")
        enhanced_parts.append("=" * 80)
        enhanced_parts.append("")
        enhanced_parts.append(content)
        
        return "\n".join(enhanced_parts)

    def save_context_file(self, domain: str, lib_name: str, content: str):
        """Saves the context file."""
        # Create domain directory if it doesn't exist
        domain_dir = self.context_dir / domain
        domain_dir.mkdir(exist_ok=True)
        
        # Filename
        filename = f"{lib_name}-context.txt"
        filepath = domain_dir / filename
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"Context saved: {filepath}")

    def check_contextmaker_available(self) -> bool:
        """Checks if contextmaker is available."""
        try:
            result = subprocess.run(
                ["python3", "-c", "import contextmaker"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logging.info("✅ contextmaker package available")
                return True
            else:
                logging.error("❌ contextmaker package not available")
                logging.error(f"STDERR: {result.stderr}")
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

    def generate_missing_contexts(self):
        """Generates missing contexts for all libraries."""
        # Check that contextmaker and git are available
        if not self.check_contextmaker_available():
            logging.error("Cannot continue without contextmaker")
            return
        
        if not self.check_git_available():
            logging.error("Cannot continue without git")
            return
        
        # Load existing data
        existing_contexts = self.get_existing_contexts()
        libraries_data = self.load_libraries_data()
        
        logging.info(f"Existing contexts: {existing_contexts}")
        logging.info(f"Found libraries: {list(libraries_data.keys())}")
        
        total_generated = 0
        
        for domain, libraries in libraries_data.items():
            logging.info(f"Processing domain: {domain}")
            
            existing_libs = existing_contexts.get(domain, [])
            
            for lib in libraries:
                lib_name = lib.get('name', '').replace('/', '-').replace('_', '-')
                github_url = lib.get('github_url', '')
                
                if not github_url:
                    logging.warning(f"No GitHub URL for {lib_name}")
                    continue
                
                # Check if context already exists
                if lib_name in existing_libs:
                    logging.info(f"Existing context for {lib_name}, skipped")
                    continue
                
                # Extract repository information
                repo_info = self.extract_repo_info(github_url)
                if not repo_info:
                    logging.error(f"Unable to extract repo info: {github_url}")
                    continue
                
                package_name = repo_info['repo']
                
                # 1. Clone repository
                if not self.clone_repository(repo_info['owner'], repo_info['repo'], package_name):
                    logging.error(f"Failed to clone {package_name}")
                    continue
                
                # 2. Generate context content with contextmaker
                content = self.generate_context_with_contextmaker(package_name, lib_name, domain)
                
                if content:
                    # Save file
                    self.save_context_file(domain, lib_name, content)
                    total_generated += 1
                    
                    # Pause to avoid overload
                    time.sleep(2)
                else:
                    logging.warning(f"Unable to generate context for {lib_name}")
        
        logging.info(f"Generation complete. {total_generated} new contexts created.")

def main():
    """Main function."""
    generator = ContextGenerator()
    generator.generate_missing_contexts()

if __name__ == "__main__":
    main() 