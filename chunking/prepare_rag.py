#!/usr/bin/env python3
"""
Script pour préparer les contextes pour le RAG (VERSION OPTIMISÉE)
- Découpe les contextes en chunks
- Crée les embeddings
- Indexe dans ChromaDB avec optimisations pour réduire la taille
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm

# Configuration
CONTEXT_DIR = Path("public/context")
CHROMA_DIR = Path("chroma_db")
CHUNK_SIZE = 1000  # Caractères par chunk
CHUNK_OVERLAP = 200  # Overlap pour maintenir le contexte
MODEL_NAME = "all-MiniLM-L6-v2"  # Modèle gratuit, rapide, performant

print(" Initialisation du RAG Chunking System")
print("=" * 60)

# 1. Initialiser le modèle d'embedding
print("\n Chargement du modèle d'embedding...")
embedding_model = SentenceTransformer(MODEL_NAME)
print(f" Modèle chargé: {MODEL_NAME}")

# 2. Initialiser ChromaDB avec configuration optimisée
print("\n🔧 Initialisation de ChromaDB (mode optimisé)...")

# Configuration pour minimiser la taille de la DB
chroma_settings = Settings(
    anonymized_telemetry=False,
    allow_reset=True,
)

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR),
    settings=chroma_settings
)

# Créer ou récupérer la collection
try:
    # Supprimer l'ancienne collection si elle existe
    try:
        chroma_client.delete_collection(name="library_contexts")
        print("  ✓ Ancienne collection supprimée")
    except:
        pass
    
    # Créer la collection SANS full-text search
    collection = chroma_client.create_collection(
        name="library_contexts",
        metadata={
            "description": "Library documentation chunks",
            "hnsw:space": "cosine"  # Utiliser cosine similarity
        }
    )
    print("✅ Collection créée: library_contexts (optimisée)")
except Exception as e:
    print(f"❌ Erreur lors de la création de la collection: {e}")
    collection = chroma_client.get_collection(name="library_contexts")

# 3. Initialiser le text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# 4. Traiter tous les fichiers de contexte
def process_context_file(file_path: Path, domain: str) -> int:
    """
    Découpe un fichier de contexte en chunks et l'indexe
    Retourne le nombre de chunks créés
    """
    try:
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraire le nom de la bibliothèque
        library_name = file_path.stem.replace('-context', '')
        
        # Découper en chunks
        chunks = text_splitter.split_text(content)
        
        # Créer les IDs, textes et métadonnées
        ids = []
        texts = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{domain}_{library_name}_chunk_{i}"
            ids.append(chunk_id)
            texts.append(chunk)
            # Métadonnées MINIMALES pour réduire la taille
            metadatas.append({
                "domain": domain,
                "library": library_name,
                "chunk_index": i
            })
        
        # Créer les embeddings
        embeddings = embedding_model.encode(texts, show_progress_bar=False)
        
        # Ajouter à ChromaDB par lots de 100
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
        
        return len(chunks)
        
    except Exception as e:
        print(f" Erreur lors du traitement de {file_path.name}: {e}")
        return 0

# 5. Parcourir tous les domaines et fichiers
print("\n Traitement des contextes...")
print("=" * 60)

stats = {
    "total_files": 0,
    "total_chunks": 0,
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
        "chunks": 0
    }
    
    print(f"\n Traitement du domaine: {domain.upper()}")
    print(f"   Fichiers trouvés: {len(context_files)}")
    
    for file_path in tqdm(context_files, desc=f"  {domain}"):
        num_chunks = process_context_file(file_path, domain)
        
        stats["total_files"] += 1
        stats["total_chunks"] += num_chunks
        stats["by_domain"][domain]["files"] += 1
        stats["by_domain"][domain]["chunks"] += num_chunks

# 6. Afficher les statistiques
print("\n" + "=" * 60)
print(" STATISTIQUES FINALES")
print("=" * 60)
print(f"\n Total de fichiers traités: {stats['total_files']}")
print(f" Total de chunks créés: {stats['total_chunks']}")
print(f" Taille moyenne par chunk: {CHUNK_SIZE} caractères")
print(f" Overlap: {CHUNK_OVERLAP} caractères")

print("\n📈 Par domaine:")
for domain, data in stats["by_domain"].items():
    print(f"  • {domain:20s}: {data['files']:3d} fichiers → {data['chunks']:6d} chunks")

# 7. Optimiser la base de données SQLite
print("\n🗜️  Optimisation de la base de données...")
db_path = CHROMA_DIR / "chroma.sqlite3"

if db_path.exists():
    # Obtenir la taille avant optimisation
    size_before = db_path.stat().st_size / 1024 / 1024
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Supprimer le full-text search (inutile car on utilise les embeddings)
    try:
        cursor.execute("DROP TABLE IF EXISTS embedding_fulltext_search")
        cursor.execute("DROP TABLE IF EXISTS embedding_fulltext_search_data")
        cursor.execute("DROP TABLE IF EXISTS embedding_fulltext_search_idx")
        cursor.execute("DROP TABLE IF EXISTS embedding_fulltext_search_content")
        cursor.execute("DROP TABLE IF EXISTS embedding_fulltext_search_docsize")
        cursor.execute("DROP TABLE IF EXISTS embedding_fulltext_search_config")
        print("  ✓ Full-text search supprimé (inutile)")
    except Exception as e:
        print(f"  ⚠ Full-text search déjà absent: {e}")
    
    # Compacter la base de données
    print("  ⏳ Compactage en cours...")
    cursor.execute("PRAGMA optimize")
    cursor.execute("VACUUM")
    cursor.execute("ANALYZE")
    
    conn.commit()
    conn.close()
    
    # Obtenir la taille après optimisation
    size_after = db_path.stat().st_size / 1024 / 1024
    reduction = ((size_before - size_after) / size_before) * 100 if size_before > 0 else 0
    
    print(f"  ✅ Base de données optimisée:")
    print(f"     Avant:  {size_before:.2f} MB")
    print(f"     Après:  {size_after:.2f} MB")
    print(f"     Gain:   {reduction:.1f}%")

# 8. Sauvegarder les stats
stats_file = CHROMA_DIR / "indexing_stats.json"
with open(stats_file, 'w') as f:
    json.dump(stats, f, indent=2)

print(f"\n💾 Statistiques sauvegardées: {stats_file}")
print("\n✅ Indexation terminée avec succès!")
print("=" * 60)

