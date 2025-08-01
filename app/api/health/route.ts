import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Check if GCP credentials are available
    const hasGcpCredentials = !!process.env.GOOGLE_APPLICATION_CREDENTIALS;
    const hasGcpProject = !!process.env.GOOGLE_CLOUD_PROJECT;
    const hasGcpBucket = !!process.env.GOOGLE_CLOUD_BUCKET;
    
    // Check if context directories exist
    const fs = require('fs');
    const path = require('path');
    
    const contextDir = path.join(process.cwd(), 'app', 'context');
    const contextDirExists = fs.existsSync(contextDir);
    
    const publicContextDir = path.join(process.cwd(), 'public', 'context');
    const publicContextDirExists = fs.existsSync(publicContextDir);
    
    // Count contexts
    let contextCount = 0;
    if (contextDirExists) {
      const domains = fs.readdirSync(contextDir);
      for (const domain of domains) {
        const domainPath = path.join(contextDir, domain);
        if (fs.statSync(domainPath).isDirectory()) {
          const files = fs.readdirSync(domainPath);
          contextCount += files.filter((f: string) => f.endsWith('.txt')).length;
        }
      }
    }
    
    const healthStatus = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      environment: {
        node_env: process.env.NODE_ENV || 'development',
        gcp_configured: hasGcpCredentials && hasGcpProject && hasGcpBucket,
        gcp_project: process.env.GOOGLE_CLOUD_PROJECT || 'not_set',
        gcp_bucket: process.env.GOOGLE_CLOUD_BUCKET || 'not_set'
      },
      storage: {
        context_directory_exists: contextDirExists,
        public_context_directory_exists: publicContextDirExists,
        total_contexts: contextCount
      },
      version: process.env.npm_package_version || '1.0.0'
    };
    
    return NextResponse.json(healthStatus, { status: 200 });
    
  } catch (error) {
    console.error('Health check error:', error);
    
    return NextResponse.json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
} 