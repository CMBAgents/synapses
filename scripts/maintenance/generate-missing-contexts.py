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

    def normalize_library_name(self, lib_name: str) -> str:
        """Normalizes library name for consistent file naming."""
        # Remove common prefixes and normalize
        normalized = lib_name.replace('/', '-').replace('_', '-').replace('.', '-')
        # Remove duplicate hyphens
        normalized = re.sub(r'-+', '-', normalized)
        # Remove leading/trailing hyphens
        normalized = normalized.strip('-')
        return normalized

    def get_context_filename(self, lib_name: str) -> str:
        """Gets the standardized context filename for a library."""
        normalized_name = self.normalize_library_name(lib_name)
        return f"{normalized_name}-context.txt"

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
        
        # Define output path for context file using normalized name
        output_filename = self.get_context_filename(lib_name)
        output_path = domain_context_dir / output_filename
        
        try:
            # Use contextmaker.make() with the correct API structure
            import contextmaker
            
            logging.info(f"Calling contextmaker.make() for {package_name}")
            logging.info(f"  - library_name: {package_name}")
            logging.info(f"  - output_path: {output_path}")
            logging.info(f"  - input_path: {repo_path}")
            logging.info(f"  - rough: True")
            
            # Use the correct API structure based on the codebase examples
            result = contextmaker.make(
                library_name=package_name,
                output_path=str(output_path),
                input_path=str(repo_path),
                rough=True,
            )
            
            # Check if the file was created
            if output_path.exists():
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
                # Try alternative approach using command line
                logging.warning(f"Context file not found at {output_path}, trying command line approach")
                return self.try_command_line_contextmaker(package_name, lib_name, domain, repo_path, output_path)
                
        except Exception as e:
            logging.error(f"Exception during generation for {package_name}: {e}")
            # Try alternative approach
            fallback_result = self.try_command_line_contextmaker(package_name, lib_name, domain, repo_path, output_path)
            if fallback_result:
                return fallback_result
            
            # If all methods fail, create a non-Sphinx context
            logging.warning(f"All contextmaker methods failed for {package_name}, creating non-Sphinx context")
            non_sphinx_content = self.create_non_sphinx_context(package_name, lib_name, repo_path)
            enhanced_content = self.enhance_context_content(non_sphinx_content, package_name, lib_name)
            
            # Save non-Sphinx content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            logging.info(f"Non-Sphinx context created for {package_name} as final fallback")
            return enhanced_content
        finally:
            # Clean only the temporary repository, NOT the context file
            try:
                import shutil
                shutil.rmtree(repo_path)
                logging.info(f"Temporary repository cleaned: {repo_path}")
            except Exception as e:
                logging.warning(f"Unable to clean temporary repository {repo_path}: {e}")

    def create_fallback_context(self, package_name: str, lib_name: str, repo_path: Path) -> str:
        """Creates a basic fallback context when contextmaker fails."""
        logging.info(f"Creating fallback context for {package_name}")
        
        # Try to extract basic information from the repository
        fallback_content = []
        fallback_content.append(f"# Documentation for {lib_name}")
        fallback_content.append(f"Package: {package_name}")
        fallback_content.append(f"Generated with: fallback method")
        fallback_content.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        fallback_content.append("")
        fallback_content.append("=" * 80)
        fallback_content.append("")
        fallback_content.append(f"# {lib_name}")
        fallback_content.append("")
        fallback_content.append("This context was generated using a fallback method because the primary contextmaker failed.")
        fallback_content.append("")
        
        # Try to read README files
        readme_files = [
            "README.md", "README.rst", "README.txt", "readme.md", "readme.rst", "readme.txt"
        ]
        
        for readme_file in readme_files:
            readme_path = repo_path / readme_file
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        fallback_content.append(f"## README Content")
                        fallback_content.append("")
                        fallback_content.append("```markdown")
                        fallback_content.append(content)
                        fallback_content.append("```")
                        fallback_content.append("")
                        break
                except Exception as e:
                    logging.warning(f"Could not read {readme_file}: {e}")
        
        # Try to extract basic file structure
        try:
            fallback_content.append("## Repository Structure")
            fallback_content.append("")
            fallback_content.append("```")
            for item in sorted(repo_path.iterdir()):
                if item.is_dir():
                    fallback_content.append(f"📁 {item.name}/")
                else:
                    fallback_content.append(f"📄 {item.name}")
            fallback_content.append("```")
            fallback_content.append("")
        except Exception as e:
            logging.warning(f"Could not list repository structure: {e}")
        
        return "\n".join(fallback_content)

    def create_non_sphinx_context(self, package_name: str, lib_name: str, repo_path: Path) -> str:
        """Creates a comprehensive context without using Sphinx."""
        logging.info(f"Creating non-Sphinx context for {package_name}")
        
        context_parts = []
        context_parts.append(f"# Documentation for {lib_name}")
        context_parts.append(f"Package: {package_name}")
        context_parts.append(f"Generated with: non-Sphinx method")
        context_parts.append(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        context_parts.append("")
        context_parts.append("=" * 80)
        context_parts.append("")
        
        # 1. README and documentation files
        context_parts.append("## Documentation Files")
        context_parts.append("")
        
        doc_files = [
            "README.md", "README.rst", "README.txt", "readme.md", "readme.rst", "readme.txt",
            "INSTALL.md", "INSTALL.rst", "INSTALL.txt", "install.md", "install.rst", "install.txt",
            "USAGE.md", "USAGE.rst", "USAGE.txt", "usage.md", "usage.rst", "usage.txt",
            "CHANGELOG.md", "CHANGELOG.rst", "CHANGELOG.txt", "changelog.md", "changelog.rst", "changelog.txt",
            "LICENSE", "LICENSE.md", "LICENSE.txt", "license", "license.md", "license.txt"
        ]
        
        for doc_file in doc_files:
            doc_path = repo_path / doc_file
            if doc_path.exists():
                try:
                    with open(doc_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context_parts.append(f"### {doc_file}")
                        context_parts.append("")
                        context_parts.append("```")
                        context_parts.append(content)
                        context_parts.append("```")
                        context_parts.append("")
                except Exception as e:
                    logging.warning(f"Could not read {doc_file}: {e}")
        
        # 2. Python source code documentation
        context_parts.append("## Python Source Code")
        context_parts.append("")
        
        python_files = []
        for root, dirs, files in os.walk(repo_path):
            # Skip common directories to avoid
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'build', 'dist', 'venv', '.venv']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Sort files and limit to first 20 to avoid huge contexts
        python_files.sort()
        python_files = python_files[:20]
        
        for py_file in python_files:
            try:
                rel_path = os.path.relpath(py_file, repo_path)
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context_parts.append(f"### {rel_path}")
                    context_parts.append("")
                    context_parts.append("```python")
                    context_parts.append(content)
                    context_parts.append("```")
                    context_parts.append("")
            except Exception as e:
                logging.warning(f"Could not read {py_file}: {e}")
        
        # 3. Configuration files
        context_parts.append("## Configuration Files")
        context_parts.append("")
        
        config_files = [
            "setup.py", "setup.cfg", "pyproject.toml", "requirements.txt", "requirements-dev.txt",
            "Makefile", "CMakeLists.txt", "Dockerfile", ".gitignore", "MANIFEST.in"
        ]
        
        for config_file in config_files:
            config_path = repo_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context_parts.append(f"### {config_file}")
                        context_parts.append("")
                        context_parts.append("```")
                        context_parts.append(content)
                        context_parts.append("```")
                        context_parts.append("")
                except Exception as e:
                    logging.warning(f"Could not read {config_file}: {e}")
        
        # 4. Repository structure
        context_parts.append("## Repository Structure")
        context_parts.append("")
        context_parts.append("```")
        
        def list_directory(path, prefix="", max_depth=3, current_depth=0):
            if current_depth > max_depth:
                return
            
            items = sorted(path.iterdir())
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                
                if item.is_dir():
                    context_parts.append(f"{prefix}{current_prefix}{item.name}/")
                    if current_depth < max_depth:
                        new_prefix = prefix + ("    " if is_last else "│   ")
                        list_directory(item, new_prefix, max_depth, current_depth + 1)
                else:
                    context_parts.append(f"{prefix}{current_prefix}{item.name}")
        
        list_directory(repo_path)
        context_parts.append("```")
        context_parts.append("")
        
        return "\n".join(context_parts)

    def try_command_line_contextmaker(self, package_name: str, lib_name: str, domain: str, repo_path: Path, output_path: Path) -> Optional[str]:
        """Try using contextmaker via command line as fallback."""
        try:
            logging.info(f"Trying command line contextmaker for {package_name}")
            
            # Use the command line interface
            cmd = [
                "contextmaker", 
                package_name, 
                "--output", str(output_path),
                "--input-path", str(repo_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0 and output_path.exists():
                logging.info(f"Command line contextmaker succeeded for {package_name}")
                
                # Read content
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add metadata
                enhanced_content = self.enhance_context_content(content, package_name, lib_name)
                
                # Save enhanced content back to the same file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                
                return enhanced_content
            else:
                logging.error(f"Command line contextmaker failed for {package_name}")
                logging.error(f"STDOUT: {result.stdout}")
                logging.error(f"STDERR: {result.stderr}")
                
                # Use non-Sphinx method as final fallback
                logging.info(f"Using non-Sphinx method for {package_name}")
                non_sphinx_content = self.create_non_sphinx_context(package_name, lib_name, repo_path)
                enhanced_content = self.enhance_context_content(non_sphinx_content, package_name, lib_name)
                
                # Save non-Sphinx content
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                
                logging.info(f"Non-Sphinx context created for {package_name}")
                return enhanced_content
                
        except Exception as e:
            logging.error(f"Exception in command line contextmaker for {package_name}: {e}")
            
            # Use non-Sphinx method as final fallback
            logging.info(f"Using non-Sphinx method for {package_name} after exception")
            non_sphinx_content = self.create_non_sphinx_context(package_name, lib_name, repo_path)
            enhanced_content = self.enhance_context_content(non_sphinx_content, package_name, lib_name)
            
            # Save non-Sphinx content
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            logging.info(f"Non-Sphinx context created for {package_name} after exception")
            return enhanced_content

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
        
        # Use normalized filename
        filename = self.get_context_filename(lib_name)
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
                
                # Normalize library name for consistent comparison
                normalized_lib_name = self.normalize_library_name(lib_name)
                
                # Check if context already exists using normalized name
                if normalized_lib_name in existing_libs:
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