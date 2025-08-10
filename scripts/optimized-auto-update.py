#!/usr/bin/env python3
"""
Optimized automatic updater for config.json with minimal resource usage.
Only updates when files actually change, includes log rotation.
"""

import os
import json
import time
import logging
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler

class OptimizedAutoUpdater:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.config_file = self.base_dir / "config.json"
        self.context_dir = self.base_dir / "app" / "context"
        self.state_file = self.base_dir / "updater_state.json"
        
        # Setup optimized logging with rotation
        self.setup_logging()
        
        # Load state for change detection
        self.state = self.load_state()
        
    def setup_logging(self):
        """Setup logging with rotation to prevent large log files."""
        log_file = self.base_dir / "optimized_update.log"
        
        # Rotating file handler: max 1MB, keep 3 backups
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=1024*1024,  # 1MB
            backupCount=3
        )
        
        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        
        # Configure formatting
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Setup logger
        self.logger = logging.getLogger('OptimizedUpdater')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def load_state(self):
        """Load previous state for change detection."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "last_check": None,
            "file_hashes": {},
            "last_update": None,
            "check_count": 0
        }
    
    def save_state(self):
        """Save current state."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def get_file_hash(self, filepath):
        """Get MD5 hash of a file."""
        if not filepath.exists():
            return None
        
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def has_context_changes(self):
        """Check if context files have changed since last check."""
        current_hashes = {}
        changes_detected = False
        
        # Scan all context files
        for domain_dir in self.context_dir.iterdir():
            if domain_dir.is_dir():
                for context_file in domain_dir.glob("*.txt"):
                    file_path = str(context_file.relative_to(self.base_dir))
                    current_hash = self.get_file_hash(context_file)
                    current_hashes[file_path] = current_hash
                    
                    # Check if hash changed
                    if self.state["file_hashes"].get(file_path) != current_hash:
                        self.logger.info(f"Change detected: {file_path}")
                        changes_detected = True
        
        # Check for deleted files
        for old_file in self.state["file_hashes"]:
            if old_file not in current_hashes:
                self.logger.info(f"File deleted: {old_file}")
                changes_detected = True
        
        # Update hashes
        self.state["file_hashes"] = current_hashes
        
        return changes_detected
    
    def count_context_files(self):
        """Count context files efficiently."""
        counts = {}
        total = 0
        
        for domain_dir in self.context_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                count = len(list(domain_dir.glob("*.txt")))
                counts[domain] = count
                total += count
        
        return counts, total
    
    def update_config(self):
        """Update config.json only if needed."""
        try:
            script_path = self.base_dir / "scripts" / "update-config-from-contexts.py"
            
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                timeout=30  # Timeout after 30 seconds
            )
            
            if result.returncode == 0:
                if "Changes detected" in result.stdout:
                    self.logger.info("✅ Config updated with changes")
                    self.state["last_update"] = datetime.now().isoformat()
                    return True
                else:
                    # Only log this occasionally to reduce log spam
                    if self.state["check_count"] % 12 == 0:  # Every hour
                        self.logger.info("📄 Config check - no changes needed")
                    return False
            else:
                self.logger.error(f"Config update failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Config update timeout")
            return False
        except Exception as e:
            self.logger.error(f"Config update error: {e}")
            return False
    
    def run_check(self):
        """Run a single optimized check."""
        self.state["check_count"] += 1
        check_num = self.state["check_count"]
        
        # Only log detailed info every hour to reduce log spam
        verbose = (check_num % 12 == 0)
        
        if verbose:
            counts, total = self.count_context_files()
            self.logger.info(f"🔄 Check #{check_num}: {total} context files {counts}")
        
        # Check for changes
        has_changes = self.has_context_changes()
        
        if has_changes:
            self.logger.info("📝 Changes detected, updating config...")
            self.update_config()
        
        # Update state
        self.state["last_check"] = datetime.now().isoformat()
        self.save_state()
        
        return has_changes
    
    def run_continuous(self, interval_minutes: int = 10):
        """Run with optimized intervals."""
        self.logger.info(f"🚀 Starting optimized auto-updater (every {interval_minutes}m)")
        
        while True:
            try:
                self.run_check()
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                self.logger.info("🛑 Stopping optimized updater...")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in check cycle: {e}")
                time.sleep(interval_minutes * 60)

def main():
    import sys
    
    updater = OptimizedAutoUpdater()
    
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        updater.run_check()
    else:
        # Default: run every 10 minutes (more reasonable)
        interval = 10
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except ValueError:
                pass
        
        updater.run_continuous(interval)

if __name__ == "__main__":
    main()
