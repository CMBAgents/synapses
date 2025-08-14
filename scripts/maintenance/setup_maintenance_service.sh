#!/bin/bash
"""
Script d'installation du service de maintenance quotidienne

Ce script configure un service systemd pour exécuter automatiquement
la maintenance quotidienne du site.

Utilisation (en tant que root) :
    sudo bash scripts/setup_maintenance_service.sh

Le service sera configuré pour :
    - Démarrer automatiquement au boot
    - Redémarrer en cas d'erreur
    - Logger dans les journaux système
"""

set -e

# Configuration
SERVICE_NAME="cmbagent-maintenance"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PROJECT_DIR="$(pwd)"
PYTHON_PATH="$(which python3)"

echo "🔧 Configuration du service de maintenance quotidienne..."

# Vérifier qu'on est root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté en tant que root (utilisez sudo)"
    exit 1
fi

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "package.json" ]; then
    echo "❌ Veuillez exécuter ce script depuis la racine du projet"
    exit 1
fi

# Créer le fichier de service systemd
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=CMB Agent Info - Daily Maintenance Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=${PYTHON_PATH} ${PROJECT_DIR}/scripts/schedule_daily_maintenance.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

[Install]
WantedBy=multi-user.target
EOF

echo "📝 Fichier de service créé: $SERVICE_FILE"

# Recharger systemd
systemctl daemon-reload
echo "🔄 Configuration systemd rechargée"

# Activer le service
systemctl enable "$SERVICE_NAME"
echo "✅ Service activé pour démarrage automatique"

# Démarrer le service
systemctl start "$SERVICE_NAME"
echo "🚀 Service démarré"

# Afficher le statut
echo ""
echo "📊 Statut du service:"
systemctl status "$SERVICE_NAME" --no-pager

echo ""
echo "✅ Service de maintenance configuré avec succès !"
echo ""
echo "Commandes utiles :"
echo "  - Voir le statut:    sudo systemctl status $SERVICE_NAME"
echo "  - Voir les logs:     sudo journalctl -u $SERVICE_NAME -f"
echo "  - Arrêter:          sudo systemctl stop $SERVICE_NAME"  
echo "  - Redémarrer:       sudo systemctl restart $SERVICE_NAME"
echo "  - Désactiver:       sudo systemctl disable $SERVICE_NAME"
echo ""
