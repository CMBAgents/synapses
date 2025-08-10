#!/usr/bin/env python3
import json
import os
import subprocess
import tempfile
from typing import Dict, List

def load_domain_data(domain: str) -> Dict:
    """Load domain-specific JSON data"""
    json_path = f'app/data/{domain}-libraries.json'
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found for domain: {domain}")
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_existing_context_files(domain: str) -> List[str]:
    """Get list of existing context files for a domain"""
    context_dir = f'app/context/{domain}'
    if not os.path.exists(context_dir):
        return []
    
    context_files = []
    for file in os.listdir(context_dir):
        if file.endswith('.txt'):
            context_files.append(file)
    
    return context_files

def clone_repository(github_url: str, temp_dir: str) -> bool:
    """Clone a repository to a temporary directory"""
    try:
        print(f"🔄 Cloning {github_url}...")
        
        # Run git clone command
        result = subprocess.run([
            'git', 'clone', '--depth', '1', github_url, temp_dir
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print(f"✅ Successfully cloned {github_url}")
            return True
        else:
            print(f"❌ Failed to clone {github_url}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout cloning {github_url}")
        return False
    except Exception as e:
        print(f"❌ Exception cloning {github_url}: {e}")
        return False

def check_contextmaker_installed() -> bool:
    """Check if contextmaker is installed and available"""
    try:
        result = subprocess.run(['contextmaker', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def generate_context_with_contextmaker(repo_dir: str, package_name: str, output_path: str) -> bool:
    """Generate context file using contextmaker"""
    try:
        # Check if contextmaker is installed
        if not check_contextmaker_installed():
            print("❌ contextmaker is not installed")
            print("   Please install contextmaker first: pip install contextmaker")
            return False
        
        print(f"🔄 Running contextmaker for {package_name}...")
        
        # Use contextmaker command line with --output to specify exact filename
        
        cmd = [
            'contextmaker', 
            package_name, 
            '--output', output_path,
            '--input-path', repo_dir
        ]
        
        print(f"🔄 Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"✅ Context file generated: {output_path}")
            return True
        else:
            print(f"❌ Context file not created for {package_name}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception running contextmaker for {package_name}: {e}")
        return False

def generate_context_for_library(library: Dict, domain: str) -> bool:
    """Generate context file for a specific library"""
    try:
        library_name = library['name']
        github_url = library['github_url']
        package_name = library_name.split('/')[-1]
        
        # Create context directory if it doesn't exist
        context_dir = f'public/context/{domain}'
        os.makedirs(context_dir, exist_ok=True)
        
        # Check if context file already exists
        output_file = f'{context_dir}/{package_name}-context.txt'
        if os.path.exists(output_file):
            print(f"✅ {library_name}: Context file already exists")
            return True
        
        print(f"🔄 Processing {library_name}...")
        
        # Create temporary directory for cloning
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone the repository
            if not clone_repository(github_url, temp_dir):
                return False
            
            # Generate context using contextmaker
            if generate_context_with_contextmaker(temp_dir, package_name, output_file):
                print(f"✅ {library_name}: Context generation completed")
                return True
            else:
                print(f"❌ {library_name}: Context generation failed")
                return False
                
    except Exception as e:
        print(f"❌ {library_name}: Exception - {e}")
        return False

def update_json_with_context_status(domain: str):
    """Update JSON file to reflect context file status"""
    json_path = f'app/data/{domain}-libraries.json'
    context_dir = f'app/context/{domain}'
    
    if not os.path.exists(json_path):
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get existing context files
    context_files = []
    if os.path.exists(context_dir):
        for file in os.listdir(context_dir):
            if file.endswith('.txt'):
                context_files.append(file)
    
    # Update each library entry
    for library in data['libraries']:
        package_name = library['name'].split('/')[-1]
        context_file_name = f"{package_name}-context.txt"
        
        has_context = context_file_name in context_files
        library['hasContextFile'] = has_context
        
        if has_context:
            library['contextFileName'] = context_file_name
        elif 'contextFileName' in library:
            del library['contextFileName']
    
    # Save updated JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Updated {domain} JSON with context status")

def generate_all_missing_contexts(domain: str):
    """Generate context files for all libraries without context"""
    print(f"\n🔄 Processing {domain} domain...")
    
    data = load_domain_data(domain)
    if not data:
        return
    
    existing_contexts = get_existing_context_files(domain)
    print(f"Found {len(existing_contexts)} existing context files")
    
    missing_count = 0
    success_count = 0
    
    for library in data['libraries']:
        library_name = library['name']
        package_name = library_name.split('/')[-1]
        context_file_name = f"{package_name}-context.txt"
        
        if context_file_name not in existing_contexts:
            missing_count += 1
            if generate_context_for_library(library, domain):
                success_count += 1
    
    print(f"\n📊 {domain} Summary:")
    print(f"   Missing contexts: {missing_count}")
    print(f"   Successfully generated: {success_count}")
    print(f"   Failed: {missing_count - success_count}")
    
    # Update JSON with new context status
    update_json_with_context_status(domain)

def main():
    """Main function to generate missing contexts for all domains"""
    domains = ['astronomy', 'finance']
    
    print("🚀 Starting automatic context generation with Git cloning...")
    print("This will:")
    print("1. Clone repositories that don't have context files")
    print("2. Run contextmaker on the cloned repos")
    print("3. Save context files to public/context/{domain}/")
    print("4. Update JSON files with context status")
    print("\nMake sure contextmaker is installed and available in your PATH.\n")
    
    for domain in domains:
        generate_all_missing_contexts(domain)
    
    print("\n✅ Context generation completed!")
    print("All JSON files have been updated with the latest context status.")

if __name__ == "__main__":
    main() 