import csv
import json

def filter_cosmo_astro_repos(
    input_csv="app/update_bdd/ascl_repos_with_stars.csv",
    output_csv="app/update_bdd/top_astronomy_cosmology_repos.csv"
):
    keywords = [
        "astro", "astropy", "healpy", "photutils", "sky", "gal", "cosmo", "cmb",
        "planck", "tardis", "lightkurve", "astroquery", "pypeit", "poppy", "stellar",
        "galsim", "ultranest", "pymultinest", "zeus", "radis", "astronn", "presto", 
        "astroplan", "sep", "specutils", "s2fft", "stingray",
        "spacepy", "pycbc", "gwpy", "einsteinpy", "simonsobs", "cmbant", "lesgourg/class_public",
    ]

    filtered_repos = []

    # Lecture du CSV existant
    with open(input_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            url = row["github_url"].lower()
            if any(keyword in url for keyword in keywords):
                filtered_repos.append({
                    "github_url": row["github_url"],
                    "stars": row["stars"]
                })

    # Écriture du nouveau CSV filtré
    with open(output_csv, mode="w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=["github_url", "stars"])
        writer.writeheader()
        for repo in filtered_repos:
            writer.writerow(repo)

    print(f"CSV généré : {output_csv} ({len(filtered_repos)} dépôts filtrés)")

def get_top_starred_repos(
    input_csv="app/update_bdd/top_astronomy_cosmology_repos.csv",
    output_csv="app/update_bdd/avantdernier.csv",
    top_n=100
):
    repos = []

    # Lire le fichier CSV
    with open(input_csv, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                repos.append({
                    "url": "https://" + row["github_url"].strip(),
                    "stars": int(row["stars"])
                })
            except (KeyError, ValueError):
                continue  # ignore lignes malformées

    # Trier par nombre d'étoiles (décroissant)
    repos.sort(key=lambda r: r["stars"], reverse=True)

    # Garder les top N
    top_repos = repos[:top_n]

    # Écrire dans le nouveau CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8") as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["github_url", "stars"])  # entêtes

        for repo in top_repos:
            writer.writerow([repo["url"], repo["stars"]])

    print(f"CSV généré : {output_csv} ({len(top_repos)} dépôts)")

def extract_repo_name(github_url):
    """
    Extrait 'owner/repo' à partir d'une URL GitHub.
    """
    if not github_url.startswith("http"):
        return None
    parts = github_url.strip("/").split("/")
    if len(parts) < 2:
        return None
    return "/".join(parts[-2:])

def extract_and_write_repos_with_names():
    """
    Lit un CSV avec GitHub URLs et étoiles,
    écrit un nouveau CSV avec 'nom_librairie', 'url', 'stars'.
    """
    input_csv = "app/update_bdd/avantdernier.csv"
    output_csv = "app/update_bdd/last.csv"
    with open(input_csv, newline='', encoding='utf-8') as infile, \
         open(output_csv, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        writer.writerow(['library_name', 'github_url', 'stars'])

        for row in reader:
            if not row or not row[0].startswith("http"):
                continue
            repo_name = extract_repo_name(row[0])
            if repo_name:
                writer.writerow([repo_name, row[0], row[1]])

    print(f"CSV généré : {output_csv}")

def clean():
    """
    Nettoie les fichiers temporaires.
    """
    import os
    files_to_clean = [
        "app/update_bdd/top_astronomy_cosmology_repos.csv",
        "app/update_bdd/avantdernier.csv"
    ]
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"Fichier supprimé : {file}")

def update_astronomy_json():
    """
    Met à jour le fichier astronomy-libraries.json à partir du CSV généré.
    """
    json_path = "app/data/astronomy-libraries.json"
    csv_path = "app/update_bdd/last.csv"

    # Lire le CSV
    new_libs = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                name = row['library_name']
                url = row['github_url']
                stars = int(row['stars'])
                new_libs.append({
                    "name": name,
                    "github_url": url,
                    "stars": stars
                })
            except (KeyError, ValueError):
                continue  # Ignore lignes incomplètes ou corrompues

    # Trier par nombre d'étoiles décroissant
    new_libs.sort(key=lambda x: -x["stars"])

    # Ajouter les rangs
    for i, lib in enumerate(new_libs, 1):
        lib["rank"] = i

    # Créer le format astronomy-libraries.json
    astronomy_data = {
        "libraries": new_libs,
        "domain": "astronomy",
        "description": "Top astronomy and cosmology libraries for celestial observations, gravitational waves, and cosmic microwave background analysis",
        "keywords": ["astronomy", "cosmology", "astrophysics", "gravitational waves", "CMB", "healpy", "astropy"]
    }

    # Sauvegarder le nouveau JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(astronomy_data, f, indent=2, ensure_ascii=False)

    print(f"Fichier astronomy-libraries.json mis à jour avec {len(new_libs)} librairies")

def update_libraries_json():
    """
    Met à jour le fichier libraries.json principal.
    """
    json_path = "app/data/libraries.json"
    csv_path = "app/update_bdd/last.csv"
    category = "astronomy"

    # Lire le CSV
    new_libs = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                name = row['library_name']
                url = row['github_url']
                stars = int(row['stars'])
                new_libs.append({
                    "name": name,
                    "github_url": url,
                    "stars": stars
                })
            except (KeyError, ValueError):
                continue  # Ignore lignes incomplètes ou corrompues

    # Trier par nombre d'étoiles décroissant
    new_libs.sort(key=lambda x: -x["stars"])

    # Ajouter les rangs
    for i, lib in enumerate(new_libs, 1):
        lib["rank"] = i

    # Lire le JSON existant
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Mettre à jour la catégorie
    data[category] = new_libs

    # Sauvegarder le nouveau JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"'{category}' updated with {len(new_libs)} libraries in {json_path}")

def main():
    """
    Fonction principale pour mettre à jour les données astronomie.
    """
    print("=== Mise à jour des données astronomie ===")
    
    # Filtrer les dépôts cosmo/astro
    filter_cosmo_astro_repos()

    # Obtenir les 100 dépôts les plus étoilés
    get_top_starred_repos()

    # Extraire les noms de dépôts
    extract_and_write_repos_with_names()

    # Nettoyer les fichiers temporaires
    clean()

    # Mettre à jour les fichiers JSON
    update_astronomy_json()
    update_libraries_json()

    print("Mise à jour terminée !")

if __name__ == "__main__":
    main()