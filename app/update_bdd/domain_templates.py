#!/usr/bin/env python3
"""
Modèles de configuration pour les nouveaux domaines.
Facilite l'ajout de nouveaux domaines au système.
"""

# Modèles de configuration pour différents types de domaines
DOMAIN_TEMPLATES = {
    "web_development": {
        "use_ascl": False,
        "keywords": [
            "web", "django", "flask", "fastapi", "react", "vue", "angular",
            "express", "spring", "laravel", "rails", "aspnet", "jquery",
            "bootstrap", "tailwind", "webpack", "vite", "nextjs", "nuxtjs"
        ],
        "description": "Top web development frameworks and libraries for building modern web applications",
        "specific_libs": []
    },
    
    "mobile_development": {
        "use_ascl": False,
        "keywords": [
            "mobile", "ios", "android", "react-native", "flutter", "xamarin",
            "ionic", "cordova", "phonegap", "swift", "kotlin", "java",
            "objective-c", "xcode", "android-studio", "appium", "detox"
        ],
        "description": "Top mobile development frameworks and tools for iOS and Android applications",
        "specific_libs": []
    },
    
    "game_development": {
        "use_ascl": False,
        "keywords": [
            "game", "unity", "unreal", "godot", "pygame", "cocos2d",
            "phaser", "threejs", "babylon", "opengl", "vulkan", "directx",
            "opencv", "pillow", "pyglet", "arcade", "kivy", "ursina"
        ],
        "description": "Top game development engines and libraries for creating interactive games",
        "specific_libs": []
    },
    
    "cybersecurity": {
        "use_ascl": False,
        "keywords": [
            "security", "cyber", "crypto", "encryption", "penetration", "malware",
            "forensics", "network", "vulnerability", "exploit", "reverse",
            "nmap", "wireshark", "metasploit", "burp", "sqlmap", "hashcat"
        ],
        "description": "Top cybersecurity tools and libraries for security research and penetration testing",
        "specific_libs": []
    },
    
    "bioinformatics": {
        "use_ascl": False,
        "keywords": [
            "bio", "genomics", "proteomics", "biopython", "bioconductor", "plink",
            "samtools", "bwa", "bowtie", "gatk", "picard", "fastqc",
            "rna-seq", "dna", "protein", "sequence", "alignment", "phylogeny"
        ],
        "description": "Top bioinformatics tools and libraries for genomic and proteomic analysis",
        "specific_libs": []
    },
    
    "quantum_computing": {
        "use_ascl": False,
        "keywords": [
            "quantum", "qiskit", "cirq", "pennylane", "qutip", "projectq",
            "qsharp", "braket", "ionq", "rigetti", "dwave", "quantum-circuit"
        ],
        "description": "Top quantum computing frameworks and libraries for quantum algorithm development",
        "specific_libs": []
    },
    
    "blockchain": {
        "use_ascl": False,
        "keywords": [
            "blockchain", "ethereum", "bitcoin", "solidity", "web3", "truffle",
            "hardhat", "ganache", "metamask", "ipfs", "hyperledger", "consensys",
            "defi", "nft", "smart-contract", "cryptocurrency", "wallet"
        ],
        "description": "Top blockchain development tools and libraries for decentralized applications",
        "specific_libs": []
    },
    
    "devops": {
        "use_ascl": False,
        "keywords": [
            "devops", "docker", "kubernetes", "jenkins", "gitlab", "github-actions",
            "terraform", "ansible", "chef", "puppet", "prometheus", "grafana",
            "elk", "splunk", "nagios", "zabbix", "monitoring", "ci-cd"
        ],
        "description": "Top DevOps tools and platforms for automation and infrastructure management",
        "specific_libs": []
    },
    
    "cloud_computing": {
        "use_ascl": False,
        "keywords": [
            "cloud", "aws", "azure", "gcp", "kubernetes", "docker", "terraform",
            "serverless", "lambda", "functions", "containers", "microservices",
            "elastic", "scalable", "distributed", "orchestration", "deployment"
        ],
        "description": "Top cloud computing platforms and tools for scalable application deployment",
        "specific_libs": []
    },
    
    "iot": {
        "use_ascl": False,
        "keywords": [
            "iot", "internet-of-things", "arduino", "raspberry-pi", "esp32", "esp8266",
            "sensors", "actuators", "mqtt", "coap", "zigbee", "bluetooth",
            "wifi", "cellular", "edge-computing", "smart-home", "industrial-iot"
        ],
        "description": "Top IoT development platforms and libraries for connected device applications",
        "specific_libs": []
    }
}

def get_template(domain_name: str) -> dict:
    """Récupère un modèle de domaine par nom"""
    return DOMAIN_TEMPLATES.get(domain_name, {})

def list_available_templates() -> list:
    """Liste tous les modèles disponibles"""
    return list(DOMAIN_TEMPLATES.keys())

def create_custom_domain(
    name: str,
    keywords: list,
    description: str,
    specific_libs: list = None,
    use_ascl: bool = False
) -> dict:
    """Crée une configuration de domaine personnalisée"""
    return {
        "use_ascl": use_ascl,
        "keywords": keywords,
        "description": description,
        "specific_libs": specific_libs or []
    }

def validate_domain_config(config: dict) -> tuple[bool, list]:
    """Valide une configuration de domaine"""
    errors = []
    required_fields = ["use_ascl", "keywords", "description", "specific_libs"]
    
    # Vérifier les champs requis
    for field in required_fields:
        if field not in config:
            errors.append(f"Champ manquant: {field}")
    
    # Vérifier que keywords n'est pas vide
    if "keywords" in config and not config["keywords"]:
        errors.append("La liste des mots-clés ne peut pas être vide")
    
    # Vérifier que description n'est pas vide
    if "description" in config and not config["description"]:
        errors.append("La description ne peut pas être vide")
    
    # Vérifier le type des champs
    if "use_ascl" in config and not isinstance(config["use_ascl"], bool):
        errors.append("use_ascl doit être un booléen")
    
    if "keywords" in config and not isinstance(config["keywords"], list):
        errors.append("keywords doit être une liste")
    
    if "specific_libs" in config and not isinstance(config["specific_libs"], list):
        errors.append("specific_libs doit être une liste")
    
    return len(errors) == 0, errors

def print_template_info(template_name: str):
    """Affiche les informations d'un modèle"""
    if template_name not in DOMAIN_TEMPLATES:
        print(f"❌ Modèle '{template_name}' non trouvé")
        return
    
    template = DOMAIN_TEMPLATES[template_name]
    print(f"📋 Modèle: {template_name}")
    print(f"   - Utilise ASCL: {template['use_ascl']}")
    print(f"   - Mots-clés: {len(template['keywords'])}")
    print(f"   - Description: {template['description']}")
    print(f"   - Librairies spécifiques: {len(template['specific_libs'])}")
    
    print(f"\n🔑 Mots-clés:")
    for i, keyword in enumerate(template['keywords'], 1):
        print(f"   {i:2d}. {keyword}")

def main():
    """Fonction principale pour tester les modèles"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestion des modèles de domaines")
    parser.add_argument("--list", action="store_true", help="Lister tous les modèles disponibles")
    parser.add_argument("--template", help="Afficher les détails d'un modèle spécifique")
    parser.add_argument("--validate", help="Valider une configuration JSON")
    
    args = parser.parse_args()
    
    if args.list:
        print("📚 MODÈLES DE DOMAINES DISPONIBLES:")
        print("=" * 50)
        for template in list_available_templates():
            print(f"   - {template}")
        print(f"\nTotal: {len(DOMAIN_TEMPLATES)} modèles")
    
    elif args.template:
        print_template_info(args.template)
    
    elif args.validate:
        try:
            import json
            with open(args.validate, 'r') as f:
                config = json.load(f)
            
            is_valid, errors = validate_domain_config(config)
            if is_valid:
                print("✅ Configuration valide!")
            else:
                print("❌ Configuration invalide:")
                for error in errors:
                    print(f"   - {error}")
        except Exception as e:
            print(f"❌ Erreur lors de la validation: {e}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
