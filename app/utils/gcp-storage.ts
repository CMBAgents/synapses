import { Storage } from '@google-cloud/storage';

// Initialize Google Cloud Storage
const storage = new Storage({
  projectId: process.env.GOOGLE_CLOUD_PROJECT,
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS
});

// Bucket instances
export const contextsBucket = storage.bucket(process.env.GOOGLE_CLOUD_BUCKET!);
export const staticBucket = storage.bucket(process.env.GOOGLE_CLOUD_STATIC_BUCKET!);

/**
 * Upload a context file to GCP Cloud Storage
 */
export async function uploadContext(domain: string, filename: string, content: string): Promise<void> {
  try {
    const file = contextsBucket.file(`${domain}/${filename}`);
    await file.save(content, {
      metadata: {
        contentType: 'text/plain',
        cacheControl: 'public, max-age=3600'
      }
    });
    console.log(`✅ Context uploaded: ${domain}/${filename}`);
  } catch (error) {
    console.error(`❌ Error uploading context ${domain}/${filename}:`, error);
    throw error;
  }
}

/**
 * Get a signed URL for reading a context file
 */
export async function getContextUrl(domain: string, filename: string): Promise<string> {
  try {
    const file = contextsBucket.file(`${domain}/${filename}`);
    const [url] = await file.getSignedUrl({
      action: 'read',
      expires: Date.now() + 24 * 60 * 60 * 1000 // 24 hours
    });
    return url;
  } catch (error) {
    console.error(`❌ Error getting signed URL for ${domain}/${filename}:`, error);
    throw error;
  }
}

/**
 * List all context files in a domain
 */
export async function listContexts(domain: string): Promise<string[]> {
  try {
    const [files] = await contextsBucket.getFiles({ prefix: `${domain}/` });
    return files.map(file => file.name.replace(`${domain}/`, ''));
  } catch (error) {
    console.error(`❌ Error listing contexts for domain ${domain}:`, error);
    throw error;
  }
}

/**
 * Check if a context file exists
 */
export async function contextExists(domain: string, filename: string): Promise<boolean> {
  try {
    const file = contextsBucket.file(`${domain}/${filename}`);
    const [exists] = await file.exists();
    return exists;
  } catch (error) {
    console.error(`❌ Error checking if context exists ${domain}/${filename}:`, error);
    return false;
  }
}

/**
 * Delete a context file
 */
export async function deleteContext(domain: string, filename: string): Promise<void> {
  try {
    const file = contextsBucket.file(`${domain}/${filename}`);
    await file.delete();
    console.log(`✅ Context deleted: ${domain}/${filename}`);
  } catch (error) {
    console.error(`❌ Error deleting context ${domain}/${filename}:`, error);
    throw error;
  }
}

/**
 * Get context file metadata
 */
export async function getContextMetadata(domain: string, filename: string) {
  try {
    const file = contextsBucket.file(`${domain}/${filename}`);
    const [metadata] = await file.getMetadata();
    return metadata;
  } catch (error) {
    console.error(`❌ Error getting metadata for ${domain}/${filename}:`, error);
    throw error;
  }
}

/**
 * Upload static assets to the static bucket
 */
export async function uploadStaticAsset(path: string, content: string, contentType: string = 'text/plain'): Promise<void> {
  try {
    const file = staticBucket.file(path);
    await file.save(content, {
      metadata: {
        contentType,
        cacheControl: 'public, max-age=86400' // 24 hours
      }
    });
    console.log(`✅ Static asset uploaded: ${path}`);
  } catch (error) {
    console.error(`❌ Error uploading static asset ${path}:`, error);
    throw error;
  }
}

/**
 * Sync local context directory to GCP
 */
export async function syncContextsToGCP(): Promise<void> {
  try {
    const fs = require('fs');
    const path = require('path');
    
    const contextDir = path.join(process.cwd(), 'app', 'context');
    
    if (!fs.existsSync(contextDir)) {
      console.log('No local context directory found');
      return;
    }
    
    const domains = fs.readdirSync(contextDir);
    
    for (const domain of domains) {
      const domainPath = path.join(contextDir, domain);
      if (fs.statSync(domainPath).isDirectory()) {
        const files = fs.readdirSync(domainPath);
        
        for (const file of files) {
          if (file.endsWith('.txt')) {
            const filePath = path.join(domainPath, file);
            const content = fs.readFileSync(filePath, 'utf8');
            
            await uploadContext(domain, file, content);
          }
        }
      }
    }
    
    console.log('✅ All contexts synced to GCP');
  } catch (error) {
    console.error('❌ Error syncing contexts to GCP:', error);
    throw error;
  }
} 