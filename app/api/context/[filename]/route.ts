import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { isDomainSupported } from '@/app/config/domains';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const { filename } = await params;
    const { searchParams } = new URL(request.url);
    const domain = searchParams.get('domain');

    if (!domain || !isDomainSupported(domain)) {
      return NextResponse.json({ error: 'Invalid domain' }, { status: 400 });
    }

    if (!filename) {
      return NextResponse.json({ error: 'Filename is required' }, { status: 400 });
    }

    // Construct the file path
    const contextDir = path.join(process.cwd(), 'public', 'context', domain);
    const contextFilePath = path.join(contextDir, filename);

    // Check if file exists
    if (!fs.existsSync(contextFilePath)) {
      return NextResponse.json({ 
        error: 'Context file not found',
        filename,
        domain 
      }, { status: 404 });
    }

    // Read the file
    const contextContent = fs.readFileSync(contextFilePath, 'utf-8');
    
    // Get file stats for cache headers
    const stats = fs.statSync(contextFilePath);
    const lastModified = stats.mtime.toUTCString();
    const etag = `"${stats.mtime.getTime()}-${stats.size}"`;

    // Return the context content with optimized headers
    return new NextResponse(contextContent, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'public, max-age=3600, stale-while-revalidate=86400', // 1 hour cache, 24h stale
        'Last-Modified': lastModified,
        'ETag': etag,
        'Content-Length': contextContent.length.toString(),
        'X-Context-Filename': filename,
        'X-Context-Domain': domain,
        'X-Context-Size': contextContent.length.toString()
      }
    });

  } catch (error) {
    console.error(`Error loading context file:`, error);
    return NextResponse.json({ 
      error: 'Internal server error'
    }, { status: 500 });
  }
}

// Handle HEAD requests for checking file existence
export async function HEAD(
  request: NextRequest,
  { params }: { params: Promise<{ filename: string }> }
) {
  try {
    const { filename } = await params;
    const { searchParams } = new URL(request.url);
    const domain = searchParams.get('domain');

    if (!domain || !isDomainSupported(domain)) {
      return new NextResponse(null, { status: 400 });
    }

    if (!filename) {
      return new NextResponse(null, { status: 400 });
    }

    // Construct the file path
    const contextDir = path.join(process.cwd(), 'public', 'context', domain);
    const contextFilePath = path.join(contextDir, filename);

    // Check if file exists
    if (!fs.existsSync(contextFilePath)) {
      return new NextResponse(null, { status: 404 });
    }

    // Get file stats
    const stats = fs.statSync(contextFilePath);
    const lastModified = stats.mtime.toUTCString();
    const etag = `"${stats.mtime.getTime()}-${stats.size}"`;

    return new NextResponse(null, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'public, max-age=3600, stale-while-revalidate=86400',
        'Last-Modified': lastModified,
        'ETag': etag,
        'Content-Length': stats.size.toString(),
        'X-Context-Filename': filename,
        'X-Context-Domain': domain,
        'X-Context-Size': stats.size.toString()
      }
    });

  } catch (error) {
    console.error(`Error checking context file:`, error);
    return new NextResponse(null, { status: 500 });
  }
}