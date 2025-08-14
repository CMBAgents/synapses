#!/usr/bin/env python3
"""
Script to synchronize contexts with the cloud.
Supports AWS S3, Google Cloud Storage, and other storage services.
"""

import os
import json
import boto3
import logging
from pathlib import Path
from typing import Dict, List, Optional
from google.cloud import storage
import requests
from datetime import datetime
import hashlib

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloud_sync.log'),
        logging.StreamHandler()
    ]
)

class CloudContextSync:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.context_dir = self.base_dir / "public" / "context"
        self.public_context_dir = self.base_dir / "public" / "context"
        
        # Cloud configuration
        self.cloud_config = self.load_cloud_config()
        
        # Initialize cloud clients
        self.s3_client = None
        self.gcs_client = None
        self.init_cloud_clients()

    def load_cloud_config(self) -> Dict:
        """Loads cloud configuration from JSON file."""
        config_file = self.base_dir / "gestion" / "config" / "cloud-config.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "provider": "local",  # local, s3, gcs, azure
                "bucket_name": "cmbagent-contexts",
                "region": "us-east-1",
                "sync_enabled": True,
                "backup_enabled": True,
                "cdn_url": None
            }

    def init_cloud_clients(self):
        """Initializes cloud clients based on configuration."""
        provider = self.cloud_config.get("provider", "local")
        
        if provider == "s3":
            try:
                self.s3_client = boto3.client(
                    's3',
                    region_name=self.cloud_config.get("region", "us-east-1"),
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                )
                logging.info("AWS S3 client initialized")
            except Exception as e:
                logging.error(f"Error initializing S3 client: {e}")
        
        elif provider == "gcs":
            try:
                self.gcs_client = storage.Client()
                logging.info("Google Cloud Storage client initialized")
            except Exception as e:
                logging.error(f"Error initializing GCS client: {e}")

    def get_file_hash(self, filepath: Path) -> str:
        """Calculates MD5 hash of a file."""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def upload_to_s3(self, filepath: Path, key: str) -> bool:
        """Uploads a file to AWS S3."""
        try:
            self.s3_client.upload_file(
                str(filepath),
                self.cloud_config["bucket_name"],
                key,
                ExtraArgs={'ContentType': 'text/plain'}
            )
            logging.info(f"File uploaded to S3: {key}")
            return True
        except Exception as e:
            logging.error(f"Error uploading to S3: {e}")
            return False

    def upload_to_gcs(self, filepath: Path, blob_name: str) -> bool:
        """Uploads a file to Google Cloud Storage."""
        try:
            bucket = self.gcs_client.bucket(self.cloud_config["bucket_name"])
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(str(filepath))
            logging.info(f"File uploaded to GCS: {blob_name}")
            return True
        except Exception as e:
            logging.error(f"Error uploading to GCS: {e}")
            return False

    def upload_to_http(self, filepath: Path, filename: str) -> bool:
        """Uploads a file to an HTTP endpoint (REST API)."""
        try:
            url = self.cloud_config.get("upload_url")
            if not url:
                logging.error("Upload URL not configured")
                return False
            
            with open(filepath, 'rb') as f:
                files = {'file': (filename, f, 'text/plain')}
                response = requests.post(url, files=files)
                
                if response.status_code == 200:
                    logging.info(f"File uploaded via HTTP: {filename}")
                    return True
                else:
                    logging.error(f"HTTP error {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            logging.error(f"Error uploading via HTTP: {e}")
            return False

    def upload_file(self, filepath: Path, domain: str, filename: str) -> bool:
        """Uploads a file according to the configured provider."""
        provider = self.cloud_config.get("provider", "local")
        
        if provider == "local":
            # Local copy to public/context
            dest_path = self.public_context_dir / filename
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            import shutil
            shutil.copy2(filepath, dest_path)
            logging.info(f"File copied locally: {dest_path}")
            return True
        
        elif provider == "s3":
            key = f"contexts/{domain}/{filename}"
            return self.upload_to_s3(filepath, key)
        
        elif provider == "gcs":
            blob_name = f"contexts/{domain}/{filename}"
            return self.upload_to_gcs(filepath, blob_name)
        
        elif provider == "http":
            return self.upload_to_http(filepath, filename)
        
        else:
            logging.error(f"Unsupported provider: {provider}")
            return False

    def get_context_files(self) -> List[Dict]:
        """Gets the list of all context files."""
        context_files = []
        
        for domain_dir in self.context_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                
                for context_file in domain_dir.glob("*.txt"):
                    context_files.append({
                        'domain': domain,
                        'filename': context_file.name,
                        'filepath': context_file,
                        'size': context_file.stat().st_size,
                        'modified': datetime.fromtimestamp(context_file.stat().st_mtime)
                    })
        
        return context_files

    def sync_contexts_to_cloud(self):
        """Synchronizes all contexts to the cloud."""
        if not self.cloud_config.get("sync_enabled", True):
            logging.info("Cloud synchronization disabled")
            return
        
        context_files = self.get_context_files()
        logging.info(f"Found {len(context_files)} context files to synchronize")
        
        success_count = 0
        error_count = 0
        
        for context_file in context_files:
            try:
                if self.upload_file(
                    context_file['filepath'],
                    context_file['domain'],
                    context_file['filename']
                ):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logging.error(f"Error synchronizing {context_file['filename']}: {e}")
                error_count += 1
        
        logging.info(f"Synchronization complete: {success_count} successes, {error_count} errors")

    def create_backup(self):
        """Creates a backup of contexts."""
        if not self.cloud_config.get("backup_enabled", True):
            logging.info("Backup disabled")
            return
        
        backup_dir = self.base_dir / "backups" / f"contexts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        context_files = self.get_context_files()
        
        for context_file in context_files:
            dest_path = backup_dir / context_file['domain'] / context_file['filename']
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            import shutil
            shutil.copy2(context_file['filepath'], dest_path)
        
        logging.info(f"Backup created: {backup_dir}")

    def generate_cdn_urls(self) -> Dict[str, str]:
        """Generates CDN URLs for contexts."""
        cdn_base = self.cloud_config.get("cdn_url")
        if not cdn_base:
            return {}
        
        cdn_urls = {}
        context_files = self.get_context_files()
        
        for context_file in context_files:
            cdn_key = f"contexts/{context_file['domain']}/{context_file['filename']}"
            cdn_urls[cdn_key] = f"{cdn_base}/{cdn_key}"
        
        return cdn_urls

    def update_context_metadata(self):
        """Updates context metadata."""
        metadata = {
            "last_sync": datetime.now().isoformat(),
            "total_files": len(self.get_context_files()),
            "cdn_urls": self.generate_cdn_urls(),
            "cloud_provider": self.cloud_config.get("provider", "local")
        }
        
        metadata_file = self.base_dir / "context-metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logging.info("Context metadata updated")

def main():
    """Main function."""
    syncer = CloudContextSync()
    
    # Create backup
    syncer.create_backup()
    
    # Synchronize to cloud
    syncer.sync_contexts_to_cloud()
    
    # Update metadata
    syncer.update_context_metadata()
    
    logging.info("Cloud synchronization complete")

if __name__ == "__main__":
    main() 