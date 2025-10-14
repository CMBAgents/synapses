#!/usr/bin/env python3
"""
STEP 7: Réindexation RAG Intelligente (Incrémentale)
- Découpe SEULEMENT les contextes nouveaux/modifiés
- Utilise MD5 pour détecter les changements
- Conserve les chunks existants non modifiés
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import os
import json
import hashlib
from datetime import datetime
import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

# Configuration
CONTEXT_DIR = project_root / "public" / "context"
CHROMA_DIR = project_root / "chroma_db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MODEL_NAME = "all-MiniLM-L6-v2"
REGISTRY_FILE = CHROMA_DIR / "chunk_registry.json"

print("=" * 80)
print(" STEP 7: RAG Reindexing (Incremental)")
print("=" * 80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Vérifier si on est sur GCP (Cloud Run)
is_cloud_run = os.getenv('K_SERVICE') is not None
if is_cloud_run:
    print(" Execution sur Cloud Run detectee")
    print(" ChromaDB non disponible sur GCP - Skip de l'indexation")
    print(" (ChromaDB fonctionne uniquement en local)")
    print()
    print(" Indexation RAG skippee (environment Cloud Run)")
    print("=" * 80)
    sys.exit(0)

# Vérifier les dépendances RAG
try:
    import chromadb
    import sentence_transformers
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print(" Dépendances RAG installées")
except ImportError as e:
    print(" Dépendances RAG manquantes")
    print(f"   Erreur: {e}")
    print()
    print(" Pour installer:")
    print("   pip install -r requirements.txt")
    print()
    print("  Skip de la réindexation RAG")
    sys.exit(0)

# Vérifier le répertoire de contextes
if not CONTEXT_DIR.exists():
    print(f" Répertoire de contextes non trouvé: {CONTEXT_DIR}")
    sys.exit(1)

print(f" Répertoire contextes: {CONTEXT_DIR}")
print(f" Base ChromaDB: {CHROMA_DIR}")
print()

# Charger le registre des chunks (hash MD5 + metadata)
def load_chunk_registry() -> dict:
    """Charge le registre des fichiers déjà chunkés"""
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE, 'r') as f:
            return json.load(f)
    return {"files": {}, "last_update": None}

def save_chunk_registry(registry: dict):
    """Sauvegarde le registre"""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    registry["last_update"] = datetime.now().isoformat()
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2)

def get_file_hash(file_path: Path) -> str:
    """Calcule le hash MD5 d'un fichier"""
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

# Charger le registre
print(" Chargement du registre de chunks...")
registry = load_chunk_registry()
print(f"   • Fichiers déjà indexés: {len(registry['files'])}")
print()

# Charger le modèle d'embedding
print(" Chargement du modèle d'embedding...")
try:
    embedding_model = SentenceTransformer(MODEL_NAME)
    print(f" Modèle chargé: {MODEL_NAME}")
except Exception as e:
    print(f" Erreur chargement modèle: {e}")
    sys.exit(1)

# Initialiser ChromaDB
print("  Initialisation de ChromaDB...")
try:
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # Récupérer ou créer la collection
    try:
        collection = chroma_client.get_collection(name="library_contexts")
        print(" Collection existante récupérée")
    except:
        collection = chroma_client.create_collection(
            name="library_contexts",
            metadata={"description": "Library documentation chunks"}
        )
        print(" Nouvelle collection créée")
    
except Exception as e:
    print(f" Erreur ChromaDB: {e}")
    sys.exit(1)

# Initialiser le text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)

def remove_library_chunks(collection, domain: str, library_name: str):
    """Supprime tous les chunks d'une bibliothèque de ChromaDB"""
    try:
        # Récupérer tous les chunks de cette bibliothèque
        results = collection.get(
            where={"$and": [{"domain": domain}, {"library": library_name}]}
        )
        
        if results and results['ids']:
            # Supprimer par lots
            batch_size = 100
            ids_to_delete = results['ids']
            
            for i in range(0, len(ids_to_delete), batch_size):
                batch_ids = ids_to_delete[i:i+batch_size]
                collection.delete(ids=batch_ids)
            
            return len(ids_to_delete)
        return 0
    except Exception as e:
        print(f"        Erreur suppression: {e}")
        return 0

def process_context_file(file_path: Path, domain: str, registry: dict) -> tuple:
    """
    Traite un fichier de contexte (découpage + indexation)
    Retourne (num_chunks, file_size, status, was_skipped)
    status: "new", "updated", "unchanged", "error"
    """
    library_name = file_path.stem.replace('-context', '')
    file_key = f"{domain}/{library_name}"
    
    # Calculer le hash du fichier
    try:
        current_hash = get_file_hash(file_path)
        file_size = file_path.stat().st_size
    except Exception as e:
        return (0, 0, "error", False)
    
    # Vérifier si le fichier a déjà été indexé
    if file_key in registry["files"]:
        stored_info = registry["files"][file_key]
        
        # Comparer les hash
        if stored_info.get("hash") == current_hash:
            # Fichier inchangé, skip
            return (stored_info.get("chunks", 0), file_size, "unchanged", True)
        else:
            # Fichier modifié, supprimer les anciens chunks
            deleted = remove_library_chunks(collection, domain, library_name)
            status = "updated"
    else:
        status = "new"
    
    # Lire et découper le fichier
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = text_splitter.split_text(content)
        
        # Créer les IDs, textes et métadonnées
        ids = []
        texts = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{domain}_{library_name}_chunk_{i}"
            ids.append(chunk_id)
            texts.append(chunk)
            metadatas.append({
                "domain": domain,
                "library": library_name,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source_file": str(file_path.relative_to(CONTEXT_DIR)),
                "indexed_at": datetime.now().isoformat()
            })
        
        # Créer les embeddings
        embeddings = embedding_model.encode(texts, show_progress_bar=False)
        
        # Ajouter à ChromaDB par lots
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_embeddings = embeddings[i:i+batch_size].tolist()
            
            collection.add(
                ids=batch_ids,
                documents=batch_texts,
                metadatas=batch_metadatas,
                embeddings=batch_embeddings
            )
        
        # Mettre à jour le registre
        registry["files"][file_key] = {
            "hash": current_hash,
            "chunks": len(chunks),
            "size": file_size,
            "indexed_at": datetime.now().isoformat(),
            "status": status
        }
        
        return (len(chunks), file_size, status, False)
        
    except Exception as e:
        print(f"       Erreur: {e}")
        return (0, 0, "error", False)

# Traiter tous les domaines
print()
print(" Analyse et traitement des contextes...")
print("=" * 80)

stats = {
    "total_files": 0,
    "new_files": 0,
    "updated_files": 0,
    "unchanged_files": 0,
    "failed_files": 0,
    "total_chunks": 0,
    "new_chunks": 0,
    "total_size": 0,
    "by_domain": {}
}

domains = ["astronomy", "biochemistry", "finance", "machinelearning"]

for domain in domains:
    domain_path = CONTEXT_DIR / domain
    if not domain_path.exists():
        print(f"  Domaine non trouvé: {domain}")
        continue
    
    context_files = list(domain_path.glob("*.txt"))
    stats["by_domain"][domain] = {
        "files": 0,
        "new": 0,
        "updated": 0,
        "unchanged": 0,
        "failed": 0,
        "chunks": 0,
        "size": 0
    }
    
    print(f"\n {domain.upper()}")
    print(f"   Fichiers: {len(context_files)}")
    
    # Analyser d'abord tous les fichiers
    files_to_process = []
    for file_path in context_files:
        try:
            current_hash = get_file_hash(file_path)
            library_name = file_path.stem.replace('-context', '')
            file_key = f"{domain}/{library_name}"
            
            if file_key in registry["files"]:
                if registry["files"][file_key].get("hash") == current_hash:
                    stats["unchanged_files"] += 1
                    stats["by_domain"][domain]["unchanged"] += 1
                    stats["by_domain"][domain]["files"] += 1
                    stats["total_files"] += 1
                    
                    # Récupérer les infos du registre
                    stored_chunks = registry["files"][file_key].get("chunks", 0)
                    stats["total_chunks"] += stored_chunks
                    stats["by_domain"][domain]["chunks"] += stored_chunks
                    continue
            
            files_to_process.append(file_path)
        except Exception as e:
            print(f"     Erreur lecture {file_path.name}: {e}")
    
    # Afficher le statut
    if files_to_process:
        print(f"    À traiter: {len(files_to_process)} fichiers")
        print(f"    Inchangés: {stats['by_domain'][domain]['unchanged']} fichiers (skip)")
        
        # Traiter les fichiers modifiés/nouveaux
        for file_path in tqdm(files_to_process, desc=f"   Indexation", ncols=80):
            num_chunks, file_size, status, was_skipped = process_context_file(file_path, domain, registry)
            
            stats["total_files"] += 1
            stats["by_domain"][domain]["files"] += 1
            
            if status == "new":
                stats["new_files"] += 1
                stats["new_chunks"] += num_chunks
                stats["by_domain"][domain]["new"] += 1
            elif status == "updated":
                stats["updated_files"] += 1
                stats["new_chunks"] += num_chunks
                stats["by_domain"][domain]["updated"] += 1
            elif status == "error":
                stats["failed_files"] += 1
                stats["by_domain"][domain]["failed"] += 1
            
            if status != "error":
                stats["total_chunks"] += num_chunks
                stats["total_size"] += file_size
                stats["by_domain"][domain]["chunks"] += num_chunks
                stats["by_domain"][domain]["size"] += file_size
    else:
        print(f"    Tous les fichiers sont à jour ({stats['by_domain'][domain]['unchanged']} fichiers)")

# Sauvegarder le registre mis à jour
save_chunk_registry(registry)

# Afficher les statistiques
print()
print("=" * 80)
print(" STATISTIQUES FINALES")
print("=" * 80)
print(f"\n Fichiers analysés: {stats['total_files']}")
print(f"   •  Nouveaux: {stats['new_files']}")
print(f"   •  Mis à jour: {stats['updated_files']}")
print(f"   •  Inchangés (skipped): {stats['unchanged_files']}")
if stats["failed_files"] > 0:
    print(f"   •  Échoués: {stats['failed_files']}")

print(f"\n Chunks:")
print(f"   • Total dans la base: {stats['total_chunks']:,}")
print(f"   • Nouveaux/mis à jour: {stats['new_chunks']:,}")
print(f"   • Gain de temps: {stats['unchanged_files']} fichiers skippés")

if stats["total_size"] > 0:
    print(f"\n Taille traitée: {stats['total_size'] / (1024*1024):.2f} MB")

print(f"\n📐 Configuration:")
print(f"   • Taille chunk: {CHUNK_SIZE} caractères")
print(f"   • Overlap: {CHUNK_OVERLAP} caractères")
print(f"   • Modèle embedding: {MODEL_NAME}")

print(f"\n📈 Par domaine:")
for domain, data in stats["by_domain"].items():
    if data["files"] > 0:
        status_str = ""
        if data["new"] > 0:
            status_str += f"{data['new']} "
        if data["updated"] > 0:
            status_str += f"{data['updated']} "
        if data["unchanged"] > 0:
            status_str += f"{data['unchanged']} "
        
        size_mb = data["size"] / (1024*1024) if data["size"] > 0 else 0
        print(f"   • {domain:20s}: {data['files']:3d} fichiers ({status_str.strip()}) → {data['chunks']:6,d} chunks | {size_mb:.2f} MB")

# Vérifier la collection finale
final_count = collection.count()
print(f"\n Vérification ChromaDB:")
print(f"   • Chunks dans la base: {final_count:,}")

if final_count != stats["total_chunks"]:
    print(f"     Différence détectée: {final_count:,} vs {stats['total_chunks']:,}")
else:
    print(f"    Cohérence vérifiée")

# Sauvegarder les stats globales
stats_file = CHROMA_DIR / "indexing_stats.json"
stats["timestamp"] = datetime.now().isoformat()
stats["model"] = MODEL_NAME
stats["chunk_size"] = CHUNK_SIZE
stats["chunk_overlap"] = CHUNK_OVERLAP
stats["incremental"] = True

with open(stats_file, 'w') as f:
    json.dump(stats, f, indent=2)

print(f"\n Statistiques sauvegardées:")
print(f"   • {stats_file}")
print(f"   • {REGISTRY_FILE}")

# Calculer le gain de temps
if stats["total_files"] > 0:
    skip_percentage = (stats["unchanged_files"] / stats["total_files"]) * 100
    print(f"\n Optimisation:")
    print(f"   • {skip_percentage:.1f}% des fichiers ont été skippés")
    print(f"   • Temps économisé: ~{stats['unchanged_files'] * 2} secondes")

print()
print(" Réindexation RAG terminée avec succès!")
print("=" * 80)
