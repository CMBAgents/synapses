#!/usr/bin/env python3
import subprocess
import sys
import argparse
from pathlib import Path

class FixedModularMaintenance:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.steps_dir = self.base_dir / "maintenance" / "steps"
        
        # Définir toutes les étapes disponibles (SANS redondance)
        self.all_steps = {
            "step0": "step0_dependencies.py",
            "step1": "step1_update_domains.py", 
            "step2": "step2_update_stars_and_detect_changes.py",  # Mise à jour étoiles + détection
            "step3": "step3_fix_context_names.py",
            "step4": "step4_generate_contexts.py",          # Génération SEULEMENT
            "step7": "step7_reindex_rag.py",                # Réindexation RAG après génération
            "step5": "step5_update_configuration.py",       # Configuration SEULEMENT
            "step6": "step6_cleanup.py"
        }
        
        # Deux modes de maintenance
        self.modes = {
            "quick": ["step0", "step2", "step3", "step4", "step7", "step5", "step6"],  # Mise à jour étoiles + génération contextes + RAG
            "full": ["step0", "step1", "step3", "step4", "step7", "step5", "step6"]  # Découverte + étoiles + génération contextes + RAG
        }
    
    def cleanup_old_logs(self):
        """Nettoie tous les anciens fichiers de logs (garde seulement les 10 plus récents)"""
        logs_dir = self.base_dir / "logs"
        if not logs_dir.exists():
            return
        
        # Récupérer tous les fichiers de log
        log_files = list(logs_dir.glob("*.log"))
        
        if len(log_files) <= 10:
            print("✅ Aucun ancien log à nettoyer")
            return
        
        # Trier par date de modification (plus récent en premier)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Supprimer les anciens (garder les 10 plus récents)
        old_logs = log_files[10:]
        
        if old_logs:
            print("🧹 Nettoyage des anciens logs...")
            for log_file in old_logs:
                try:
                    log_file.unlink()
                    print(f"   🗑️ Supprimé: {log_file.name}")
                except Exception as e:
                    print(f"   ⚠️ Erreur suppression {log_file.name}: {e}")
            print("✅ Anciens logs nettoyés")
    
    def run_step(self, step_name: str) -> bool:
        """Exécute une étape spécifique"""
        if step_name not in self.all_steps:
            print(f"❌ Étape inconnue: {step_name}")
            return False
        
        script_path = self.steps_dir / self.all_steps[step_name]
        if not script_path.exists():
            print(f"❌ Script non trouvé: {script_path}")
            return False
        
        print(f"\n{'='*60}")
        print(f"🔄 Exécution de {step_name}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(
                ["python3", str(script_path)],
                cwd=self.base_dir,
                capture_output=False,  # Afficher les logs en temps réel
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {step_name} terminée avec succès")
                return True
            else:
                print(f"❌ {step_name} échouée (code: {result.returncode})")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de {step_name}: {e}")
            return False
    
    def run_mode(self, mode: str) -> bool:
        """Exécute un mode de maintenance"""
        if mode not in self.modes:
            print(f"❌ Mode inconnu: {mode}")
            print(f"Modes disponibles: {list(self.modes.keys())}")
            return False
        
        # Nettoyer les anciens logs au début
        self.cleanup_old_logs()
        
        steps = self.modes[mode]
        print(f"🚀 Début de la maintenance {mode}")
        print(f"📋 Étapes à exécuter: {', '.join(steps)}")
        
        success_count = 0
        total_steps = len(steps)
        
        for step in steps:
            if self.run_step(step):
                success_count += 1
            else:
                print(f"⚠️ Échec de l'étape {step}, continuation...")
        
        print(f"\n{'='*60}")
        print(f"📊 RÉSUMÉ: {success_count}/{total_steps} étapes réussies")
        print(f"{'='*60}")
        
        if success_count == total_steps:
            print(f"🎉 Maintenance {mode} terminée avec succès!")
            return True
        else:
            print(f"⚠️ Maintenance {mode} terminée avec des erreurs")
            return False
    
    def list_steps(self):
        """Liste toutes les étapes disponibles"""
        print("📋 Étapes disponibles:")
        for step, script in self.all_steps.items():
            print(f"  - {step}: {script}")
        
        print("\n📋 Modes disponibles:")
        for mode, steps in self.modes.items():
            print(f"  - {mode}: {', '.join(steps)}")
        
        print("\n🔍 LOGIQUE DES MODES:")
        print("  - quick: Mise à jour des étoiles + détection GitHub + génération des contextes manquants (quotidien)")
        print("  - full:  Découverte nouvelles bibliothèques + mise à jour étoiles + génération contextes (hebdomadaire)")

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Maintenance modulaire CORRIGÉE - Élimination des redondances",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python3 maintenance_modular_fixed.py --mode quick          # Maintenance rapide (sans détection GitHub)
  python3 maintenance_modular_fixed.py --mode full           # Maintenance complète (avec détection GitHub)
  python3 maintenance_modular_fixed.py --step step2          # Exécuter seulement la détection GitHub
  python3 maintenance_modular_fixed.py --list                # Lister les étapes disponibles
        """
    )
    
    parser.add_argument("--mode", choices=["quick", "full"], help="Mode de maintenance")
    parser.add_argument("--step", help="Exécuter une étape spécifique")
    parser.add_argument("--list", action="store_true", help="Lister les étapes disponibles")
    parser.add_argument("--base-dir", default=".", help="Répertoire de base")
    
    args = parser.parse_args()
    
    maintenance = FixedModularMaintenance(args.base_dir)
    
    if args.list:
        maintenance.list_steps()
    elif args.step:
        success = maintenance.run_step(args.step)
        sys.exit(0 if success else 1)
    elif args.mode:
        success = maintenance.run_mode(args.mode)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
