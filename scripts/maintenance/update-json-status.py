#!/usr/bin/env python3
"""
Script de maintenance pour mettre à jour le statut des contextes dans les JSON.
Utilise la nouvelle API context pour des mises à jour sûres et fiables.
"""

import requests
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configuration des domaines
DOMAINS = ["astronomy", "finance"]

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('json_status_update.log'),
        logging.StreamHandler()
    ]
)

class JSONStatusUpdater:
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        
    def update_domain_status(self, domain: str) -> bool:
        """Met à jour le statut des contextes pour un domaine via l'API"""
        api_url = f"{self.base_url}/api/context?domain={domain}&action=updateLibrariesWithContextStatus"
        
        self.logger.info(f"Mise à jour du domaine: {domain}")
        self.logger.info(f"API: {api_url}")
        
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success"):
                self.logger.info(f"✅ Domaine {domain} mis à jour avec succès")
                
                # Afficher les statistiques
                if "data" in data and "libraries" in data["data"]:
                    libraries = data["data"]["libraries"]
                    with_context = sum(1 for lib in libraries if lib.get("hasContextFile", False))
                    total = len(libraries)
                    percentage = (with_context / total * 100) if total > 0 else 0
                    
                    self.logger.info(f"   📊 Statistiques: {with_context}/{total} contextes ({percentage:.1f}%)")
                    
                    # Afficher quelques exemples
                    context_examples = [lib["name"] for lib in libraries if lib.get("hasContextFile", False)][:5]
                    if context_examples:
                        self.logger.info(f"   📁 Exemples de contextes: {', '.join(context_examples)}")
                
                return True
            else:
                self.logger.error(f"❌ Échec de la mise à jour: {data.get('error', 'Erreur inconnue')}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Erreur de connexion à l'API: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la mise à jour: {e}")
            return False
    
    def update_all_domains(self) -> Dict[str, bool]:
        """Met à jour tous les domaines et retourne les résultats"""
        self.logger.info("🚀 DÉBUT DE LA MISE À JOUR DE TOUS LES DOMAINES")
        self.logger.info("=" * 60)
        
        results = {}
        
        for domain in DOMAINS:
            self.logger.info(f"\n--- Mise à jour du domaine: {domain} ---")
            success = self.update_domain_status(domain)
            results[domain] = success
            
            # Pause entre les domaines pour éviter la surcharge
            if domain != DOMAINS[-1]:  # Pas de pause après le dernier
                time.sleep(1)
        
        # Résumé final
        self.logger.info(f"\n📊 RÉSUMÉ FINAL:")
        self.logger.info("=" * 40)
        
        success_count = sum(results.values())
        total_count = len(results)
        
        for domain, success in results.items():
            status = "✅" if success else "❌"
            self.logger.info(f"{status} {domain}: {'Succès' if success else 'Échec'}")
        
        self.logger.info(f"\n🎯 Total: {success_count}/{total_count} domaines mis à jour avec succès")
        
        if success_count == total_count:
            self.logger.info("🎉 Tous les domaines ont été mis à jour avec succès!")
        else:
            self.logger.warning("⚠️  Certains domaines n'ont pas pu être mis à jour")
        
        return results
    
    def verify_server_status(self) -> bool:
        """Vérifie que le serveur Next.js est accessible"""
        try:
            health_url = f"{self.base_url}/api/health"
            response = requests.get(health_url, timeout=10)
            return response.status_code == 200
        except:
            return False

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Mise à jour du statut des contextes via l'API context",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 update-json-status.py                    # Mettre à jour tous les domaines
  python3 update-json-status.py --domain astronomy # Mettre à jour un domaine spécifique
  python3 update-json-status.py --url http://localhost:3001  # Autre serveur
  python3 update-json-status.py --check            # Vérifier le statut du serveur
        """
    )
    
    parser.add_argument("--domain", help="Domaine spécifique à mettre à jour")
    parser.add_argument("--url", default="http://localhost:3000", help="URL du serveur Next.js")
    parser.add_argument("--check", action="store_true", help="Vérifier le statut du serveur")
    
    args = parser.parse_args()
    
    updater = JSONStatusUpdater(args.url)
    
    # Vérifier le statut du serveur
    if not updater.verify_server_status():
        print(f"❌ Serveur inaccessible sur {args.url}")
        print("💡 Assurez-vous que le serveur Next.js est démarré")
        sys.exit(1)
    
    print(f"✅ Serveur accessible sur {args.url}")
    
    if args.check:
        print("🔍 Vérification du statut du serveur terminée")
        return
    
    if args.domain:
        if args.domain not in DOMAINS:
            print(f"❌ Domaine '{args.domain}' non supporté")
            print(f"   Domaines disponibles: {', '.join(DOMAINS)}")
            sys.exit(1)
        
        success = updater.update_domain_status(args.domain)
        if not success:
            sys.exit(1)
    else:
        # Mettre à jour tous les domaines
        results = updater.update_all_domains()
        
        # Code de sortie basé sur les résultats
        if not all(results.values()):
            sys.exit(1)

if __name__ == "__main__":
    main()
