#!/usr/bin/env python3
"""
Module de recherche sémantique pour le RAG
Utilisé par l'API Next.js pour récupérer les chunks pertinents
"""

import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Optional

class RAGRetriever:
    """Classe pour effectuer des recherches sémantiques dans les contextes"""
    
    def __init__(self, chroma_dir: str = "chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialise le retriever
        
        Args:
            chroma_dir: Chemin vers la base ChromaDB
            model_name: Nom du modèle d'embedding
        """
        self.chroma_dir = Path(chroma_dir)
        self.model_name = model_name
        
        # Charger le modèle d'embedding
        self.embedding_model = SentenceTransformer(model_name)
        
        # Connecter à ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=str(self.chroma_dir))
        self.collection = self.chroma_client.get_collection(name="library_contexts")
    
    def search(
        self, 
        query: str, 
        library: Optional[str] = None,
        domain: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Recherche sémantique dans les chunks
        
        Args:
            query: Question de l'utilisateur
            library: Nom de la bibliothèque (optionnel, filtre les résultats)
            domain: Nom du domaine (optionnel, filtre les résultats)
            top_k: Nombre de chunks à retourner
        
        Returns:
            Liste de dictionnaires avec les chunks pertinents
        """
        # Créer l'embedding de la query
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Construire les filtres
        where_filter = {}
        if library:
            where_filter["library"] = library
        if domain:
            where_filter["domain"] = domain
        
        # Recherche dans ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter if where_filter else None
        )
        
        # Formater les résultats
        chunks = []
        if results and results['documents']:
            for i in range(len(results['documents'][0])):
                chunk = {
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None,
                    "id": results['ids'][0][i]
                }
                chunks.append(chunk)
        
        return chunks
    
    def get_context_for_library(
        self,
        library: str,
        query: str,
        top_k: int = 5,
        max_tokens: int = 8000
    ) -> str:
        """
        Récupère le contexte optimal pour une bibliothèque donnée
        
        Args:
            library: Nom de la bibliothèque
            query: Question de l'utilisateur
            top_k: Nombre de chunks à récupérer
            max_tokens: Limite de tokens pour le contexte
        
        Returns:
            Contexte formaté en string
        """
        # Rechercher les chunks pertinents
        chunks = self.search(query=query, library=library, top_k=top_k)
        
        if not chunks:
            return ""
        
        # Construire le contexte
        context_parts = []
        total_chars = 0
        max_chars = max_tokens * 4  # Approximation: 1 token ≈ 4 chars
        
        for chunk in chunks:
            chunk_text = chunk['text']
            chunk_size = len(chunk_text)
            
            if total_chars + chunk_size > max_chars:
                # Tronquer le dernier chunk si nécessaire
                remaining = max_chars - total_chars
                if remaining > 200:  # Garder seulement si suffisamment de place
                    context_parts.append(chunk_text[:remaining] + "...")
                break
            
            context_parts.append(chunk_text)
            total_chars += chunk_size
        
        # Joindre avec des séparateurs
        context = "\n\n---\n\n".join(context_parts)
        
        return context
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques de la base"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "model": self.model_name,
            "chroma_dir": str(self.chroma_dir)
        }

# Fonction utilitaire pour l'API
def retrieve_context(
    library: str,
    query: str,
    top_k: int = 5,
    max_tokens: int = 8000
) -> str:
    """
    Fonction simple pour récupérer le contexte
    Utilisée par l'API Next.js
    
    Args:
        library: Nom de la bibliothèque (ex: "pixell", "astropy-astropy")
        query: Question de l'utilisateur
        top_k: Nombre de chunks à récupérer
        max_tokens: Limite de tokens
    
    Returns:
        Contexte formaté
    """
    retriever = RAGRetriever()
    return retriever.get_context_for_library(
        library=library,
        query=query,
        top_k=top_k,
        max_tokens=max_tokens
    )

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='RAG Context Retriever')
    parser.add_argument('--library', type=str, help='Library name')
    parser.add_argument('--query', type=str, help='User query')
    parser.add_argument('--top-k', type=int, default=5, help='Number of chunks')
    parser.add_argument('--max-tokens', type=int, default=8000, help='Max tokens')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    
    args = parser.parse_args()
    
    if args.test or (not args.library and not args.query):
        # Test mode
        print(" Test du RAG Retriever", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        
        try:
            retriever = RAGRetriever()
            stats = retriever.get_stats()
            
            print(f"\n Statistiques:", file=sys.stderr)
            print(f"  • Total chunks: {stats['total_chunks']}", file=sys.stderr)
            print(f"  • Modèle: {stats['model']}", file=sys.stderr)
            print(f"  • Base ChromaDB: {stats['chroma_dir']}", file=sys.stderr)
            
            # Test de recherche
            print("\n Test de recherche:", file=sys.stderr)
            test_query = "How to plot a CMB map?"
            results = retriever.search(test_query, library="simonsobs-pixell", top_k=3)
            
            print(f"\n  Query: '{test_query}'", file=sys.stderr)
            print(f"  Résultats: {len(results)} chunks trouvés", file=sys.stderr)
            
            if results:
                print(f"\n  Premier résultat:", file=sys.stderr)
                print(f"  • Bibliothèque: {results[0]['metadata']['library']}", file=sys.stderr)
                print(f"  • Distance: {results[0]['distance']:.4f}", file=sys.stderr)
                print(f"  • Texte (100 premiers chars): {results[0]['text'][:100]}...", file=sys.stderr)
            
            print("\n Test réussi!", file=sys.stderr)
            
        except Exception as e:
            print(f"\n Erreur: {e}", file=sys.stderr)
            print("   Assurez-vous d'avoir d'abord exécuté prepare_rag.py", file=sys.stderr)
    else:
        # Production mode - return context to stdout
        try:
            context = retrieve_context(
                library=args.library,
                query=args.query,
                top_k=args.top_k,
                max_tokens=args.max_tokens
            )
            # Output ONLY the context to stdout
            print(context)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

