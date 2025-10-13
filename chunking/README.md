# 🧠 Dossier Chunking - RAG System

Ce dossier contient tous les scripts pour le système de **Chunking RAG** (Retrieval-Augmented Generation).

---

## 📁 Fichiers

| Fichier | Description | Usage |
|:---|:---|:---|
| **prepare_rag.py** | Indexation initiale complète | `python chunking/prepare_rag.py` |
| **rag_retriever.py** | Recherche sémantique de chunks | `python chunking/rag_retriever.py --test` |
| **update_chunk_status.py** | Met à jour les JSON avec statut | `python chunking/update_chunk_status.py` |
| **CHUNKING_EXPLAINED.md** | Documentation détaillée | Pour comprendre le système |

---

## 🚀 Quick Start

### **1. Installer les dépendances**
```bash
pip install -r requirements.txt
```

### **2. Première indexation (une seule fois, ~30 min)**
```bash
python chunking/prepare_rag.py
```

### **3. Tester la recherche**
```bash
python chunking/rag_retriever.py --test
```

### **4. Mettre à jour les JSON (optionnel)**
```bash
python chunking/update_chunk_status.py
```

---

## 🔄 Maintenance Automatique

Les chunks sont **automatiquement réindexés** lors de la maintenance quotidienne :

```bash
python maintenance/maintenance_modular.py --mode quick
```

→ Step7 détecte les fichiers modifiés (MD5) et ne re-chunke que ceux-là !

---

## 📊 Résultat

**Avant RAG :**
- Contexte: 3.6M tokens
- ❌ LLM refuse de répondre

**Après RAG :**
- Contexte: ~20k tokens (seulement les chunks pertinents)
- ✅ LLM répond correctement

---

## 📖 Plus d'infos

Consultez [CHUNKING_EXPLAINED.md](CHUNKING_EXPLAINED.md) pour la documentation complète.

