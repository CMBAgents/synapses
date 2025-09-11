# Adding New Domains

## Quick Start

Add a new domain automatically with one command:

```bash
python3 scripts/core/unified-domain-updater.py \
  --add-domain physics \
  --display-name "Physics & Quantum Computing" \
  --description "Top physics and quantum computing libraries" \
  --keywords "physics,quantum,quantum computing,quantum mechanics" \
  --specific-libs "qiskit/qiskit,rigetti/pyquil,quantumlib/Cirq,google/quantum"
```

## Parameters

- `--add-domain`: Domain identifier (lowercase, no spaces)
- `--display-name`: Human-readable name
- `--description`: Brief description of the domain
- `--keywords`: Comma-separated keywords for GitHub search
- `--specific-libs`: Comma-separated GitHub repos (owner/repo format)
- `--use-ascl`: Optional flag to use ASCL data (for astronomy domains)

## What Happens Automatically

1. ✅ Updates `config.json` with new domain
2. ✅ Updates `domains.ts` with mappings
3. ✅ Generates domain data via GitHub API
4. ✅ Creates Next.js routes
5. ✅ Generates context files

## Example Scripts

Run the example script for pre-configured domains:

```bash
python3 scripts/core/add-domain-example.py
```

## Manual Domain Updates

Update existing domains:

```bash
# Update specific domain
python3 scripts/core/unified-domain-updater.py --domain astronomy

# Update all domains
python3 scripts/core/unified-domain-updater.py --all
```
