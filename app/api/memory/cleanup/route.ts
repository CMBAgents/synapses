import { NextRequest, NextResponse } from 'next/server';
import { clearAllCaches, getCacheInfo } from '@/app/utils/context';

export async function POST(request: NextRequest) {
  try {
    // Clear all caches to free memory
    clearAllCaches();
    
    // Force garbage collection if available
    if (global.gc) {
      global.gc();
    }
    
    return NextResponse.json({ 
      success: true, 
      message: 'Memory cleanup completed',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error during memory cleanup:', error);
    return NextResponse.json({ 
      error: 'Memory cleanup failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    // Return memory usage info
    const memUsage = process.memoryUsage();
    const cacheInfo = getCacheInfo();
    
    return NextResponse.json({
      memory: {
        rss: Math.round(memUsage.rss / 1024 / 1024), // MB
        heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024), // MB
        heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024), // MB
        external: Math.round(memUsage.external / 1024 / 1024), // MB
      },
      cache: {
        hasContext: cacheInfo.hasContext,
        currentProgram: cacheInfo.currentProgram,
        contextSizeMB: Math.round(cacheInfo.contextSize / 1024 / 1024 * 100) / 100,
        totalCacheSizeMB: Math.round(cacheInfo.totalCacheSize / 1024 / 1024 * 100) / 100,
        maxCacheSize: cacheInfo.maxCacheSize,
        maxEntries: cacheInfo.maxEntries,
        cacheUsagePercent: 'N/A (unlimited size)'
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error getting memory info:', error);
    return NextResponse.json({ 
      error: 'Failed to get memory info',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
