#!/usr/bin/env python3
"""
Script de démonstration du nouveau système de classement avec ex-aequo
et inclusion des bibliothèques spécifiques.
"""

def demo_new_ranking_system():
    """
    Démontre le nouveau système de classement.
    """
    print("=== Démonstration du nouveau système de classement ===")
    print("📋 Règles implémentées:")
    print("  1. Classement par nombre d'étoiles décroissant")
    print("  2. Libraries with the same number of stars get attributed the same rank")
    print("  3. Inclusion des bibliothèques spécifiques demandées")
    print("  4. Plus de 100 bibliothèques possibles tout en gardant un classement top 100")
    
    print("\n🔍 Bibliothèques spécifiques à inclure:")
    specific_libs = [
        "cmbagent/cmbagent",
        "cmbant/camb", 
        "cmbant/getdist",
        "CobayaSampler/cobaya"
    ]
    
    for i, lib in enumerate(specific_libs, 1):
        print(f"  {i}. {lib}")
    
    print("\n📊 Exemple de classement avec ex-aequo:")
    
    # Simulation d'un classement avec ex-aequo
    example_ranking = [
        {"name": "python-skyfield", "stars": 1570, "rank": 1},
        {"name": "astrometry.net", "stars": 750, "rank": 2},
        {"name": "astroquery", "stars": 739, "rank": 3},
        {"name": "einsteinpy", "stars": 650, "rank": 4},
        {"name": "lightkurve", "stars": 459, "rank": 5},
        {"name": "gwpy", "stars": 378, "rank": 6},
        {"name": "pycbc", "stars": 346, "rank": 7},
        {"name": "castro", "stars": 322, "rank": 8},
        {"name": "healpy", "stars": 285, "rank": 9},
        {"name": "photutils", "stars": 276, "rank": 10},
        {"name": "class_public", "stars": 267, "rank": 11},
        {"name": "spacepy", "stars": 253, "rank": 12},
        {"name": "presto", "stars": 250, "rank": 13},
        {"name": "cmbant/camb", "stars": 245, "rank": 14},  # Bibliothèque spécifique
        {"name": "cmbant/getdist", "stars": 245, "rank": 14},  # Même nombre d'étoiles
        {"name": "CobayaSampler/cobaya", "stars": 240, "rank": 16},  # Bibliothèque spécifique
        {"name": "cmbagent/cmbagent", "stars": 235, "rank": 17},  # Bibliothèque spécifique
    ]
    
    # Appliquer la logique de classement avec ex-aequo
    current_rank = 1
    for i, lib in enumerate(example_ranking):
        if i > 0 and example_ranking[i]["stars"] < example_ranking[i-1]["stars"]:
            current_rank = i + 1
        lib["rank"] = current_rank
    
    # Afficher le classement
    for lib in example_ranking:
        if any(specific in lib["name"] for specific in ["cmbagent", "cmbant", "CobayaSampler"]):
            print(f"  🎯 Rank {lib['rank']:2d}: {lib['name']:25s} ({lib['stars']:4d} étoiles) [SPÉCIFIQUE]")
        else:
            print(f"  📚 Rank {lib['rank']:2d}: {lib['name']:25s} ({lib['stars']:4d} étoiles)")
    
    print("\n💡 Observations:")
    print("  • Les bibliothèques avec le même nombre d'étoiles ont le même rang")
    print("  • Exemple: camb et getdist (245 étoiles) partagent le rang 14")
    print("  • Les bibliothèques spécifiques sont intégrées naturellement dans le classement")
    print("  • Le système peut contenir plus de 100 bibliothèques tout en gardant un classement top 100")
    
    # Statistiques
    unique_ranks = set(lib["rank"] for lib in example_ranking)
    print(f"\n📈 Statistiques de l'exemple:")
    print(f"  • Nombre total de bibliothèques: {len(example_ranking)}")
    print(f"  • Nombre de rangs uniques: {len(unique_ranks)}")
    print(f"  • Dernier rang: {max(unique_ranks)}")
    print(f"  • Bibliothèques spécifiques incluses: {sum(1 for lib in example_ranking if any(specific in lib['name'] for specific in ['cmbagent', 'cmbant', 'CobayaSampler']))}")

if __name__ == "__main__":
    demo_new_ranking_system()
