#!/usr/bin/env python3
"""
Script to automatically update config.json when context files are updated.
Integrates with the existing cloud sync and auto-update systems.
"""

import os
import json
import logging
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import subprocess

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('config_update.log'),
        logging.StreamHandler()
    ]
)

class ConfigUpdater:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.context_dir = self.base_dir / "public" / "context"
        self.data_dir = self.base_dir / "app" / "data"
        self.config_file = self.base_dir / "config.json"
        self.state_file = self.base_dir / "config_update_state.json"
        
        # Load state
        self.state = self.load_state()
        
        # Track file hashes
        self.context_hashes = {}
        self.data_hashes = {}

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
            "context_hashes": {},
            "data_hashes": {},
            "last_update": None,
            "update_count": 0,
            "last_config_hash": None
        }

    def save_state(self):
        """Saves the current state to file."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    def get_file_hash(self, filepath: Path) -> str:
        """Calculates MD5 hash of a file."""
        if not filepath.exists():
            return ""
        
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logging.error(f"Error calculating hash for {filepath}: {e}")
            return ""

    def scan_context_files(self) -> Dict[str, List[str]]:
        """Scans for context files and returns their hashes."""
        context_files = {}
        
        for domain_dir in self.context_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                context_files[domain] = []
                
                for context_file in domain_dir.glob("*.txt"):
                    file_hash = self.get_file_hash(context_file)
                    context_files[domain].append({
                        "filename": context_file.name,
                        "hash": file_hash,
                        "path": str(context_file)
                    })
        
        return context_files

    def scan_data_files(self) -> Dict[str, str]:
        """Scans for data files and returns their hashes."""
        data_files = {}
        
        for data_file in self.data_dir.glob("*.json"):
            if data_file.name in ["astronomy-libraries.json", "finance-libraries.json"]:
                file_hash = self.get_file_hash(data_file)
                data_files[data_file.name] = file_hash
        
        return data_files

    def has_changes(self) -> bool:
        """Checks if there are any changes in context or data files."""
        current_context_files = self.scan_context_files()
        current_data_files = self.scan_data_files()
        
        # Check context files
        for domain, files in current_context_files.items():
            for file_info in files:
                filename = file_info["filename"]
                current_hash = file_info["hash"]
                previous_hash = self.state.get("context_hashes", {}).get(f"{domain}/{filename}")
                
                if current_hash != previous_hash:
                    logging.info(f"Context file changed: {domain}/{filename}")
                    return True
        
        # Check data files
        for filename, current_hash in current_data_files.items():
            previous_hash = self.state.get("data_hashes", {}).get(filename)
            
            if current_hash != previous_hash:
                logging.info(f"Data file changed: {filename}")
                return True
        
        return False

    def update_context_hashes(self):
        """Updates the stored context file hashes."""
        current_context_files = self.scan_context_files()
        
        for domain, files in current_context_files.items():
            for file_info in files:
                filename = file_info["filename"]
                current_hash = file_info["hash"]
                self.state["context_hashes"][f"{domain}/{filename}"] = current_hash

    def update_data_hashes(self):
        """Updates the stored data file hashes."""
        current_data_files = self.scan_data_files()
        
        for filename, current_hash in current_data_files.items():
            self.state["data_hashes"][filename] = current_hash

    def update_library_metadata(self):
        """Updates library metadata in JSON files based on context files."""
        try:
            # Load current data
            astronomy_data = json.load(open(self.data_dir / "astronomy-libraries.json", 'r'))
            finance_data = json.load(open(self.data_dir / "finance-libraries.json", 'r'))
            
            # Scan context files
            context_files = self.scan_context_files()
            
            # Update astronomy libraries
            for lib in astronomy_data["libraries"]:
                lib_name = lib["name"].split("/")[-1]  # Get package name
                context_filename = f"{lib_name}-context.txt"
                
                # Check if context file exists
                has_context = any(
                    file_info["filename"] == context_filename 
                    for file_info in context_files.get("astro", [])
                )
                
                lib["hasContextFile"] = has_context
                if has_context:
                    lib["contextFileName"] = context_filename
            
            # Update finance libraries
            for lib in finance_data["libraries"]:
                lib_name = lib["name"].split("/")[-1]  # Get package name
                context_filename = f"{lib_name}-context.txt"
                
                # Check if context file exists
                has_context = any(
                    file_info["filename"] == context_filename 
                    for file_info in context_files.get("finance", [])
                )
                
                lib["hasContextFile"] = has_context
                if has_context:
                    lib["contextFileName"] = context_filename
            
            # Save updated data
            with open(self.data_dir / "astronomy-libraries.json", 'w') as f:
                json.dump(astronomy_data, f, indent=2)
            
            with open(self.data_dir / "finance-libraries.json", 'w') as f:
                json.dump(finance_data, f, indent=2)
            
            logging.info("Library metadata updated successfully")
            
        except Exception as e:
            logging.error(f"Error updating library metadata: {e}")

    def regenerate_config(self):
        """Regenerates config.json from the updated library data."""
        try:
            # Run the generate script
            script_path = self.base_dir / "scripts" / "generate-programs-from-libraries.py"
            
            if script_path.exists():
                result = subprocess.run(
                    ["python3", str(script_path)],
                    capture_output=True,
                    text=True,
                    cwd=self.base_dir
                )
                
                if result.returncode == 0:
                    logging.info("Config.json regenerated successfully")
                    logging.info(result.stdout)
                else:
                    logging.error(f"Error regenerating config: {result.stderr}")
            else:
                logging.error("Generate script not found")
                
        except Exception as e:
            logging.error(f"Error running generate script: {e}")

    def check_and_update(self, force: bool = False):
        """Main method to check for changes and update config if needed."""
        logging.info("Checking for changes in context and data files...")
        
        if force or self.has_changes():
            if force:
                logging.info("Force update requested, updating configuration...")
            else:
                logging.info("Changes detected, updating configuration...")
            
            # Update library metadata
            self.update_library_metadata()
            
            # Regenerate config.json
            self.regenerate_config()
            
            # Update hashes
            self.update_context_hashes()
            self.update_data_hashes()
            
            # Update state
            self.state["last_update"] = datetime.now().isoformat()
            self.state["update_count"] += 1
            self.save_state()
            
            logging.info("Configuration updated successfully")
        else:
            logging.info("No changes detected")
        
        self.state["last_check"] = datetime.now().isoformat()
        self.save_state()

    def run_continuous(self, interval: int = 300):
        """Runs the updater continuously with specified interval (in seconds)."""
        logging.info(f"Starting continuous config updater (interval: {interval}s)")
        
        while True:
            try:
                self.check_and_update()
                time.sleep(interval)
            except KeyboardInterrupt:
                logging.info("Stopping config updater...")
                break
            except Exception as e:
                logging.error(f"Error in continuous update: {e}")
                time.sleep(interval)

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update config.json from context files")
    parser.add_argument("--continuous", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds (default: 300)")
    parser.add_argument("--base-dir", default=".", help="Base directory")
    parser.add_argument("--force", action="store_true", help="Force update even if no changes detected")
    
    args = parser.parse_args()
    
    updater = ConfigUpdater(args.base_dir)
    
    if args.continuous:
        updater.run_continuous(args.interval)
    else:
        updater.check_and_update(force=args.force)

if __name__ == "__main__":
    main() 