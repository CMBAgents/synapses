#!/usr/bin/env python3
"""
Script de mise à jour rapide pour tester le système.
Options simplifiées pour des tests rapides.
"""

import sys
from pathlib import Path
import argparse

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from update_all_domains import DomainUpdater, DOMAIN_CONFIGS

def show_available_domains():
    """Affiche les domaines disponibles"""
    print("🌐 DOMAINES DISPONIBLES:")
    print("=" * 50)
    
    for domain, config in DOMAIN_CONFIGS.items():
        approach = "ASCL" if config["use_ascl"] else "GitHub API"
        status = "✅" if config["use_ascl"] else "🆕"
        print(f"{status} {domain:20} → {approach}")
    
    print(f"\nTotal: {len(DOMAIN_CONFIGS)} domaines configurés")

def quick_update_domain(domain: str, dry_run: bool = False):
    """Mise à jour rapide d'un domaine"""
    if domain not in DOMAIN_CONFIGS:
        print(f"❌ Domaine '{domain}' non configuré")
        show_available_domains()
        return False
    
    config = DOMAIN_CONFIGS[domain]
    approach = "ASCL" if config["use_ascl"] else "GitHub API"
    
    print(f"🚀 Mise à jour du domaine: {domain}")
    print(f"📡 Approche: {approach}")
    print(f"🔍 Mots-clés: {len(config['keywords'])} configurés")
    
    if dry_run:
        print("🔍 MODE DRY RUN - Aucune mise à jour réelle")
        print(f"   Fichier de sortie: app/data/{domain}-libraries.json")
        print(f"   Librairies spécifiques: {len(config['specific_libs'])}")
        return True
    
    try:
        updater = DomainUpdater()
        
        if config["use_ascl"]:
            print("📚 Utilisation du système ASCL existant...")
            updater.update_astronomy_domain()
        else:
            print("🔍 Utilisation de l'API GitHub...")
            updater.update_github_domain(domain, config)
        
        print(f"✅ Domaine {domain} mis à jour avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        return False

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Mise à jour rapide des domaines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 quick_update.py --list                    # Lister les domaines
  python3 quick_update.py --domain finance          # Mettre à jour finance
  python3 quick_update.py --domain finance --dry    # Test sans mise à jour
  python3 quick_update.py --test                    # Test de tous les domaines
        """
    )
    
    parser.add_argument("--domain", help="Domaine à mettre à jour")
    parser.add_argument("--list", action="store_true", help="Lister les domaines disponibles")
    parser.add_argument("--dry", action="store_true", help="Mode dry run (pas de vraie mise à jour)")
    parser.add_argument("--test", action="store_true", help="Test de tous les domaines (dry run)")
    
    args = parser.parse_args()
    
    if args.list:
        show_available_domains()
        return
    
    if args.test:
        print("🧪 TEST DE TOUS LES DOMAINES (DRY RUN)")
        print("=" * 50)
        
        success_count = 0
        for domain in DOMAIN_CONFIGS.keys():
            print(f"\n--- Test du domaine: {domain} ---")
            if quick_update_domain(domain, dry_run=True):
                success_count += 1
        
        print(f"\n📊 RÉSULTATS DU TEST:")
        print(f"   ✅ Succès: {success_count}/{len(DOMAIN_CONFIGS)}")
        print(f"   ❌ Échecs: {len(DOMAIN_CONFIGS) - success_count}/{len(DOMAIN_CONFIGS)}")
        return
    
    if args.domain:
        success = quick_update_domain(args.domain, dry_run=args.dry)
        if success:
            print(f"\n🎉 Mise à jour du domaine '{args.domain}' terminée!")
        else:
            print(f"\n💥 Échec de la mise à jour du domaine '{args.domain}'")
            sys.exit(1)
    else:
        print("❌ Veuillez spécifier un domaine ou utiliser --list pour voir les options")
        parser.print_help()

if __name__ == "__main__":
    main()
