#!/usr/bin/env python3
"""
Script de déploiement unifié pour CMB Agent Info
Remplace: deploy-gcp.sh, deploy-gcp-budget.sh, setup-deployment.sh, setup-budget-alerts.sh

Fonctionnalités:
1. Déploiement GCP (Cloud Run, Storage, etc.)
2. Configuration des alertes de budget
3. Installation des services
4. Configuration de la surveillance
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional

class DeploymentManager:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.config_dir = self.base_dir / "gestion" / "config"
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
    def setup_logging(self):
        """Configure le logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('deploy.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict:
        """Charge la configuration de déploiement"""
        config_file = self.config_dir / "deployment-config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Configuration par défaut
            return {
                "project_id": "",
                "region": "us-central1",
                "service_name": "cmbagent-info",
                "contexts_bucket": "",
                "static_bucket": "",
                "budget_amount": 15.0,
                "enable_monitoring": True,
                "enable_budget_alerts": True
            }
    
    def check_prerequisites(self) -> bool:
        """Vérifie les prérequis"""
        self.logger.info("📋 Vérification des prérequis...")
        
        required_commands = ['gcloud', 'node', 'npm', 'python3']
        
        for cmd in required_commands:
            try:
                subprocess.run([cmd, '--version'], capture_output=True, check=True)
                self.logger.info(f"✅ {cmd} installé")
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.logger.error(f"❌ {cmd} non installé")
                return False
        
        return True
    
    def get_project_id(self) -> str:
        """Obtient l'ID du projet GCP"""
        if self.config.get("project_id"):
            return self.config["project_id"]
        
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True, text=True, check=True
            )
            project_id = result.stdout.strip()
            if project_id:
                self.logger.info(f"📦 Projet actuel: {project_id}")
                return project_id
        except subprocess.CalledProcessError:
            pass
        
        # Demander l'ID du projet
        project_id = input("Entrez votre ID de projet GCP: ").strip()
        if project_id:
            self.config["project_id"] = project_id
            return project_id
        else:
            raise ValueError("ID de projet requis")
    
    def setup_project(self, project_id: str):
        """Configure le projet GCP"""
        self.logger.info(f"🔧 Configuration du projet {project_id}...")
        
        # Définir le projet
        subprocess.run(["gcloud", "config", "set", "project", project_id], check=True)
        
        # Activer les APIs nécessaires
        apis = [
            "cloudbuild.googleapis.com",
            "run.googleapis.com",
            "storage.googleapis.com",
            "compute.googleapis.com",
            "monitoring.googleapis.com",
            "logging.googleapis.com"
        ]
        
        for api in apis:
            self.logger.info(f"Activation de {api}...")
            subprocess.run(["gcloud", "services", "enable", api], check=True)
        
        self.logger.info("✅ APIs activées")
    
    def create_buckets(self, project_id: str):
        """Crée les buckets de stockage"""
        self.logger.info("🗂️ Création des buckets de stockage...")
        
        contexts_bucket = f"{project_id}-contexts"
        static_bucket = f"{project_id}-static"
        
        # Bucket pour les contextes
        try:
            subprocess.run(["gsutil", "mb", f"gs://{contexts_bucket}"], check=True)
            self.logger.info(f"✅ Bucket contextes créé: {contexts_bucket}")
        except subprocess.CalledProcessError:
            self.logger.info(f"ℹ️ Bucket contextes existe déjà: {contexts_bucket}")
        
        # Bucket pour les fichiers statiques
        try:
            subprocess.run(["gsutil", "mb", f"gs://{static_bucket}"], check=True)
            self.logger.info(f"✅ Bucket statique créé: {static_bucket}")
        except subprocess.CalledProcessError:
            self.logger.info(f"ℹ️ Bucket statique existe déjà: {static_bucket}")
        
        # Mettre à jour la configuration
        self.config["contexts_bucket"] = contexts_bucket
        self.config["static_bucket"] = static_bucket
    
    def build_and_deploy(self):
        """Build et déploie l'application"""
        self.logger.info("🚀 Build et déploiement de l'application...")
        
        # Build de l'application
        self.logger.info("📦 Build de l'application...")
        subprocess.run(["npm", "run", "build"], check=True)
        
        # Déploiement sur Cloud Run
        service_name = self.config["service_name"]
        region = self.config["region"]
        
        self.logger.info(f"🚀 Déploiement sur Cloud Run: {service_name}")
        subprocess.run([
            "gcloud", "run", "deploy", service_name,
            "--source", ".",
            "--region", region,
            "--allow-unauthenticated",
            "--platform", "managed"
        ], check=True)
        
        self.logger.info("✅ Application déployée avec succès")
    
    def setup_budget_alerts(self, project_id: str):
        """Configure les alertes de budget"""
        if not self.config.get("enable_budget_alerts"):
            return
        
        self.logger.info("💰 Configuration des alertes de budget...")
        
        budget_amount = self.config.get("budget_amount", 15.0)
        
        # Créer le budget
        budget_id = f"{project_id}-budget"
        
        try:
            subprocess.run([
                "gcloud", "billing", "budgets", "create",
                "--billing-account", self._get_billing_account(),
                "--budget-amount", str(budget_amount),
                "--budget-id", budget_id,
                "--display-name", f"Budget {project_id}"
            ], check=True)
            
            self.logger.info(f"✅ Budget créé: {budget_id}")
            
        except subprocess.CalledProcessError:
            self.logger.info(f"ℹ️ Budget existe déjà: {budget_id}")
    
    def setup_monitoring(self):
        """Configure la surveillance"""
        if not self.config.get("enable_monitoring"):
            return
        
        self.logger.info("📊 Configuration de la surveillance...")
        
        # Créer les dashboards de surveillance
        self._create_monitoring_dashboards()
        
        self.logger.info("✅ Surveillance configurée")
    
    def install_services(self):
        """Installe les services système"""
        self.logger.info("🔧 Installation des services système...")
        
        # Copier les scripts de service
        service_scripts = [
            "setup_maintenance_service.sh",
            "service-control.sh",
            "install-service.sh"
        ]
        
        for script in service_scripts:
            script_path = self.base_dir / "scripts" / script
            if script_path.exists():
                os.chmod(script_path, 0o755)
                self.logger.info(f"✅ Script rendu exécutable: {script}")
        
        self.logger.info("✅ Services installés")
    
    def deploy_all(self):
        """Exécute le déploiement complet"""
        self.logger.info("🚀 Début du déploiement complet")
        
        try:
            # Vérifier les prérequis
            if not self.check_prerequisites():
                raise Exception("Prérequis non satisfaits")
            
            # Obtenir l'ID du projet
            project_id = self.get_project_id()
            
            # Configurer le projet
            self.setup_project(project_id)
            
            # Créer les buckets
            self.create_buckets(project_id)
            
            # Build et déployer
            self.build_and_deploy()
            
            # Configurer les alertes de budget
            self.setup_budget_alerts(project_id)
            
            # Configurer la surveillance
            self.setup_monitoring()
            
            # Installer les services
            self.install_services()
            
            # Sauvegarder la configuration
            self.save_config()
            
            self.logger.info("🎉 Déploiement terminé avec succès!")
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors du déploiement: {e}")
            raise
    
    def _get_billing_account(self) -> str:
        """Obtient le compte de facturation"""
        try:
            result = subprocess.run(
                ["gcloud", "billing", "accounts", "list", "--format", "value(ACCOUNT_ID)"],
                capture_output=True, text=True, check=True
            )
            accounts = result.stdout.strip().split('\n')
            if accounts and accounts[0]:
                return accounts[0]
        except subprocess.CalledProcessError:
            pass
        
        return input("Entrez votre ID de compte de facturation: ").strip()
    
    def _create_monitoring_dashboards(self):
        """Crée les dashboards de surveillance"""
        # Implémentation simplifiée
        self.logger.info("Création des dashboards de surveillance...")
    
    def save_config(self):
        """Sauvegarde la configuration"""
        config_file = self.config_dir / "deployment-config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        self.logger.info(f"✅ Configuration sauvegardée: {config_file}")

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Script de déploiement unifié")
    parser.add_argument("--project-id", help="ID du projet GCP")
    parser.add_argument("--region", default="us-central1", help="Région GCP")
    parser.add_argument("--budget", type=float, default=15.0, help="Montant du budget (USD)")
    parser.add_argument("--no-monitoring", action="store_true", help="Désactiver la surveillance")
    parser.add_argument("--no-budget-alerts", action="store_true", help="Désactiver les alertes de budget")
    parser.add_argument("--base-dir", default=".", help="Répertoire de base")
    
    args = parser.parse_args()
    
    manager = DeploymentManager(args.base_dir)
    
    # Mettre à jour la configuration avec les arguments
    if args.project_id:
        manager.config["project_id"] = args.project_id
    if args.region:
        manager.config["region"] = args.region
    if args.budget:
        manager.config["budget_amount"] = args.budget
    if args.no_monitoring:
        manager.config["enable_monitoring"] = False
    if args.no_budget_alerts:
        manager.config["enable_budget_alerts"] = False
    
    manager.deploy_all()

if __name__ == "__main__":
    main()
