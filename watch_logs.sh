#!/bin/bash

echo "🔍 Surveillance des logs en temps réel pour cmbagent-info..."
echo "Appuyez sur Ctrl+C pour arrêter"
echo "=========================================="

# Fonction pour afficher les logs avec un timestamp
show_logs() {
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=cmbagent-info" \
        --limit=10 \
        --format="table(timestamp,severity,textPayload)" \
        --freshness=1m
}

# Boucle infinie pour surveiller les logs
while true; do
    echo "📅 $(date '+%Y-%m-%d %H:%M:%S') - Vérification des nouveaux logs..."
    
    # Afficher les logs récents
    logs=$(show_logs)
    
    if [ -n "$logs" ]; then
        echo "$logs"
        echo "------------------------------------------"
    else
        echo "Aucun nouveau log trouvé"
    fi
    
    # Attendre 10 secondes avant la prochaine vérification
    sleep 10
done
