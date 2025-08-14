# Synapses

A modern platform to explore and rank the top 100 open source libraries by expertise domain.

[![GitHub stars](https://img.shields.io/github/stars/CMBAgents/cmbagent-info?style=social)](https://github.com/CMBAgents/cmbagent-info)
[![GitHub forks](https://img.shields.io/github/forks/CMBAgents/cmbagent-info?style=social)](https://github.com/CMBAgents/cmbagent-info)
[![GitHub issues](https://img.shields.io/github/issues/CMBAgents/cmbagent-info)](https://github.com/CMBAgents/cmbagent-info/issues)
[![GitHub license](https://img.shields.io/github/license/CMBAgents/cmbagent-info)](https://github.com/CMBAgents/cmbagent-info/blob/main/LICENSE)

## Overview

Synapses allows you to discover, compare, and interact with the most popular libraries across different domains. Each library is ranked according to its GitHub popularity and comes with detailed contexts automatically generated from existing documentation, docstrings, notebooks, and even code.

## Screenshots

### Main Interface
![Synapses Main Interface](/github1.png)

### Library Rankings
![Library Rankings](/github2.png)

## Features

**Smart Rankings** : Ranking system based on GitHub stars with tie-breaking management

**Automatic Contexts** : Automatic generation of contextual documentation for each library taking into account existing documentation, docstrings, notebooks, and even code

**Modern Interface** : Responsive design with smooth animations and intuitive navigation

**Specialized Domains** : Focus on machine learning, astrophysics/cosmology, and finance/trading

## Technologies

- **Frontend** : Next.js 15, React 19, TypeScript
- **Styling** : Tailwind CSS with custom components
- **Backend** : Next.js API routes with Google Cloud integration
- **Documentation** : Automatic generation with contextmaker
- **Deployment** : Docker and Google Cloud Platform

## Quick Start

```bash
# Install dependencies
npm install

# Start development mode
npm run dev

# Build for production
npm run build
```

## Project Structure

```
app/
├── api/           # API routes
├── chat/          # Domain-specific chat interface
├── leaderboard/   # Library rankings
├── ui/            # Reusable components
└── utils/         # Utilities and helpers

scripts/           # Python scripts for maintenance
├── maintenance/   # Automated maintenance scripts
└── core/          # Context and data management
```

## Data Maintenance

The project includes automated scripts for:

- Updating rankings from GitHub
- Generating missing contexts
- Cloud synchronization
- Cost and performance monitoring

## Contributing

Contributions are welcome! Check open issues or propose new features.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

