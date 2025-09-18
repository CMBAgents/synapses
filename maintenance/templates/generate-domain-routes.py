#!/usr/bin/env python3
"""
Script to automatically generate domain routes based on JSON files in the data directory.
This script analyzes the data directory and generates the necessary Next.js routes for new domains.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def extract_domain_info(json_data: Dict[str, Any], filename: str) -> Dict[str, str]:
    """Extract domain information from JSON data."""
    domain_id = filename.replace('-libraries.json', '')
    
    # Try to extract domain name from the data
    domain_name = json_data.get('domain', domain_id.title())
    
    # Use the domain mappings from configuration
    domain_mappings = {
        'astronomy': 'Astrophysics & Cosmology',
        'biochemistry': 'Biochemistry & Bioinformatics',
        'finance': 'Finance & Trading',
        'machinelearning': 'Machine Learning & AI'
    }
    
    # Use mapped name if available, otherwise use the name from JSON
    display_name = domain_mappings.get(domain_id, domain_name)
    
    # Generate description based on domain
    descriptions = {
        'astronomy': 'Celestial observations, gravitational waves, and cosmic microwave background analysis',
        'biochemistry': 'Molecular dynamics, drug discovery, and computational biology',
        'machinelearning': 'Deep learning, neural networks, and AI model development',
        'finance': 'Portfolio optimization, algorithmic trading, and financial analysis'
    }
    
    description = descriptions.get(domain_id, f'Top libraries in {display_name.lower()}')
    
    return {
        'id': domain_id,
        'name': display_name,
        'description': description,
        'icon': ''
    }

def generate_domain_loader_update(domains: List[Dict[str, str]], data_dir: Path) -> str:
    """Generate the updated domain-loader.ts content."""
    
    # Generate imports
    imports = []
    domain_map_entries = []
    
    for domain in domains:
        domain_id = domain['id']
        filename = f"{domain_id}-libraries.json"
        # Convertir le nom d'import en camelCase valide
        import_name = domain_id.replace('-', '') + "Data"
        
        imports.append(f"import {import_name} from '../data/{filename}';")
        domain_map_entries.append(f"  '{domain_id}': {import_name} as DomainData,")
    
    # Generate the file content
    imports_str = '\n'.join(imports)
    # Générer les fonctions de chargement avec les noms d'import corrects
    loader_functions = []
    for d in domains:
        domain_id = d['id']
        import_name = domain_id.replace('-', '') + "Data"
        function_name = domain_id.replace('-', '') + "Data"
        loader_functions.append(f"export function load{function_name}(): DomainData {{ return {import_name} as DomainData; }}")
    
    loader_functions_str = '\n'.join(loader_functions)
    domains_json = json.dumps(domains, indent=2)
    
    content = f"""{imports_str}

export type LibraryEntry = {{
  rank: number;
  name: string;
  github_url: string;
  stars: number;
  hasContextFile?: boolean;
  contextFileName?: string;
}};

export type DomainData = {{
  libraries: LibraryEntry[];
  domain: string;
  description: string;
  keywords: string[];
}};

// Map of domain IDs to their data
const domainDataMap: Record<string, DomainData> = {{
{chr(10).join(domain_map_entries)}
}};

// Individual loader functions for backward compatibility
{loader_functions_str}

export function getDomainData(domain: string): DomainData {{
  const domainData = domainDataMap[domain];
  if (!domainData) {{
    throw new Error(`Unknown domain: ${{domain}}`);
  }}
  return domainData;
}}

export function getAllDomains(): Array<{{id: string, name: string, description: string, icon: string}}> {{
  return {domains_json};
}}

// Function to check if a domain exists
export function domainExists(domain: string): boolean {{
  return domain in domainDataMap;
}}

// Function to get all available domain IDs
export function getAvailableDomainIds(): string[] {{
  return Object.keys(domainDataMap);
}}
"""
    
    return content

def generate_static_params(domains: List[Dict[str, str]]) -> str:
    """Generate the static params for Next.js routes."""
    domain_params = [f"    {{ domain: '{d['id']}' }}" for d in domains]
    return ",\n".join(domain_params)

def main():
    """Main function to generate domain routes."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    data_dir = project_root / "app" / "data"
    
    if not data_dir.exists():
        print(f"Data directory not found: {data_dir}")
        return
    
    # Find all JSON files in the data directory
    json_files = list(data_dir.glob("*-libraries.json"))
    
    if not json_files:
        print("No library JSON files found in data directory")
        return
    
    print(f"Found {len(json_files)} domain files:")
    for file_path in json_files:
        print(f"  - {file_path.name}")
    
    # Load and analyze each domain
    domains = []
    for file_path in json_files:
        json_data = load_json_file(file_path)
        if json_data:
            domain_info = extract_domain_info(json_data, file_path.name)
            domains.append(domain_info)
            print(f"  ✓ {domain_info['id']}: {domain_info['name']}")
    
    if not domains:
        print("No valid domains found")
        return
    
    # Generate the updated domain-loader.ts
    domain_loader_content = generate_domain_loader_update(domains, data_dir)
    domain_loader_path = project_root / "app" / "utils" / "domain-loader.ts"
    
    # Backup existing file if it exists
    if domain_loader_path.exists():
        backup_path = domain_loader_path.with_suffix('.ts.backup')
        domain_loader_path.rename(backup_path)
        print(f"Backed up existing domain-loader.ts to {backup_path.name}")
    
    # Write new content
    with open(domain_loader_path, 'w', encoding='utf-8') as f:
        f.write(domain_loader_content)
    
    print(f"✓ Updated {domain_loader_path}")
    
    # Generate static params for routes
    static_params = generate_static_params(domains)
    
    # Update chat route
    chat_route_path = project_root / "app" / "chat" / "[domain]" / "page.tsx"
    if chat_route_path.exists():
        with open(chat_route_path, 'r', encoding='utf-8') as f:
            chat_content = f.read()
        
        # Update the static params
        chat_content = re.sub(
            r'return \[\s*\{[^}]*\}\s*,\s*\{[^}]*\}\s*,\s*\{[^}]*\}\s*,\s*\{[^}]*\}\s*\];',
            f'return [\n    {static_params}\n  ];',
            chat_content,
            flags=re.DOTALL
        )
        
        with open(chat_route_path, 'w', encoding='utf-8') as f:
            f.write(chat_content)
        
        print(f"✓ Updated {chat_route_path}")
    
    # Update leaderboard route
    leaderboard_route_path = project_root / "app" / "leaderboard" / "[domain]" / "page.tsx"
    if leaderboard_route_path.exists():
        with open(leaderboard_route_path, 'r', encoding='utf-8') as f:
            leaderboard_content = f.read()
        
        # Update the static params
        leaderboard_content = re.sub(
            r'return \[\s*\{[^}]*\}\s*,\s*\{[^}]*\}\s*,\s*\{[^}]*\}\s*,\s*\{[^}]*\}\s*\];',
            f'return [\n    {static_params}\n  ];',
            leaderboard_content,
            flags=re.DOTALL
        )
        
        with open(leaderboard_route_path, 'w', encoding='utf-8') as f:
            f.write(leaderboard_content)
        
        print(f"✓ Updated {leaderboard_route_path}")
    
    print(f"\n✓ Successfully generated routes for {len(domains)} domains:")
    for domain in domains:
        print(f"  - {domain['id']}: {domain['name']}")
    
    print(f"\nTo add a new domain:")
    print(f"1. Create a JSON file in {data_dir}")
    print(f"2. Run this script again")
    print(f"3. The routes will be automatically generated")

if __name__ == "__main__":
    main()
