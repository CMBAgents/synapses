#!/usr/bin/env python3
"""
Exemple d'utilisation de la fonction d'ajout automatique de domaines.
Ce script montre comment ajouter un nouveau domaine en une seule commande.
"""

import subprocess
import sys
from pathlib import Path

def add_physics_domain():
    """Exemple : Ajouter le domaine 'physics' avec des bibliothèques de physique quantique"""
    
    print("🚀 Exemple d'ajout automatique du domaine 'physics'...")
    
    # Commande pour ajouter le domaine physics
    cmd = [
        "python3", "scripts/core/unified-domain-updater.py",
        "--add-domain", "physics",
        "--display-name", "Physics & Quantum Computing",
        "--description", "Top physics and quantum computing libraries for quantum mechanics, quantum algorithms, and quantum information science",
        "--keywords", "physics,quantum,quantum computing,quantum mechanics,quantum algorithms,quantum information,quantum simulation",
        "--specific-libs", "qiskit/qiskit,rigetti/pyquil,quantumlib/Cirq,google/quantum,quantumlib/OpenFermion,quantumlib/OpenFermion-Cirq,quantumlib/ReCirq,quantumlib/QuantumFlow,quantumlib/QuantumFlow-Cirq,quantumlib/QuantumFlow-OpenFermion"
    ]
    
    print(f"Commande exécutée: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, cwd=Path.cwd(), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Domaine 'physics' ajouté avec succès !")
            print("📋 Sortie:")
            print(result.stdout)
        else:
            print("❌ Erreur lors de l'ajout du domaine:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False
    
    return True

def add_chemistry_domain():
    """Exemple : Ajouter le domaine 'chemistry' avec des bibliothèques de chimie computationnelle"""
    
    print("🚀 Exemple d'ajout automatique du domaine 'chemistry'...")
    
    # Commande pour ajouter le domaine chemistry
    cmd = [
        "python3", "scripts/core/unified-domain-updater.py",
        "--add-domain", "chemistry",
        "--display-name", "Chemistry & Computational Chemistry",
        "--description", "Top chemistry and computational chemistry libraries for molecular modeling, drug discovery, and chemical analysis",
        "--keywords", "chemistry,computational chemistry,molecular modeling,drug discovery,chemical analysis,quantum chemistry,molecular dynamics",
        "--specific-libs", "rdkit/rdkit,openbabel/openbabel,mdanalysis/mdanalysis,openmm/openmm,gromacs/gromacs,cp2k/cp2k,nwchemgit/nwchem,psi4/psi4,xtb-python/xtb-python,chemfiles/chemfiles"
    ]
    
    print(f"Commande exécutée: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, cwd=Path.cwd(), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Domaine 'chemistry' ajouté avec succès !")
            print("📋 Sortie:")
            print(result.stdout)
        else:
            print("❌ Erreur lors de l'ajout du domaine:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False
    
    return True

def main():
    """Fonction principale avec menu interactif"""
    
    print("🎯 Système d'Ajout Automatique de Domaines")
    print("=" * 50)
    print()
    print("Choisissez un exemple à exécuter:")
    print("1. Ajouter le domaine 'physics' (quantum computing)")
    print("2. Ajouter le domaine 'chemistry' (computational chemistry)")
    print("3. Quitter")
    print()
    
    while True:
        choice = input("Votre choix (1-3): ").strip()
        
        if choice == "1":
            add_physics_domain()
            break
        elif choice == "2":
            add_chemistry_domain()
            break
        elif choice == "3":
            print("👋 Au revoir !")
            break
        else:
            print("❌ Choix invalide. Veuillez choisir 1, 2 ou 3.")

if __name__ == "__main__":
    main()
