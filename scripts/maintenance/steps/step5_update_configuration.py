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
                # Utiliser le nom de fichier existant ou construire un nom par défaut
                context_file_name = lib.get('contextFileName')
                if context_file_name:
                    # Vérifier le fichier existant
                    context_path = Path(__file__).parent.parent.parent.parent / "public" / "context" / domain / context_file_name
                    has_context = context_path.exists()
                else:
                    # Fallback : construire le nom si pas de métadonnée
                    lib_name = lib.get('name', '').replace('/', '-').replace('_', '-').replace('.', '-')
                    context_file_name = f"{lib_name}-context.txt"
                    context_path = Path(__file__).parent.parent.parent.parent / "public" / "context" / domain / context_file_name
                    has_context = context_path.exists()
                
                if lib.get('hasContextFile', False) != has_context:
                    lib['hasContextFile'] = has_context
                    lib['contextFileName'] = context_file_name if has_context else None
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
                        program_id = lib['name'].replace('/', '-').replace('_', '-').replace('.', '-').lower()
                        # Gérer le cas où contextFileName est null
                        context_files = [lib['contextFileName']] if lib.get('contextFileName') else []
                        
                        programs.append({
                            "id": program_id,
                            "name": lib['name'].split('/')[-1],
                            "description": f"{lib['name']} - {domain} library with {lib.get('stars', 0)} stars",
                            "contextFiles": context_files,
                            "docsUrl": lib.get('github_url', ''),
                            "extraSystemPrompt": None
                        })
        
        # Charger le config existant et préserver les extraSystemPrompt
        config_file = Path(__file__).parent.parent.parent.parent / "config.json"
        existing_extra_prompts = {}
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Préserver les extraSystemPrompt existants
                if 'programs' in config:
                    for prog in config['programs']:
                        if 'extraSystemPrompt' in prog and prog['extraSystemPrompt'] is not None:
                            existing_extra_prompts[prog['id']] = prog['extraSystemPrompt']
        else:
            config = {}
        
        # Restaurer les extraSystemPrompt existants
        for program in programs:
            if program['id'] in existing_extra_prompts:
                program['extraSystemPrompt'] = existing_extra_prompts[program['id']]
        
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
    """Génère les modules embedded-context-{domain}.ts pour chaque domaine"""
    print("📦 Génération des modules embedded-context-{domain}.ts...")
    
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
        
        total_generated = 0
        
        # Générer un fichier séparé pour chaque domaine
        for domain, data in domains_data.items():
            if 'libraries' not in data:
                continue
            
            print(f"   📦 Génération du module pour le domaine: {domain}")
            
            # Générer le contenu du module pour ce domaine
            embedded_content = f"// Generated embedded context module for {domain.title()} domain\n"
            embedded_content += "export const embeddedContexts = {\n"
            embedded_content += f"  {domain}: {{\n"
            
            domain_generated = 0
            for lib in data['libraries']:
                if lib.get('hasContextFile', False) and lib.get('contextFileName'):
                    lib_name = lib.get('name', '').replace('/', '-').replace('_', '-').replace('.', '-')
                    context_file = lib.get('contextFileName', '')
                    
                    # Lire le contenu du contexte
                    context_path = Path(__file__).parent.parent.parent.parent / "public" / "context" / domain / context_file
                    if context_path.exists():
                        try:
                            with open(context_path, 'r', encoding='utf-8') as f:
                                context_content = f.read()
                                # Escape all special characters that could cause syntax errors in TypeScript template literals
                                context_content = context_content.replace('\\', '\\\\')  # Escape backslashes first
                                context_content = context_content.replace('`', '\\`')    # Escape backticks
                                context_content = context_content.replace('${', '\\${')  # Escape template literal expressions
                            
                            embedded_content += f"    '{lib_name}': `{context_content}`,\n"
                            domain_generated += 1
                        except Exception as e:
                            print(f"      ⚠️ Erreur lecture contexte {lib_name}: {e}")
            
            embedded_content += "  },\n"
            embedded_content += "};\n"
            
            # Sauvegarder le module pour ce domaine
            embedded_file = Path(__file__).parent.parent.parent.parent / "app" / "utils" / f"embedded-context-{domain}.ts"
            embedded_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(embedded_file, 'w', encoding='utf-8') as f:
                f.write(embedded_content)
            
            print(f"   ✅ embedded-context-{domain}.ts généré ({domain_generated} contextes)")
            total_generated += domain_generated
        
        print(f"✅ {total_generated} contextes intégrés générés dans {len(domains_data)} domaines")
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
        
        # Génération de embedded-context.ts (DISABLED - using direct file loading)
        # if not generate_embedded_context():
        #     success = False
        print("📦 Contextes intégrés désactivés - utilisation des fichiers .txt directs")
        
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
