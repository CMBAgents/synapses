# Adding New Domains

## Quick Start

Add a new domain automatically with one command:

```bash
python3 maintenance/unified-domain-updater.py \
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
6. ✅ **NEW**: Automatically works with embedded context system

## Example Scripts

Run the example script for pre-configured domains:

```bash
# Le fichier add-domain-example.py a été supprimé car non utilisé
```

## Manual Domain Updates

Update existing domains:

```bash
# Update specific domain
python3 maintenance/unified-domain-updater.py --domain astronomy

# Update all domains
python3 maintenance/unified-domain-updater.py --all
```

## Embedded Context System

The system now includes a **dynamic embedded context system** that automatically works with new domains:

### How It Works

1. **Automatic Loading**: When a domain is added, the system automatically looks for `embedded-context-{domain}.ts` files
2. **Lazy Loading**: Contexts are only loaded when needed, improving performance
3. **Smart Caching**: Loaded contexts are cached to avoid repeated loading
4. **Pattern Recognition**: Programs are automatically associated with the correct domain

### Creating Embedded Context Files

For each domain, create a file `app/utils/embedded-context-{domain}.ts`:

```typescript
// Generated embedded context module for {Domain}
export const embeddedContexts = {
  '{domain}': {
    'program-1': `# Documentation for program 1
Content here...
`,
    'program-2': `# Documentation for program 2
Content here...
`,
    // ... more programs
  }
};
```

### Available Functions

- `loadEmbeddedContext(domain)` - Load context for a domain
- `getEmbeddedContext(domain, programId)` - Get specific program context
- `getAvailablePrograms(domain)` - List all programs in a domain
- `preloadAllContexts()` - Preload all contexts
- `getLoadedDomains()` - List loaded domains
- `isDomainLoaded(domain)` - Check if domain is loaded

### Benefits

✅ **No Code Changes Required** - New domains work automatically
✅ **Performance Optimized** - Lazy loading and caching
✅ **Error Resilient** - Graceful handling of missing domains
✅ **Extensible** - Easy to add new domains without touching existing code
