#!/usr/bin/env python3
"""
Script to clean up duplicate context files.
Removes context files from public/context/ that are already in public/context/{domain}/
"""

import os
import shutil
from pathlib import Path
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cleanup_duplicates.log'),
        logging.StreamHandler()
    ]
)

def cleanup_duplicate_contexts(base_dir: str = "."):
    """Clean up duplicate context files."""
    base_path = Path(base_dir)
    public_context_dir = base_path / "public" / "context"
    
    if not public_context_dir.exists():
        logging.info("public/context directory does not exist")
        return
    
    # Get all context files in public/context (root level)
    root_context_files = []
    for file in public_context_dir.iterdir():
        if file.is_file() and file.name.endswith('-context.txt'):
            root_context_files.append(file.name)
    
    if not root_context_files:
        logging.info("No context files found in public/context root")
        return
    
    logging.info(f"Found {len(root_context_files)} context files in public/context root")
    
    # Check each domain subdirectory
    domains = ['astronomy', 'finance']
    files_to_remove = []
    
    for domain in domains:
        domain_dir = public_context_dir / domain
        if not domain_dir.exists():
            continue
            
        logging.info(f"Checking domain: {domain}")
        
        # Get context files in domain directory
        domain_files = []
        for file in domain_dir.iterdir():
            if file.is_file() and file.name.endswith('-context.txt'):
                domain_files.append(file.name)
        
        logging.info(f"  Found {len(domain_files)} context files in {domain}/")
        
        # Find duplicates
        for root_file in root_context_files:
            if root_file in domain_files:
                files_to_remove.append(public_context_dir / root_file)
                logging.info(f"  Found duplicate: {root_file}")
    
    # Remove duplicate files
    if files_to_remove:
        logging.info(f"Removing {len(files_to_remove)} duplicate files...")
        
        for file_path in files_to_remove:
            try:
                file_path.unlink()
                logging.info(f"  Removed: {file_path.name}")
            except Exception as e:
                logging.error(f"  Error removing {file_path.name}: {e}")
        
        logging.info("Cleanup completed successfully")
    else:
        logging.info("No duplicate files found to remove")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up duplicate context files")
    parser.add_argument("--base-dir", default=".", help="Base directory")
    
    args = parser.parse_args()
    
    print("🧹 Starting cleanup of duplicate context files...")
    cleanup_duplicate_contexts(args.base_dir)
    print("✅ Cleanup completed!")

if __name__ == "__main__":
    main()
