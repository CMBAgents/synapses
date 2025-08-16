#!/usr/bin/env python3
"""
Script to verify that context files are in the correct structure.
Ensures context files are only in public/context/{domain}/ and not duplicated in public/context/
"""

import os
from pathlib import Path
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('verify_structure.log'),
        logging.StreamHandler()
    ]
)

def verify_context_structure(base_dir: str = "."):
    """Verify that context files are in the correct structure."""
    base_path = Path(base_dir)
    public_context_dir = base_path / "public" / "context"
    
    if not public_context_dir.exists():
        logging.error("public/context directory does not exist")
        return False
    
    # Check for context files in root public/context (should not exist)
    root_context_files = []
    for file in public_context_dir.iterdir():
        if file.is_file() and file.name.endswith('-context.txt'):
            root_context_files.append(file.name)
    
    if root_context_files:
        logging.error(f"❌ Found {len(root_context_files)} context files in public/context root (should not exist):")
        for file in root_context_files:
            logging.error(f"  - {file}")
        return False
    
    # Check domain subdirectories
    domains = ['astronomy', 'finance']
    total_contexts = 0
    
    for domain in domains:
        domain_dir = public_context_dir / domain
        if not domain_dir.exists():
            logging.warning(f"Domain directory {domain}/ does not exist")
            continue
            
        logging.info(f"Checking domain: {domain}")
        
        # Count context files in domain directory
        domain_files = []
        for file in domain_dir.iterdir():
            if file.is_file() and file.name.endswith('-context.txt'):
                domain_files.append(file.name)
        
        logging.info(f"  Found {len(domain_files)} context files in {domain}/")
        total_contexts += len(domain_files)
        
        # List all context files
        for file in sorted(domain_files):
            logging.info(f"    - {file}")
    
    logging.info(f"✅ Structure verification completed. Total contexts: {total_contexts}")
    return True

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify context file structure")
    parser.add_argument("--base-dir", default=".", help="Base directory")
    
    args = parser.parse_args()
    
    print("🔍 Verifying context file structure...")
    success = verify_context_structure(args.base_dir)
    
    if success:
        print("✅ Context structure is correct!")
    else:
        print("❌ Context structure has issues. Check the log for details.")
        exit(1)

if __name__ == "__main__":
    main()
