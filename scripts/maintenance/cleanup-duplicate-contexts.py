#!/usr/bin/env python3
"""
Script to clean up duplicate context files and keep the longest one for each library.
Also updates JSON files after each context modification.
"""

import os
import shutil
import json
import requests
from pathlib import Path
import logging
from typing import Dict, List, Tuple

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_duplicates.log'),
        logging.StreamHandler()
    ]
)

class ContextCleanupManager:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.public_context_dir = self.base_dir / "public" / "context"
        self.data_dir = self.base_dir / "app" / "data"
        self.logger = logging.getLogger(__name__)
        
    def get_library_name_from_filename(self, filename: str) -> str:
        """Extract library name from context filename."""
        # Remove -context.txt suffix
        if filename.endswith('-context.txt'):
            return filename[:-14]  # Remove "-context.txt"
        elif filename.endswith('.txt'):
            return filename[:-4]   # Remove ".txt"
        return filename
    
    def find_context_files_for_library(self, library_name: str) -> List[Path]:
        """Find all context files for a specific library across all domains."""
        context_files = []
        
        # Search in all domain directories
        for domain_dir in self.public_context_dir.iterdir():
            if domain_dir.is_dir():
                for file in domain_dir.iterdir():
                    if file.is_file() and file.name.endswith('.txt'):
                        file_lib_name = self.get_library_name_from_filename(file.name)
                        if file_lib_name == library_name:
                            context_files.append(file)
        
        return context_files
    
    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        try:
            return file_path.stat().st_size
        except:
            return 0
    
    def cleanup_duplicate_contexts_for_library(self, library_name: str) -> bool:
        """Clean up duplicate contexts for a specific library, keeping the longest one."""
        context_files = self.find_context_files_for_library(library_name)
        
        if len(context_files) <= 1:
            return False  # No duplicates to clean
        
        self.logger.info(f"Found {len(context_files)} context files for library '{library_name}':")
        for file in context_files:
            size = self.get_file_size(file)
            self.logger.info(f"  - {file.name}: {size} bytes")
        
        # Find the longest file
        longest_file = max(context_files, key=self.get_file_size)
        self.logger.info(f"Keeping longest file: {longest_file.name} ({self.get_file_size(longest_file)} bytes)")
        
        # Remove other files
        files_removed = []
        for file in context_files:
            if file != longest_file:
                try:
                    file.unlink()
                    files_removed.append(file.name)
                    self.logger.info(f"  Removed: {file.name}")
                except Exception as e:
                    self.logger.error(f"  Error removing {file.name}: {e}")
        
        if files_removed:
            self.logger.info(f"Cleaned up {len(files_removed)} duplicate files for '{library_name}'")
            return True
        
        return False
    
    def update_json_after_context_change(self, domain: str):
        """Update JSON file after context changes via API."""
        try:
            api_url = f"http://localhost:3000/api/context?domain={domain}&action=updateLibrariesWithContextStatus"
            response = requests.get(api_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.logger.info(f"✅ JSON updated for domain {domain} via API")
                    return True
                else:
                    self.logger.error(f"❌ API returned error for {domain}: {data.get('error')}")
            else:
                self.logger.error(f"❌ HTTP {response.status_code} for {domain}")
                
        except Exception as e:
            self.logger.error(f"❌ Error updating JSON for {domain}: {e}")
        
        return False
    
    def cleanup_all_duplicates(self):
        """Clean up all duplicate contexts across all libraries."""
        self.logger.info("🧹 Starting cleanup of duplicate context files...")
        
        # Get all unique library names from context files
        all_libraries = set()
        for domain_dir in self.public_context_dir.iterdir():
            if domain_dir.is_dir():
                for file in domain_dir.iterdir():
                    if file.is_file() and file.name.endswith('.txt'):
                        lib_name = self.get_library_name_from_filename(file.name)
                        all_libraries.add(lib_name)
        
        self.logger.info(f"Found {len(all_libraries)} unique libraries with context files")
        
        # Clean up duplicates for each library
        libraries_cleaned = 0
        total_files_removed = 0
        
        for library_name in sorted(all_libraries):
            if self.cleanup_duplicate_contexts_for_library(library_name):
                libraries_cleaned += 1
                # Update JSON for affected domains
                self.update_json_after_context_change("astronomy")
                self.update_json_after_context_change("finance")
        
        self.logger.info(f"✅ Cleanup completed: {libraries_cleaned} libraries cleaned")
        return libraries_cleaned
    
    def cleanup_duplicate_contexts_legacy(self):
        """Legacy cleanup: Remove context files from public/context root that are in domain subdirs."""
        if not self.public_context_dir.exists():
            self.logger.info("public/context directory does not exist")
            return
        
        # Get all context files in public/context (root level)
        root_context_files = []
        for file in self.public_context_dir.iterdir():
            if file.is_file() and file.name.endswith('-context.txt'):
                root_context_files.append(file.name)
        
        if not root_context_files:
            self.logger.info("No context files found in public/context root")
            return
        
        self.logger.info(f"Found {len(root_context_files)} context files in public/context root")
        
        # Check each domain subdirectory
        domains = ['astronomy', 'finance']
        files_to_remove = []
        
        for domain in domains:
            domain_dir = self.public_context_dir / domain
            if not domain_dir.exists():
                continue
                
            self.logger.info(f"Checking domain: {domain}")
            
            # Get context files in domain directory
            domain_files = []
            for file in domain_dir.iterdir():
                if file.is_file() and file.name.endswith('.txt'):
                    domain_files.append(file.name)
            
            self.logger.info(f"  Found {len(domain_files)} context files in {domain}/")
            
            # Find duplicates
            for root_file in root_context_files:
                if root_file in domain_files:
                    files_to_remove.append(self.public_context_dir / root_file)
                    self.logger.info(f"  Found duplicate: {root_file}")
        
        # Remove duplicate files
        if files_to_remove:
            self.logger.info(f"Removing {len(files_to_remove)} duplicate files...")
            
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                    self.logger.info(f"  Removed: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"  Error removing {file_path.name}: {e}")
            
            self.logger.info("Legacy cleanup completed successfully")
            
            # Update JSON files after cleanup
            self.update_json_after_context_change("astronomy")
            self.update_json_after_context_change("finance")
        else:
            self.logger.info("No duplicate files found to remove")

def cleanup_duplicate_contexts(base_dir: str = "."):
    """Main cleanup function."""
    manager = ContextCleanupManager(base_dir)
    
    # First do legacy cleanup (root level duplicates)
    manager.cleanup_duplicate_contexts_legacy()
    
    # Then do advanced cleanup (keep longest for each library)
    manager.cleanup_all_duplicates()

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up duplicate context files and keep longest ones")
    parser.add_argument("--base-dir", default=".", help="Base directory")
    parser.add_argument("--legacy-only", action="store_true", help="Only do legacy cleanup")
    parser.add_argument("--advanced-only", action="store_true", help="Only do advanced cleanup")
    
    args = parser.parse_args()
    
    print("🧹 Starting advanced cleanup of duplicate context files...")
    
    if args.legacy_only:
        manager = ContextCleanupManager(args.base_dir)
        manager.cleanup_duplicate_contexts_legacy()
    elif args.advanced_only:
        manager = ContextCleanupManager(args.base_dir)
        manager.cleanup_all_duplicates()
    else:
        cleanup_duplicate_contexts(args.base_dir)
    
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    main()
