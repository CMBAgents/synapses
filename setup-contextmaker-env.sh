#!/bin/bash
# Script pour configurer l'environnement contextmaker avec jupytext

# Ajouter jupytext au PATH
export PATH="/Library/Frameworks/Python.framework/Versions/3.12/bin:$PATH"

# Vérifier que jupytext est accessible
if command -v jupytext &> /dev/null; then
    echo "✅ jupytext est accessible: $(which jupytext)"
    echo "✅ Version: $(jupytext --version)"
else
    echo "❌ jupytext n'est pas accessible"
    exit 1
fi

echo "✅ Environnement contextmaker configuré avec succès"
