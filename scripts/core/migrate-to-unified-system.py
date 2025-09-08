#!/usr/bin/env python3
"""
Script de migration vers le système unifié de gestion des domaines.
Ce script facilite la transition depuis l'ancien système vers le nouveau.
"""

import json
import shutil
import subprocess
from pathlib import Path
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DomainSystemMigrator:
    """Migrateur vers le système unifié de domaines"""
    
    def __init__(self):
        self.base_dir = Path(".")
        self.data_dir = self.base_dir / "app" / "data"
        self.backup_dir = self.base_dir / "backup_migration"
        self.unified_script = self.base_dir / "scripts" / "core" / "unified-domain-updater.py"
        
        # Créer le dossier de sauvegarde
        self.backup_dir.mkdir(exist_ok=True)
    
    def backup_existing_data(self):
        """Sauvegarde les données existantes"""
        logger.info("💾 Sauvegarde des données existantes...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = self.backup_dir / f"backup_{timestamp}"
        backup_subdir.mkdir(exist_ok=True)
        
        # Fichiers à sauvegarder
        files_to_backup = [
            "app/data/astronomy-libraries.json",
            "app/data/biochemistry-libraries.json",
            "app/data/finance-libraries.json",
            "app/data/machinelearning-libraries.json",
            "config.json",
        ]
        
        for file_path in files_to_backup:
            source = Path(file_path)
            if source.exists():
                dest = backup_subdir / source.name
                shutil.copy2(source, dest)
                logger.info(f"✅ Sauvegardé: {file_path}")
            else:
                logger.info(f"📄 Fichier non trouvé: {file_path}")
        
        logger.info(f"💾 Sauvegarde terminée dans: {backup_subdir}")
        return backup_subdir
    
    def verify_unified_script(self) -> bool:
        """Vérifie que le script unifié existe et fonctionne"""
        logger.info("🔍 Vérification du script unifié...")
        
        if not self.unified_script.exists():
            logger.error(f"❌ Script unifié non trouvé: {self.unified_script}")
            return False
        
        # Tester la syntaxe
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(self.unified_script)],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Erreur de syntaxe dans le script unifié: {result.stderr}")
                return False
            
            logger.info("✅ Script unifié vérifié")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification: {e}")
            return False
    
    def test_unified_script(self) -> bool:
        """Teste le script unifié avec un domaine simple"""
        logger.info("🧪 Test du script unifié...")
        
        try:
            # Tester la commande d'aide
            result = subprocess.run(
                ["python3", str(self.unified_script), "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"❌ Test de la commande d'aide échoué: {result.stderr}")
                return False
            
            logger.info("✅ Test du script unifié réussi")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout lors du test du script unifié")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors du test: {e}")
            return False
    
    def migrate_domain_data(self, domain: str) -> bool:
        """Migre les données d'un domaine vers le nouveau système"""
        logger.info(f"🔄 Migration du domaine {domain}...")
        
        try:
            # Utiliser le script unifié pour mettre à jour le domaine
            result = subprocess.run(
                ["python3", str(self.unified_script), "--domain", domain],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Domaine {domain} migré avec succès")
                return True
            else:
                logger.error(f"❌ Échec de la migration du domaine {domain}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Timeout lors de la migration du domaine {domain}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la migration du domaine {domain}: {e}")
            return False
    
    def update_config_json(self):
        """Met à jour le fichier config.json pour utiliser le nouveau système"""
        logger.info("⚙️ Mise à jour de la configuration...")
        
        config_file = self.base_dir / "config.json"
        if not config_file.exists():
            logger.warning("⚠️ Fichier config.json non trouvé")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Ajouter une note sur le nouveau système
            if 'system_info' not in config:
                config['system_info'] = {}
            
            config['system_info']['unified_domain_system'] = {
                'enabled': True,
                'script': 'scripts/core/unified-domain-updater.py',
                'migration_date': datetime.now().isoformat(),
                'description': 'Système unifié de gestion des domaines avec API GitHub'
            }
            
            # Sauvegarder
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Configuration mise à jour")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la mise à jour de la configuration: {e}")
    
    def verify_migration(self) -> bool:
        """Vérifie que la migration s'est bien déroulée"""
        logger.info("🔍 Vérification de la migration...")
        
        domains = ['astronomy', 'biochemistry', 'finance', 'machinelearning']
        all_valid = True
        
        for domain in domains:
            json_file = self.data_dir / f"{domain}-libraries.json"
            
            if not json_file.exists():
                logger.error(f"❌ Fichier JSON manquant: {json_file}")
                all_valid = False
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Vérifier la structure
                required_fields = ['libraries', 'domain', 'description', 'keywords']
                for field in required_fields:
                    if field not in data:
                        logger.error(f"❌ Champ manquant dans {json_file}: {field}")
                        all_valid = False
                
                # Vérifier le nombre de bibliothèques
                lib_count = len(data.get('libraries', []))
                if lib_count > 0:
                    logger.info(f"✅ {domain}: {lib_count} bibliothèques")
                else:
                    logger.warning(f"⚠️ {domain}: Aucune bibliothèque trouvée")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors de la vérification de {domain}: {e}")
                all_valid = False
        
        return all_valid
    
    def run_migration(self, domains: list = None):
        """Exécute la migration complète"""
        logger.info("🚀 Début de la migration vers le système unifié")
        logger.info("=" * 60)
        
        if domains is None:
            domains = ['astronomy', 'biochemistry', 'finance', 'machinelearning']
        
        # Étape 1: Sauvegarde
        backup_dir = self.backup_existing_data()
        
        # Étape 2: Vérification du script unifié
        if not self.verify_unified_script():
            logger.error("❌ Script unifié non valide, arrêt de la migration")
            return False
        
        if not self.test_unified_script():
            logger.error("❌ Test du script unifié échoué, arrêt de la migration")
            return False
        
        # Étape 3: Migration des domaines
        migration_results = {}
        for domain in domains:
            logger.info(f"\n--- Migration du domaine {domain} ---")
            success = self.migrate_domain_data(domain)
            migration_results[domain] = success
        
        # Étape 4: Mise à jour de la configuration
        self.update_config_json()
        
        # Étape 5: Vérification
        if not self.verify_migration():
            logger.error("❌ Vérification de la migration échouée")
            return False
        
        # Résumé
        logger.info("\n" + "=" * 60)
        logger.info("📊 RÉSUMÉ DE LA MIGRATION")
        logger.info("=" * 60)
        
        successful = sum(1 for success in migration_results.values() if success)
        total = len(migration_results)
        
        for domain, success in migration_results.items():
            status = "✅" if success else "❌"
            logger.info(f"{status} {domain}")
        
        logger.info(f"\nRésultat: {successful}/{total} domaines migrés avec succès")
        logger.info(f"💾 Sauvegarde disponible dans: {backup_dir}")
        
        if successful == total:
            logger.info("🎉 Migration terminée avec succès!")
            return True
        else:
            logger.error("❌ Migration partiellement échouée")
            return False

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migration vers le système unifié de domaines")
    parser.add_argument("--domains", nargs="+", help="Domaines à migrer (par défaut: tous)")
    parser.add_argument("--backup-only", action="store_true", help="Sauvegarder seulement")
    parser.add_argument("--verify-only", action="store_true", help="Vérifier seulement")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    migrator = DomainSystemMigrator()
    
    if args.backup_only:
        migrator.backup_existing_data()
    elif args.verify_only:
        success = migrator.verify_migration()
        if not success:
            sys.exit(1)
    else:
        success = migrator.run_migration(args.domains)
        if not success:
            sys.exit(1)

if __name__ == "__main__":
    main()
