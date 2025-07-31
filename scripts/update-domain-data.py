#!/usr/bin/env python3
"""
Script to update domain-specific JSON files using the get100 algorithm.
This script separates astronomy/cosmology and finance libraries into separate files.
"""

import json
import csv
import os
from pathlib import Path

def load_csv_data(csv_path):
    """Load data from CSV file."""
    data = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def filter_astronomy_libraries(data):
    """Filter astronomy and cosmology libraries."""
    astronomy_keywords = [
        "astro", "astropy", "healpy", "photutils", "sky", "gal", "cosmo", "cmb",
        "planck", "tardis", "lightkurve", "astroquery", "pypeit", "poppy", "stellar",
        "galsim", "ultranest", "pymultinest", "zeus", "radis", "astronn", "presto", 
        "astroplan", "sep", "specutils", "s2fft", "stingray",
        "spacepy", "pycbc", "gwpy", "einsteinpy", "simonsobs", "cmbant", "lesgourg/class_public",
    ]
    
    filtered = []
    for item in data:
        url = item.get("github_url", "").lower()
        if any(keyword in url for keyword in astronomy_keywords):
            filtered.append(item)
    
    return filtered

def filter_finance_libraries(data):
    """Filter finance and trading libraries."""
    finance_keywords = [
        "finance", "trading", "portfolio", "quant", "zipline", "yfinance", "pyfolio",
        "empyrical", "alphalens", "mlfinlab", "ffn", "finquant", "backtrader",
        "vnpy", "tushare", "akshare", "ccxt", "pandas-ta", "ta-lib", "finrl",
        "qlib", "finrl", "gplearn", "pykalman", "arch", "statsmodels"
    ]
    
    filtered = []
    for item in data:
        url = item.get("github_url", "").lower()
        if any(keyword in url for keyword in finance_keywords):
            filtered.append(item)
    
    return filtered

def create_domain_json(libraries, domain, output_path):
    """Create domain-specific JSON file."""
    domain_data = {
        "libraries": [],
        "domain": domain,
        "description": "",
        "keywords": []
    }
    
    # Set domain-specific metadata
    if domain == "astronomy":
        domain_data["description"] = "Top astronomy and cosmology libraries for celestial observations, gravitational waves, and cosmic microwave background analysis"
        domain_data["keywords"] = ["astronomy", "cosmology", "astrophysics", "gravitational waves", "CMB", "healpy", "astropy"]
    elif domain == "finance":
        domain_data["description"] = "Top finance and trading libraries for portfolio optimization, algorithmic trading, and financial analysis"
        domain_data["keywords"] = ["finance", "trading", "portfolio", "quantitative", "zipline", "yfinance", "pyfolio"]
    
    # Convert libraries to the required format
    for i, lib in enumerate(libraries[:100], 1):  # Top 100
        try:
            stars = int(lib.get("stars", 0))
            domain_data["libraries"].append({
                "name": lib.get("name", ""),
                "github_url": lib.get("github_url", ""),
                "stars": stars,
                "rank": i
            })
        except (ValueError, KeyError):
            continue
    
    # Sort by stars (descending)
    domain_data["libraries"].sort(key=lambda x: x["stars"], reverse=True)
    
    # Update ranks
    for i, lib in enumerate(domain_data["libraries"], 1):
        lib["rank"] = i
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(domain_data, f, indent=2, ensure_ascii=False)
    
    print(f"Created {output_path} with {len(domain_data['libraries'])} libraries")

def main():
    """Main function to update domain data."""
    # Paths
    base_dir = Path("app/data")
    csv_path = Path("app/update_bdd/last.csv")
    
    # Ensure directories exist
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if CSV exists
    if not csv_path.exists():
        print(f"Error: {csv_path} not found. Please run get100.py first.")
        return
    
    # Load data
    print("Loading data from CSV...")
    data = load_csv_data(csv_path)
    print(f"Loaded {len(data)} libraries from CSV")
    
    # Filter by domain
    print("Filtering astronomy libraries...")
    astronomy_libs = filter_astronomy_libraries(data)
    print(f"Found {len(astronomy_libs)} astronomy libraries")
    
    print("Filtering finance libraries...")
    finance_libs = filter_finance_libraries(data)
    print(f"Found {len(finance_libs)} finance libraries")
    
    # Create JSON files
    print("Creating JSON files...")
    create_domain_json(astronomy_libs, "astronomy", base_dir / "astronomy-libraries.json")
    create_domain_json(finance_libs, "finance", base_dir / "finance-libraries.json")
    
    print("Domain data update completed!")

if __name__ == "__main__":
    main() 