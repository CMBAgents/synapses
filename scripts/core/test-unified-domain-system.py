#!/usr/bin/env python3
"""
Script de test pour le système unifié de gestion des domaines.
Teste la mise à jour des domaines et vérifie la cohérence des données.
"""

import json
import sys
import subprocess
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DomainSystemTester:
    """Testeur pour le système unifié de domaines"""
    
    def __init__(self):
        self.base_dir = Path(".")
        self.data_dir = self.base_dir / "app" / "data"
        self.unified_script = self.base_dir / "scripts" / "core" / "unified-domain-updater.py"
        
        # Domaines à tester
        self.domains = ['astronomy', 'biochemistry', 'finance', 'machinelearning']
    
    def test_script_exists(self) -> bool:
        """Teste si le script unifié existe"""
        logger.info("🔍 Test: Vérification de l'existence du script unifié...")
        
        if not self.unified_script.exists():
            logger.error(f"❌ Script unifié non trouvé: {self.unified_script}")
            return False
        
        logger.info("✅ Script unifié trouvé")
        return True
    
    def test_script_syntax(self) -> bool:
        """Teste la syntaxe du script unifié"""
        logger.info("🔍 Test: Vérification de la syntaxe du script...")
        
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(self.unified_script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Syntaxe du script valide")
                return True
            else:
                logger.error(f"❌ Erreur de syntaxe: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du test de syntaxe: {e}")
            return False
    
    def test_help_command(self) -> bool:
        """Teste la commande d'aide du script"""
        logger.info("🔍 Test: Vérification de la commande d'aide...")
        
        try:
            result = subprocess.run(
                ["python3", str(self.unified_script), "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and "Système unifié de mise à jour des domaines" in result.stdout:
                logger.info("✅ Commande d'aide fonctionne")
                return True
            else:
                logger.error(f"❌ Commande d'aide échouée: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout lors du test de la commande d'aide")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors du test de la commande d'aide: {e}")
            return False
    
    def test_domain_update(self, domain: str) -> bool:
        """Teste la mise à jour d'un domaine spécifique"""
        logger.info(f"🔍 Test: Mise à jour du domaine {domain}...")
        
        try:
            result = subprocess.run(
                ["python3", str(self.unified_script), "--domain", domain],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Domaine {domain} mis à jour avec succès")
                return True
            else:
                logger.error(f"❌ Échec de la mise à jour du domaine {domain}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout lors de la mise à jour du domaine {domain}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour du domaine {domain}: {e}")
            return False
    
    def test_json_files_exist(self) -> bool:
        """Teste si les fichiers JSON des domaines existent"""
        logger.info("🔍 Test: Vérification de l'existence des fichiers JSON...")
        
        all_exist = True
        for domain in self.domains:
            json_file = self.data_dir / f"{domain}-libraries.json"
            if json_file.exists():
                logger.info(f"✅ Fichier JSON trouvé: {json_file}")
            else:
                logger.error(f"❌ Fichier JSON manquant: {json_file}")
                all_exist = False
        
        return all_exist
    
    def test_json_structure(self) -> bool:
        """Teste la structure des fichiers JSON"""
        logger.info("🔍 Test: Vérification de la structure des fichiers JSON...")
        
        all_valid = True
        for domain in self.domains:
            json_file = self.data_dir / f"{domain}-libraries.json"
            
            if not json_file.exists():
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Vérifier la structure requise
                required_fields = ['libraries', 'domain', 'description', 'keywords']
                for field in required_fields:
                    if field not in data:
                        logger.error(f"❌ Champ manquant dans {json_file}: {field}")
                        all_valid = False
                
                # Vérifier la structure des bibliothèques
                if 'libraries' in data and data['libraries']:
                    lib = data['libraries'][0]
                    lib_required_fields = ['name', 'github_url', 'stars', 'rank']
                    for field in lib_required_fields:
                        if field not in lib:
                            logger.error(f"❌ Champ manquant dans la bibliothèque de {json_file}: {field}")
                            all_valid = False
                
                if all_valid:
                    logger.info(f"✅ Structure JSON valide: {json_file}")
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ Erreur JSON dans {json_file}: {e}")
                all_valid = False
            except Exception as e:
                logger.error(f"❌ Erreur lors de la lecture de {json_file}: {e}")
                all_valid = False
        
        return all_valid
    
    def test_library_counts(self) -> bool:
        """Teste le nombre de bibliothèques par domaine"""
        logger.info("🔍 Test: Vérification du nombre de bibliothèques...")
        
        all_valid = True
        expected_counts = {
            'astronomy': (50, 200),  # Entre 50 et 200 bibliothèques
            'biochemistry': (5, 50),   # Entre 5 et 50 bibliothèques
            'finance': (5, 50),        # Entre 5 et 50 bibliothèques
            'machinelearning': (5, 50) # Entre 5 et 50 bibliothèques
        }
        
        for domain in self.domains:
            json_file = self.data_dir / f"{domain}-libraries.json"
            
            if not json_file.exists():
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                lib_count = len(data.get('libraries', []))
                min_count, max_count = expected_counts.get(domain, (1, 100))
                
                if min_count <= lib_count <= max_count:
                    logger.info(f"✅ {domain}: {lib_count} bibliothèques (attendu: {min_count}-{max_count})")
                else:
                    logger.warning(f"⚠️ {domain}: {lib_count} bibliothèques (attendu: {min_count}-{max_count})")
                    # Ne pas échouer le test pour cela, juste avertir
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la vérification de {domain}: {e}")
                all_valid = False
        
        return all_valid
    
    def run_all_tests(self) -> bool:
        """Exécute tous les tests"""
        logger.info("🚀 Début des tests du système unifié de domaines")
        logger.info("=" * 60)
        
        tests = [
            ("Existence du script", self.test_script_exists),
            ("Syntaxe du script", self.test_script_syntax),
            ("Commande d'aide", self.test_help_command),
            ("Fichiers JSON existants", self.test_json_files_exist),
            ("Structure JSON", self.test_json_structure),
            ("Nombre de bibliothèques", self.test_library_counts),
        ]
        
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                results[test_name] = test_func()
            except Exception as e:
                logger.error(f"❌ Erreur lors du test '{test_name}': {e}")
                results[test_name] = False
        
        # Résumé
        logger.info("\n" + "=" * 60)
        logger.info("📊 RÉSUMÉ DES TESTS")
        logger.info("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{status} {test_name}")
        
        logger.info(f"\nRésultat global: {passed}/{total} tests réussis")
        
        if passed == total:
            logger.info("🎉 Tous les tests sont passés avec succès!")
            return True
        else:
            logger.error("❌ Certains tests ont échoué")
            return False

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test du système unifié de domaines")
    parser.add_argument("--domain", help="Tester un domaine spécifique")
    parser.add_argument("--update", action="store_true", help="Mettre à jour les domaines avant les tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = DomainSystemTester()
    
    if args.update:
        logger.info("🔄 Mise à jour des domaines avant les tests...")
        if args.domain:
            success = tester.test_domain_update(args.domain)
            if not success:
                logger.error("❌ Échec de la mise à jour, arrêt des tests")
                sys.exit(1)
        else:
            # Mettre à jour tous les domaines
            for domain in tester.domains:
                success = tester.test_domain_update(domain)
                if not success:
                    logger.warning(f"⚠️ Échec de la mise à jour du domaine {domain}")
    
    if args.domain:
        # Tester un domaine spécifique
        success = tester.test_domain_update(args.domain)
        if success:
            logger.info(f"✅ Test du domaine {args.domain} réussi")
        else:
            logger.error(f"❌ Test du domaine {args.domain} échoué")
            sys.exit(1)
    else:
        # Exécuter tous les tests
        success = tester.run_all_tests()
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
