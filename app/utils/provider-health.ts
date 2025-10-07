/**
 * Provider Health Monitoring System
 * Tracks provider performance and availability for adaptive routing
 */

interface ProviderHealth {
  isAvailable: boolean;
  averageResponseTime: number;
  successRate: number;
  lastChecked: number;
  consecutiveFailures: number;
  lastError?: string;
}

interface ProviderMetrics {
  totalRequests: number;
  successfulRequests: number;
  totalResponseTime: number;
  errors: string[];
}

// Health status for each provider
const providerHealth: Record<string, ProviderHealth> = {};

// Performance metrics for each provider
const providerMetrics: Record<string, ProviderMetrics> = {};

// Initialize default metrics for all providers
const initializeProviderMetrics = (provider: string) => {
  if (!providerMetrics[provider]) {
    providerMetrics[provider] = {
      totalRequests: 0,
      successfulRequests: 0,
      totalResponseTime: 0,
      errors: []
    };
  }
  if (!providerHealth[provider]) {
    providerHealth[provider] = {
      isAvailable: true,
      averageResponseTime: 0,
      successRate: 1.0,
      lastChecked: 0,
      consecutiveFailures: 0
    };
  }
};

// Health check configuration
const HEALTH_CHECK_INTERVAL = 5 * 60 * 1000; // 5 minutes
const MAX_CONSECUTIVE_FAILURES = 3;
const HEALTH_CHECK_TIMEOUT = 10000; // 10 seconds

/**
 * Initialize provider health monitoring
 */
export function initializeProviderHealth() {
  // Initialize health status for all providers
  const providers = ['openai', 'gemini', 'openrouter', 'vertexai', 'sambanova', 'deepseek'];
  
  providers.forEach(provider => {
    providerHealth[provider] = {
      isAvailable: true,
      averageResponseTime: 0,
      successRate: 1.0,
      lastChecked: 0,
      consecutiveFailures: 0
    };
    
    providerMetrics[provider] = {
      totalRequests: 0,
      successfulRequests: 0,
      totalResponseTime: 0,
      errors: []
    };
  });
  
  // Start periodic health checks
  setInterval(performHealthChecks, HEALTH_CHECK_INTERVAL);
  
  console.log('Provider health monitoring initialized');
}

/**
 * Perform health checks on all providers
 */
async function performHealthChecks() {
  console.log('Performing provider health checks...');
  
  const healthCheckPromises = Object.keys(providerHealth).map(async (provider) => {
    try {
      await checkProviderHealth(provider);
    } catch (error) {
      console.error(`Health check failed for ${provider}:`, error);
    }
  });
  
  await Promise.allSettled(healthCheckPromises);
  
  // Log health status
  logProviderHealth();
}

/**
 * Check health of a specific provider
 */
async function checkProviderHealth(provider: string): Promise<void> {
  const startTime = Date.now();
  
  try {
    // Simple health check based on provider type
    let healthCheckPromise: Promise<any>;
    
    switch (provider) {
      case 'openai':
        healthCheckPromise = checkOpenAIHealth();
        break;
      case 'gemini':
        healthCheckPromise = checkGeminiHealth();
        break;
      case 'openrouter':
        healthCheckPromise = checkOpenRouterHealth();
        break;
      case 'vertexai':
        healthCheckPromise = checkVertexAIHealth();
        break;
      case 'sambanova':
        healthCheckPromise = checkSambaNovaHealth();
        break;
      case 'deepseek':
        healthCheckPromise = checkDeepSeekHealth();
        break;
      default:
        throw new Error(`Unknown provider: ${provider}`);
    }
    
    // Wait for health check with timeout
    await Promise.race([
      healthCheckPromise,
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Health check timeout')), HEALTH_CHECK_TIMEOUT)
      )
    ]);
    
    const responseTime = Date.now() - startTime;
    updateProviderHealth(provider, true, responseTime);
    
  } catch (error) {
    const responseTime = Date.now() - startTime;
    updateProviderHealth(provider, false, responseTime, error instanceof Error ? error.message : 'Unknown error');
  }
}

/**
 * Provider-specific health checks
 */
async function checkOpenAIHealth(): Promise<void> {
  // Check if OpenAI API key is available
  if (!process.env.OPENAI_API_KEY) {
    throw new Error('OpenAI API key not configured');
  }
  // Could add a simple API call here if needed
}

async function checkGeminiHealth(): Promise<void> {
  // Check if Gemini API key is available
  if (!process.env.GEMINI_API_KEY) {
    throw new Error('Gemini API key not configured');
  }
}

async function checkOpenRouterHealth(): Promise<void> {
  // Check if OpenRouter API key is available
  if (!process.env.OPEN_ROUTER_KEY) {
    throw new Error('OpenRouter API key not configured');
  }
}

async function checkVertexAIHealth(): Promise<void> {
  // Check if Google Cloud credentials are available
  if (!process.env.GOOGLE_APPLICATION_CREDENTIALS && 
      !process.env.GOOGLE_CLOUD_PROJECT) {
    throw new Error('Google Cloud credentials not configured');
  }
}

async function checkSambaNovaHealth(): Promise<void> {
  // Check if SambaNova API key is available
  if (!process.env.SAMBA_NOVA_API_KEY) {
    throw new Error('SambaNova API key not configured');
  }
}

async function checkDeepSeekHealth(): Promise<void> {
  // Check if DeepSeek API key is available
  if (!process.env.DEEPSEEK_API_KEY) {
    throw new Error('DeepSeek API key not configured');
  }
}

/**
 * Update provider health status
 */
function updateProviderHealth(
  provider: string, 
  isHealthy: boolean, 
  responseTime: number, 
  error?: string
) {
  // Ensure provider metrics are initialized
  initializeProviderMetrics(provider);
  
  const health = providerHealth[provider];
  const metrics = providerMetrics[provider];
  
  // Update metrics (with safety checks)
  if (metrics && health) {
    metrics.totalRequests++;
    if (isHealthy) {
      metrics.successfulRequests++;
      metrics.totalResponseTime += responseTime;
      health.consecutiveFailures = 0;
    } else {
      health.consecutiveFailures++;
      if (error) {
        metrics.errors.push(error);
        health.lastError = error;
      }
    }
  }
  
  // Update health status (with safety checks)
  if (health && metrics) {
    health.isAvailable = health.consecutiveFailures < MAX_CONSECUTIVE_FAILURES;
    health.averageResponseTime = metrics.successfulRequests > 0 ? metrics.totalResponseTime / metrics.successfulRequests : 0;
    health.successRate = metrics.totalRequests > 0 ? metrics.successfulRequests / metrics.totalRequests : 0;
    health.lastChecked = Date.now();
  }
  
  console.log(`Provider ${provider} health updated:`, {
    available: health.isAvailable,
    responseTime: `${responseTime}ms`,
    successRate: `${(health.successRate * 100).toFixed(1)}%`,
    consecutiveFailures: health.consecutiveFailures
  });
}

/**
 * Record a request result for a provider
 */
export function recordProviderResult(
  provider: string, 
  success: boolean, 
  responseTime: number, 
  error?: string
) {
  updateProviderHealth(provider, success, responseTime, error);
}

/**
 * Get the best available provider based on performance
 */
export function getBestProvider(requestedProvider?: string): string {
  // If a specific provider is requested and it's healthy, use it
  if (requestedProvider && providerHealth[requestedProvider]?.isAvailable) {
    return requestedProvider;
  }
  
  // Find the best available provider based on performance
  const availableProviders = Object.entries(providerHealth)
    .filter(([_, health]) => health.isAvailable)
    .sort(([_, a], [__, b]) => {
      // Sort by success rate first, then by response time
      if (a.successRate !== b.successRate) {
        return b.successRate - a.successRate;
      }
      return a.averageResponseTime - b.averageResponseTime;
    });
  
  if (availableProviders.length === 0) {
    console.warn('No healthy providers available, falling back to openrouter');
    return 'openrouter';
  }
  
  const [bestProvider] = availableProviders[0];
  console.log(`Selected best provider: ${bestProvider}`, {
    successRate: `${(providerHealth[bestProvider].successRate * 100).toFixed(1)}%`,
    avgResponseTime: `${providerHealth[bestProvider].averageResponseTime.toFixed(0)}ms`
  });
  
  return bestProvider;
}

/**
 * Get provider health status
 */
export function getProviderHealth(): Record<string, ProviderHealth> {
  return { ...providerHealth };
}

/**
 * Get provider metrics
 */
export function getProviderMetrics(): Record<string, ProviderMetrics> {
  return { ...providerMetrics };
}

/**
 * Log current provider health status
 */
function logProviderHealth() {
  console.log('📊 Provider Health Status:');
  Object.entries(providerHealth).forEach(([provider, health]) => {
    console.log(`  ${provider}:`, {
      available: health.isAvailable ? '✅' : '❌',
      successRate: `${(health.successRate * 100).toFixed(1)}%`,
      avgResponseTime: `${health.averageResponseTime.toFixed(0)}ms`,
      consecutiveFailures: health.consecutiveFailures,
      lastError: health.lastError || 'None'
    });
  });
}

/**
 * Reset provider health (for testing)
 */
export function resetProviderHealth() {
  Object.keys(providerHealth).forEach(provider => {
    providerHealth[provider] = {
      isAvailable: true,
      averageResponseTime: 0,
      successRate: 1.0,
      lastChecked: 0,
      consecutiveFailures: 0
    };
    
    providerMetrics[provider] = {
      totalRequests: 0,
      successfulRequests: 0,
      totalResponseTime: 0,
      errors: []
    };
  });
  
  console.log('Provider health reset');
}
