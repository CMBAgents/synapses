#!/usr/bin/env python3
"""
Script to automatically install all necessary dependencies
for context generation and synchronization.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Executes a command and displays the result."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def check_python_version():
    """Checks Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("   Python 3.8+ is required")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True

def install_pip_packages():
    """Installs necessary Python packages."""
    packages = [
        "requests",
        "boto3",
        "google-cloud-storage",
        "tqdm",
        "pathlib",
        "typing-extensions",
        "contextmaker",  # Package for documentation extraction
        "schedule"  # Package for scheduling tasks
    ]
    
    print("📦 Installing Python packages...")
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Failed to install {package}")
    
    return True

def install_node_dependencies():
    """Installs Node.js dependencies."""
    if not run_command("npm install", "Installing Node.js dependencies"):
        print("⚠️  Failed to install Node.js dependencies")
        return False
    return True

def setup_environment_variables():
    """Configures environment variables."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("🔧 Creating .env file...")
        
        env_content = """# Configuration for context generation and synchronization

# GitHub Token (optional, to increase rate limiting limits)
# GITHUB_TOKEN=your_github_token_here

# AWS Configuration (for S3)
# AWS_ACCESS_KEY_ID=your_aws_access_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Google Cloud Configuration (for GCS)
# GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json

# Cloud configuration
# CLOUD_PROVIDER=local  # local, s3, gcs, http
# CLOUD_BUCKET=cmbagent-contexts
# CLOUD_REGION=us-east-1
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created")
        print("   Please configure environment variables as needed")
    
    return True

def create_directories():
    """Creates necessary directories."""
    directories = [
        "public/context",
        "public/context/astronomy",
        "public/context/finance",
        "public/context",
        "backups",
        "logs"
    ]
    
    print("📁 Creating directories...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")
    
    return True

def check_cloud_config():
    """Checks and creates cloud configuration if necessary."""
            cloud_config = Path("gestion/config/cloud-config.json")
    
    if not cloud_config.exists():
        print("🔧 Creating default cloud configuration...")
        
        default_config = {
            "provider": "local",
            "bucket_name": "cmbagent-contexts",
            "region": "us-east-1",
            "sync_enabled": True,
            "backup_enabled": True,
            "cdn_url": None,
            "upload_url": None
        }
        
        import json
        with open(cloud_config, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print("✅ Cloud configuration created")
    
    return True

def test_installation():
    """Tests the installation."""
    print("🧪 Testing installation...")
    
    # Test Python
    try:
        import requests
        print("✅ requests - OK")
    except ImportError:
        print("❌ requests - Not installed")
        return False
    
    try:
        import boto3
        print("✅ boto3 - OK")
    except ImportError:
        print("❌ boto3 - Not installed")
        return False
    
    try:
        import contextmaker
        print("✅ contextmaker - OK")
    except ImportError:
        print("❌ contextmaker - Not installed")
        return False
    
    # Test Git
    if not run_command("git --version", "Checking Git"):
        print("❌ Git not found - required for cloning repositories")
        return False
    
    # Test Node.js
    if not run_command("node --version", "Checking Node.js"):
        print("⚠️  Node.js not found")
        return False
    
    if not run_command("npm --version", "Checking npm"):
        print("⚠️  npm not found")
        return False
    
    print("✅ All tests passed")
    return True

def main():
    """Main installation function."""
    print("🚀 Installing dependencies for context generation and synchronization")
    print("="*70)
    
    # Check Python
    if not check_python_version():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Install Python packages
    if not install_pip_packages():
        return False
    
    # Install Node.js dependencies
    if not install_node_dependencies():
        return False
    
    # Configure environment variables
    if not setup_environment_variables():
        return False
    
    # Check cloud configuration
    if not check_cloud_config():
        return False
    
    # Test installation
    if not test_installation():
        return False
    
    print("\n" + "="*70)
    print("✅ Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Configure your environment variables in the .env file")
            print("2. Modify gestion/config/cloud-config.json according to your needs")
    print("3. Run: python scripts/generate-and-sync-all.py")
    print("\n📚 Documentation:")
            print("- gestion/config/cloud-config.json: Cloud storage configuration")
    print("- .env: Environment variables")
    print("- scripts/: Generation and synchronization scripts")
    print("="*70)

if __name__ == "__main__":
    main() 