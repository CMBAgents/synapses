#!/usr/bin/env python3
"""
Script pour ajouter facilement un nouveau domaine au système.
Utilise les modèles prédéfinis et permet la personnalisation.
"""

import sys
import json
from pathlib import Path
import argparse

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from domain_templates import (
    DOMAIN_TEMPLATES, 
    get_template, 
    create_custom_domain, 
    validate_domain_config
)
from update_all_domains import DOMAIN_CONFIGS

def show_existing_domains():
    """Affiche les domaines existants"""
    print("🌐 DOMAINES EXISTANTS:")
    print("=" * 40)
    for domain in DOMAIN_CONFIGS.keys():
        print(f"   - {domain}")
    print(f"\nTotal: {len(DOMAIN_CONFIGS)} domaines")

def show_available_templates():
    """Affiche les modèles disponibles"""
    print("📚 MODÈLES DISPONIBLES:")
    print("=" * 40)
    for template in DOMAIN_TEMPLATES.keys():
        print(f"   - {template}")
    print(f"\nTotal: {len(DOMAIN_TEMPLATES)} modèles")

def add_domain_from_template(template_name: str, custom_name: str = None):
    """Ajoute un domaine en utilisant un modèle"""
    if template_name not in DOMAIN_TEMPLATES:
        print(f"❌ Modèle '{template_name}' non trouvé")
        return False
    
    # Utiliser le nom du modèle si aucun nom personnalisé n'est fourni
    domain_name = custom_name or template_name
    
    if domain_name in DOMAIN_CONFIGS:
        print(f"❌ Le domaine '{domain_name}' existe déjà")
        return False
    
    # Récupérer le modèle
    template = DOMAIN_TEMPLATES[template_name]
    
    # Créer la configuration du domaine
    domain_config = {
        "use_ascl": template["use_ascl"],
        "keywords": template["keywords"].copy(),
        "description": template["description"],
        "specific_libs": template["specific_libs"].copy()
    }
    
    # Ajouter au système
    DOMAIN_CONFIGS[domain_name] = domain_config
    
    print(f"✅ Domaine '{domain_name}' ajouté avec succès!")
    print(f"   - Basé sur le modèle: {template_name}")
    print(f"   - Mots-clés: {len(domain_config['keywords'])}")
    print(f"   - Utilise ASCL: {domain_config['use_ascl']}")
    
    return True

def add_custom_domain(
    name: str, 
    keywords: list, 
    description: str, 
    specific_libs: list = None,
    use_ascl: bool = False
):
    """Ajoute un domaine personnalisé"""
    if name in DOMAIN_CONFIGS:
        print(f"❌ Le domaine '{name}' existe déjà")
        return False
    
    # Créer la configuration
    domain_config = create_custom_domain(name, keywords, description, specific_libs, use_ascl)
    
    # Valider la configuration
    is_valid, errors = validate_domain_config(domain_config)
    if not is_valid:
        print("❌ Configuration invalide:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    # Ajouter au système
    DOMAIN_CONFIGS[name] = domain_config
    
    print(f"✅ Domaine personnalisé '{name}' ajouté avec succès!")
    print(f"   - Mots-clés: {len(keywords)}")
    print(f"   - Utilise ASCL: {use_ascl}")
    
    return True

def save_domain_configs():
    """Sauvegarde la configuration des domaines dans un fichier"""
    config_file = Path(__file__).parent / "domain_configs_backup.json"
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(DOMAIN_CONFIGS, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Configuration sauvegardée dans: {config_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

def interactive_add_domain():
    """Ajoute un domaine de manière interactive"""
    print("🎯 AJOUT INTERACTIF D'UN DOMAINE")
    print("=" * 50)
    
    # Demander le nom du domaine
    domain_name = input("Nom du domaine (ex: web_development): ").strip()
    if not domain_name:
        print("❌ Nom de domaine requis")
        return False
    
    if domain_name in DOMAIN_CONFIGS:
        print(f"❌ Le domaine '{domain_name}' existe déjà")
        return False
    
    # Choisir entre modèle et personnalisé
    print("\nChoisir l'approche:")
    print("1. Utiliser un modèle existant")
    print("2. Créer un domaine personnalisé")
    
    choice = input("Votre choix (1 ou 2): ").strip()
    
    if choice == "1":
        # Utiliser un modèle
        show_available_templates()
        template_name = input("Nom du modèle à utiliser: ").strip()
        
        if template_name in DOMAIN_TEMPLATES:
            return add_domain_from_template(template_name, domain_name)
        else:
            print(f"❌ Modèle '{template_name}' non trouvé")
            return False
    
    elif choice == "2":
        # Créer un domaine personnalisé
        print("\nConfiguration du domaine personnalisé:")
        
        # Mots-clés
        keywords_input = input("Mots-clés (séparés par des virgules): ").strip()
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        if not keywords:
            print("❌ Au moins un mot-clé est requis")
            return False
        
        # Description
        description = input("Description du domaine: ").strip()
        if not description:
            print("❌ Description requise")
            return False
        
        # Librairies spécifiques
        specific_libs_input = input("Librairies spécifiques (séparées par des virgules, optionnel): ").strip()
        specific_libs = [lib.strip() for lib in specific_libs_input.split(",") if lib.strip()]
        
        # Utiliser ASCL
        use_ascl_input = input("Utiliser ASCL ? (y/n, défaut: n): ").strip().lower()
        use_ascl = use_ascl_input in ['y', 'yes', 'oui', 'o']
        
        return add_custom_domain(domain_name, keywords, description, specific_libs, use_ascl)
    
    else:
        print("❌ Choix invalide")
        return False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Ajouter un nouveau domaine au système",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 add_new_domain.py --list                    # Lister les domaines existants
  python3 add_new_domain.py --templates               # Lister les modèles disponibles
  python3 add_new_domain.py --template web_dev        # Ajouter depuis un modèle
  python3 add_new_domain.py --custom                  # Ajouter un domaine personnalisé
  python3 add_new_domain.py --interactive             # Mode interactif
        """
    )
    
    parser.add_argument("--list", action="store_true", help="Lister les domaines existants")
    parser.add_argument("--templates", action="store_true", help="Lister les modèles disponibles")
    parser.add_argument("--template", help="Ajouter un domaine depuis un modèle")
    parser.add_argument("--custom", action="store_true", help="Ajouter un domaine personnalisé")
    parser.add_argument("--interactive", action="store_true", help="Mode interactif")
    parser.add_argument("--save", action="store_true", help="Sauvegarder la configuration")
    
    args = parser.parse_args()
    
    if args.list:
        show_existing_domains()
        return
    
    if args.templates:
        show_available_templates()
        return
    
    if args.template:
        success = add_domain_from_template(args.template)
        if success and args.save:
            save_domain_configs()
        return
    
    if args.custom:
        print("🎯 AJOUT D'UN DOMAINE PERSONNALISÉ")
        print("=" * 50)
        
        domain_name = input("Nom du domaine: ").strip()
        keywords_input = input("Mots-clés (séparés par des virgules): ").strip()
        description = input("Description: ").strip()
        
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        success = add_custom_domain(domain_name, keywords, description)
        if success and args.save:
            save_domain_configs()
        return
    
    if args.interactive:
        success = interactive_add_domain()
        if success and args.save:
            save_domain_configs()
        return
    
    if args.save:
        save_domain_configs()
        return
    
    # Aucun argument fourni, afficher l'aide
    parser.print_help()

if __name__ == "__main__":
    main()
