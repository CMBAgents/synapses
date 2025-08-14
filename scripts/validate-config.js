#!/usr/bin/env node
/**
 * Configuration validation script
 * Checks that all components are properly configured
 */

const fs = require('fs');
const path = require('path');

class ConfigValidator {
    constructor() {
        this.baseDir = process.cwd();
        this.errors = [];
        this.warnings = [];
        this.success = [];
    }

    log(message, type = 'info') {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
    }

    checkFileExists(filePath, description) {
        const fullPath = path.join(this.baseDir, filePath);
        if (fs.existsSync(fullPath)) {
            this.success.push(`${description} found: ${filePath}`);
            return true;
        } else {
            this.errors.push(`${description} missing: ${filePath}`);
            return false;
        }
    }

    checkDirectoryExists(dirPath, description) {
        const fullPath = path.join(this.baseDir, dirPath);
        if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
            this.success.push(`${description} found: ${dirPath}`);
            return true;
        } else {
            this.errors.push(`${description} missing: ${dirPath}`);
            return false;
        }
    }

    validateJsonFile(filePath, description) {
        if (!this.checkFileExists(filePath, description)) {
            return false;
        }

        try {
            const fullPath = path.join(this.baseDir, filePath);
            const content = fs.readFileSync(fullPath, 'utf8');
            JSON.parse(content);
            this.success.push(`${description} JSON valid: ${filePath}`);
        return true;
        } catch (error) {
            this.errors.push(`${description} JSON invalid: ${filePath} - ${error.message}`);
        return false;
      }
    }

    checkContextFiles() {
        const contextDir = path.join(this.baseDir, 'app', 'context');
        if (!fs.existsSync(contextDir)) {
            this.errors.push('Context directory missing: app/context');
            return;
        }

        let totalFiles = 0;
        let validFiles = 0;

        const domains = fs.readdirSync(contextDir).filter(item => {
            return fs.statSync(path.join(contextDir, item)).isDirectory();
        });

        for (const domain of domains) {
            const domainPath = path.join(contextDir, domain);
            const files = fs.readdirSync(domainPath).filter(file => file.endsWith('.txt'));

            totalFiles += files.length;
            for (const file of files) {
                const filePath = path.join(domainPath, file);
                const stats = fs.statSync(filePath);
                
                if (stats.size > 1000) {
                    validFiles++;
                    this.success.push(`Valid context: ${domain}/${file} (${stats.size} bytes)`);
                } else {
                    this.warnings.push(`Context too small: ${domain}/${file} (${stats.size} bytes)`);
                }
            }
        }

        this.success.push(`Contexts found: ${validFiles}/${totalFiles} valid`);
    }

    checkDataFiles() {
        const dataDir = path.join(this.baseDir, 'app', 'data');
        if (!fs.existsSync(dataDir)) {
            this.errors.push('Data directory missing: app/data');
            return;
        }

        const requiredFiles = [
            'astronomy-libraries.json',
            'finance-libraries.json',
            'libraries.json'
        ];

        for (const file of requiredFiles) {
            this.validateJsonFile(`app/data/${file}`, `Data file ${file}`);
        }
    }

    checkScripts() {
        const scriptsDir = path.join(this.baseDir, 'scripts');
        if (!fs.existsSync(scriptsDir)) {
            this.errors.push('Scripts directory missing: scripts');
            return;
        }

        const requiredScripts = [
            'generate-missing-contexts.py',
            'cloud-sync-contexts.py',
            'generate-and-sync-all.py',
            'install-dependencies.py',
            'build-context.js'
        ];

        for (const script of requiredScripts) {
            this.checkFileExists(`scripts/${script}`, `Script ${script}`);
        }
    }

    checkConfiguration() {
        // Check main config.json
        this.validateJsonFile('config.json', 'Main configuration');

        // Check cloud-config.json
        this.validateJsonFile('gestion/config/cloud-config.json', 'Cloud configuration');

        // Check package.json
        this.validateJsonFile('package.json', 'Node.js configuration');
    }

    checkEnvironment() {
        // Check .env
        const envPath = path.join(this.baseDir, '.env');
        if (fs.existsSync(envPath)) {
            this.success.push('.env file found');
        } else {
            this.warnings.push('.env file missing (optional)');
        }

        // Check node_modules
        const nodeModulesPath = path.join(this.baseDir, 'node_modules');
        if (fs.existsSync(nodeModulesPath)) {
            this.success.push('Node.js dependencies installed');
        } else {
            this.warnings.push('Node.js dependencies not installed (npm install)');
        }
    }

    checkPublicContext() {
        const publicContextDir = path.join(this.baseDir, 'public', 'context');
        if (fs.existsSync(publicContextDir)) {
            const files = fs.readdirSync(publicContextDir).filter(file => file.endsWith('.txt'));
            this.success.push(`Public contexts: ${files.length} files`);
        } else {
            this.warnings.push('public/context directory missing');
        }
    }

    validateCloudConfig() {
        try {
            const cloudConfigPath = path.join(this.baseDir, 'gestion', 'config', 'cloud-config.json');
            if (!fs.existsSync(cloudConfigPath)) {
                this.errors.push('Cloud configuration missing');
                return;
            }

            const config = JSON.parse(fs.readFileSync(cloudConfigPath, 'utf8'));
            
            // Check required fields
            const requiredFields = ['provider', 'sync_enabled'];
            for (const field of requiredFields) {
                if (!(field in config)) {
                    this.errors.push(`Required field missing in cloud-config.json: ${field}`);
                }
            }

            // Check provider
            const validProviders = ['local', 's3', 'gcs', 'http'];
            if (config.provider && !validProviders.includes(config.provider)) {
                this.errors.push(`Invalid provider: ${config.provider}. Valid: ${validProviders.join(', ')}`);
            }

            // Check configuration based on provider
            if (config.provider === 's3') {
                if (!config.bucket_name) {
                    this.errors.push('bucket_name required for S3 provider');
                }
                if (!config.region) {
                    this.errors.push('region required for S3 provider');
                }
            }

            if (config.provider === 'gcs') {
                if (!config.bucket_name) {
                    this.errors.push('bucket_name required for GCS provider');
                }
            }

            if (config.provider === 'http') {
                if (!config.upload_url) {
                    this.errors.push('upload_url required for HTTP provider');
                }
            }

            this.success.push('Cloud configuration validated');
        } catch (error) {
            this.errors.push(`Error validating cloud configuration: ${error.message}`);
        }
    }

    runAllChecks() {
        this.log('Starting configuration validation...', 'info');
        console.log('='.repeat(60));

        // Basic checks
        this.checkConfiguration();
        this.checkScripts();
        this.checkDataFiles();
        this.checkContextFiles();
        this.checkPublicContext();
        this.checkEnvironment();
        this.validateCloudConfig();

        // Display results
        console.log('\n' + '='.repeat(60));
        this.log('Validation results:', 'info');

        if (this.success.length > 0) {
            console.log('\n✅ SUCCESS:');
            this.success.forEach(msg => console.log(`  ✓ ${msg}`));
        }

        if (this.warnings.length > 0) {
            console.log('\n⚠️  WARNINGS:');
            this.warnings.forEach(msg => console.log(`  ⚠ ${msg}`));
        }

        if (this.errors.length > 0) {
            console.log('\n❌ ERRORS:');
            this.errors.forEach(msg => console.log(`  ✗ ${msg}`));
        }

        console.log('\n' + '='.repeat(60));
        
        const summary = {
            total: this.success.length + this.warnings.length + this.errors.length,
            success: this.success.length,
            warnings: this.warnings.length,
            errors: this.errors.length
        };

        this.log(`Validation complete: ${summary.success} successes, ${summary.warnings} warnings, ${summary.errors} errors`, 'info');

        if (summary.errors > 0) {
            this.log('❌ Configuration has errors that must be fixed', 'error');
    process.exit(1);
        } else if (summary.warnings > 0) {
            this.log('⚠️  Configuration has warnings but can function', 'warn');
        } else {
            this.log('✅ Configuration is valid and ready to use', 'info');
        }

        return summary;
    }
}

// Execute if called directly
if (require.main === module) {
    const validator = new ConfigValidator();
    validator.runAllChecks();
}

module.exports = ConfigValidator;
