#!/usr/bin/env python3
"""
Main script to generate and synchronize all contexts.
Orchestrates the complete process of generation and cloud storage.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('generate_and_sync.log'),
        logging.StreamHandler()
    ]
)

class ContextOrchestrator:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.scripts_dir = self.base_dir / "scripts"
        
        # Load configuration
        self.config = self.load_config()
        
        # Statistics
        self.stats = {
            "start_time": datetime.now(),
            "contexts_generated": 0,
            "contexts_synced": 0,
            "errors": 0
        }

    def load_config(self) -> Dict:
        """Loads configuration from config.json and cloud-config.json."""
        config = {}
        
        # Load main config.json
        config_file = self.base_dir / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config.update(json.load(f))
        
        # Load cloud-config.json
        cloud_config_file = self.base_dir / "gestion" / "config" / "cloud-config.json"
        if cloud_config_file.exists():
            with open(cloud_config_file, 'r', encoding='utf-8') as f:
                config['cloud'] = json.load(f)
        
        return config

    def run_script(self, script_name: str, args: List[str] = None) -> bool:
        """Executes a Python script."""
        script_path = self.scripts_dir / script_name
        
        if not script_path.exists():
            logging.error(f"Script not found: {script_path}")
            return False
        
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        try:
            logging.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                logging.info(f"Script {script_name} executed successfully")
                if result.stdout:
                    logging.info(f"Output: {result.stdout}")
                return True
            else:
                logging.error(f"Error executing {script_name}")
                logging.error(f"STDERR: {result.stderr}")
                return False
        except Exception as e:
            logging.error(f"Exception executing {script_name}: {e}")
            return False

    def update_libraries_data(self):
        """Updates library data from ASCL."""
        logging.info("=== Updating library data ===")
        
        # Execute ASCL scraping script
        if self.run_script("update-domain-data.py"):
            logging.info("✅ ASCL data updated")
        else:
            logging.error("❌ Error updating ASCL data")

    def generate_missing_contexts(self):
        """Generates missing contexts."""
        logging.info("=== Generating missing contexts ===")
        
        if self.run_script("generate-missing-contexts.py"):
            logging.info("✅ Missing contexts generated")
        else:
            logging.error("❌ Error generating contexts")

    def sync_to_cloud(self):
        """Synchronizes contexts to cloud."""
        logging.info("=== Cloud synchronization ===")
        
        if self.run_script("cloud-sync-contexts.py"):
            logging.info("✅ Cloud synchronization complete")
        else:
            logging.error("❌ Error during cloud synchronization")

    def build_contexts(self):
        """Builds contexts for the application."""
        logging.info("=== Building contexts ===")
        
        if self.run_script("build-context.js"):
            logging.info("✅ Contexts built")
        else:
            logging.error("❌ Error building contexts")

    def generate_context_module(self):
        """Generates context module."""
        logging.info("=== Generating context module ===")
        
        if self.run_script("generate-context-module.js"):
            logging.info("✅ Context module generated")
        else:
            logging.error("❌ Error generating context module")

    def validate_contexts(self):
        """Validates generated contexts."""
        logging.info("=== Validating contexts ===")
        
        context_dir = self.base_dir / "app" / "context"
        total_files = 0
        valid_files = 0
        
        for domain_dir in context_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                domain_files = 0
                domain_valid = 0
                
                for context_file in domain_dir.glob("*.txt"):
                    domain_files += 1
                    total_files += 1
                    
                    # Check file size
                    file_size = context_file.stat().st_size
                    if file_size > 1000:  # At least 1KB
                        domain_valid += 1
                        valid_files += 1
                    else:
                        logging.warning(f"File too small: {context_file}")
                
                logging.info(f"Domain {domain}: {domain_valid}/{domain_files} valid files")
        
        logging.info(f"Total: {valid_files}/{total_files} valid files")
        return valid_files > 0

    def create_summary_report(self):
        """Creates a summary report."""
        end_time = datetime.now()
        duration = end_time - self.stats["start_time"]
        
        report = {
            "execution_date": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "stats": self.stats,
            "config": {
                "provider": self.config.get("cloud", {}).get("provider", "local"),
                "sync_enabled": self.config.get("cloud", {}).get("sync_enabled", True)
            }
        }
        
        report_file = self.base_dir / "execution_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Summary report created: {report_file}")
        
        # Display summary
        print("\n" + "="*50)
        print("SUMMARY REPORT")
        print("="*50)
        print(f"Execution duration: {duration}")
        print(f"Contexts generated: {self.stats['contexts_generated']}")
        print(f"Contexts synchronized: {self.stats['contexts_synced']}")
        print(f"Errors: {self.stats['errors']}")
        print("="*50)

    def run_full_pipeline(self):
        """Executes the complete pipeline."""
        logging.info("🚀 Starting complete context generation and synchronization pipeline")
        
        try:
            # 1. Update library data
            self.update_libraries_data()
            
            # 2. Generate missing contexts
            self.generate_missing_contexts()
            
            # 3. Validate contexts
            if not self.validate_contexts():
                logging.error("❌ Context validation failed")
                self.stats["errors"] += 1
                return False
            
            # 4. Build contexts
            self.build_contexts()
            
            # 5. Generate context module
            self.generate_context_module()
            
            # 6. Synchronize to cloud
            self.sync_to_cloud()
            
            logging.info("✅ Complete pipeline finished successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error during pipeline execution: {e}")
            self.stats["errors"] += 1
            return False
        finally:
            # Create summary report
            self.create_summary_report()

def main():
    """Main function."""
    orchestrator = ContextOrchestrator()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "update-data":
            orchestrator.update_libraries_data()
        elif command == "generate":
            orchestrator.generate_missing_contexts()
        elif command == "sync":
            orchestrator.sync_to_cloud()
        elif command == "build":
            orchestrator.build_contexts()
        elif command == "validate":
            orchestrator.validate_contexts()
        else:
            print("Available commands:")
            print("  update-data  - Update library data")
            print("  generate     - Generate missing contexts")
            print("  sync         - Synchronize to cloud")
            print("  build        - Build contexts")
            print("  validate     - Validate contexts")
            print("  full         - Execute complete pipeline")
    else:
        # Execute complete pipeline by default
        orchestrator.run_full_pipeline()

if __name__ == "__main__":
    main() 