#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

def load_domain_data(domain):
    """Load domain-specific JSON data"""
    json_path = f'app/data/{domain}-libraries.json'
    if not os.path.exists(json_path):
        print(f"❌ JSON file not found for domain: {domain}")
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_existing_context_files(domain):
    """Get list of existing context files for a domain"""
    context_dir = f'app/context/{domain}'
    if not os.path.exists(context_dir):
        return []
    
    context_files = []
    for file in os.listdir(context_dir):
        if file.endswith('.txt'):
            context_files.append(file)
    
    return context_files

def generate_context_for_library(library_name, domain):
    """Generate context file for a specific library"""
    try:
        # Extract package name from library name
        package_name = library_name.split('/')[-1]
        context_dir = f'app/context/{domain}'
        output_file = f'{context_dir}/{package_name}-context.txt'
        
        # Create context directory if it doesn't exist
        os.makedirs(context_dir, exist_ok=True)
        
        # Check if file already exists
        if os.path.exists(output_file):
            print(f"✅ {library_name}: Context file already exists")
            return True
        
        print(f"🔄 Generating context for {library_name}...")
        
        # Run contextmaker command
        command = f"contextmaker {package_name} --output {output_file}"
        print(f"Running: {command}")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            if os.path.exists(output_file):
                print(f"✅ {library_name}: Context file generated successfully")
                return True
            else:
                print(f"❌ {library_name}: Context file not created")
                return False
        else:
            print(f"❌ {library_name}: Error running contextmaker")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {library_name}: Exception - {e}")
        return False

def update_json_with_context_status(domain):
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

def generate_all_missing_contexts(domain):
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
            if generate_context_for_library(library_name, domain):
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
    
    print("🚀 Starting automatic context generation...")
    print("This will generate context files for all libraries that don't have them yet.")
    print("Make sure contextmaker is installed and available in your PATH.\n")
    
    for domain in domains:
        generate_all_missing_contexts(domain)
    
    print("\n✅ Context generation completed!")
    print("All JSON files have been updated with the latest context status.")

if __name__ == "__main__":
    main() 