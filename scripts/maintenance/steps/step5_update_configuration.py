#!/usr/bin/env python3
"""
Étape 5 CORRIGÉE: Mise à jour de la configuration UNIQUEMENT
"""

import subprocess
import sys
from pathlib import Path

def update_library_metadata():
    """Met à jour les métadonnées des bibliothèques"""
    print("📝 Mise à jour des métadonnées...")
    
    try:
        import json
        from pathlib import Path
        
        domains = ['astronomy', 'biochemistry', 'finance', 'machinelearning']
        total_updated = 0
        
        for domain in domains:
            domain_file = Path(__file__).parent.parent.parent.parent / "app" / "data" / f"{domain}-libraries.json"
            if not domain_file.exists():
                continue
                
            with open(domain_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'libraries' not in data:
                continue
                
            domain_updated = 0
            for lib in data['libraries']:
                # Vérifier si le contexte existe
                lib_name = lib.get('name', '').replace('/', '-').replace('_', '-')
                context_file = f"{lib_name}-context.txt"
                context_path = Path(__file__).parent.parent.parent.parent / "public" / "context" / domain / context_file
                
                has_context = context_path.exists()
                if lib.get('hasContextFile', False) != has_context:
                    lib['hasContextFile'] = has_context
                    lib['contextFileName'] = context_file if has_context else None
                    domain_updated += 1
            
            if domain_updated > 0:
                with open(domain_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                total_updated += domain_updated
                print(f"   📝 {domain}: {domain_updated} métadonnées mises à jour")
        
        print(f"✅ {total_updated} métadonnées mises à jour")
        return True
        
    except Exception as e:
        print(f"❌ Erreur mise à jour métadonnées: {e}")
        return False

def regenerate_config():
    """Régénère config.json"""
    print("⚙️ Régénération de config.json...")
    
    try:
        import json
        from pathlib import Path
        
        # Charger les données des domaines
        domains_data = {}
        for domain in ['astronomy', 'biochemistry', 'finance', 'machinelearning']:
            domain_file = Path(__file__).parent.parent.parent.parent / "app" / "data" / f"{domain}-libraries.json"
            if domain_file.exists():
                with open(domain_file, 'r', encoding='utf-8') as f:
                    domains_data[domain] = json.load(f)
        
        # Générer la liste des programmes
        programs = []
        for domain, data in domains_data.items():
            if 'libraries' in data:
                for lib in data['libraries']:
                    if lib.get('hasContextFile', False) and lib.get('contextFileName'):
                        program_id = lib['name'].replace('/', '-')
                        programs.append({
                            "id": program_id,
                            "name": lib['name'].split('/')[-1],
                            "description": f"{lib['name']} - {domain} library with {lib.get('stars', 0)} stars",
                            "contextFiles": [lib['contextFileName']],
                            "docsUrl": lib.get('github_url', ''),
                            "extraSystemPrompt": None
                        })
        
        # Charger le config existant et mettre à jour les programmes
        config_file = Path(__file__).parent.parent.parent.parent / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {}
        
        config['programs'] = programs
        config['defaultProgram'] = programs[0]['id'] if programs else 'default'
        
        # Sauvegarder le config
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ config.json régénéré avec {len(programs)} programmes")
        return True
        
    except Exception as e:
        print(f"❌ Erreur régénération config: {e}")
        return False

def generate_embedded_context():
    """Génère le module embedded-context.ts"""
    print("📦 Génération du module embedded-context.ts...")
    
    try:
        import json
        from pathlib import Path
        
        # Charger les données des domaines
        domains_data = {}
        for domain in ['astronomy', 'biochemistry', 'finance', 'machinelearning']:
            domain_file = Path(__file__).parent.parent.parent.parent / "app" / "data" / f"{domain}-libraries.json"
            if domain_file.exists():
                with open(domain_file, 'r', encoding='utf-8') as f:
                    domains_data[domain] = json.load(f)
        
        # Générer le contenu du module
        embedded_content = "// Generated embedded context module\n"
        embedded_content += "export const embeddedContexts = {\n"
        
        for domain, data in domains_data.items():
            if 'libraries' not in data:
                continue
                
            embedded_content += f"  {domain}: {{\n"
            
            for lib in data['libraries']:
                if lib.get('hasContextFile', False) and lib.get('contextFileName'):
                    lib_name = lib.get('name', '').replace('/', '-').replace('_', '-')
                    context_file = lib.get('contextFileName', '')
                    
                    # Lire le contenu du contexte
                    context_path = Path(__file__).parent.parent.parent.parent / "public" / "context" / domain / context_file
                    if context_path.exists():
                        with open(context_path, 'r', encoding='utf-8') as f:
                            context_content = f.read().replace('`', '\\`').replace('${', '\\${')
                        
                        embedded_content += f"    '{lib_name}': `{context_content}`,\n"
            
            embedded_content += "  },\n"
        
        embedded_content += "};\n"
        
        # Sauvegarder le module
        embedded_file = Path(__file__).parent.parent.parent.parent / "app" / "utils" / "embedded-context.ts"
        embedded_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(embedded_file, 'w', encoding='utf-8') as f:
            f.write(embedded_content)
        
        print("✅ embedded-context.ts généré")
        return True
        
    except Exception as e:
        print(f"❌ Erreur génération embedded: {e}")
        return False

def main():
    """Point d'entrée principal"""
    print("=== ÉTAPE 5: Mise à jour de la configuration ===")
    
    try:
        success = True
        
        # Mise à jour des métadonnées
        if not update_library_metadata():
            success = False
        
        # Régénération de config.json
        if not regenerate_config():
            success = False
        
        # Génération de embedded-context.ts
        if not generate_embedded_context():
            success = False
        
        if success:
            print("✅ Étape 5 terminée")
        else:
            print("❌ Étape 5 échouée")
            sys.exit(1)
        
    except Exception as e:
        print(f"❌ Erreur dans l'étape 5: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
