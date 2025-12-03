/**
 * API Configuration
 * Centralized configuration for backend API endpoints
 */

// Use relative URLs in production, absolute URLs in development
const isDevelopment = import.meta.env.DEV;

export const API_CONFIG = {
  // Base URL - use proxy in development, adjust for production
  baseURL: isDevelopment ? '/api' : '/api',
  assetsURL: isDevelopment ? '/assets' : '/assets',
  
  // Full backend URL (for direct connections if needed)
  backendURL: 'http://localhost:5000',
  
  // Endpoints
  endpoints: {
    health: '/health',
    configKeys: '/config/keys',
    configHealth: '/config/health',
    chat: '/chat',
    chatClear: '/chat/clear',
    chatHistory: '/chat/history',
    generateVideo: '/generate/video',
    generateScript: '/generate/script',
    generateAudio: '/generate/audio',
    generateImages: '/generate/images',
    generateVideos: '/generate/videos',
    generateRender: '/generate/render',
    editorExport: '/editor/export',
    huggingfaceImageToVideo: '/huggingface/image-to-video',
  }
};

/**
 * Helper to build full API URL
 */
export function getApiUrl(endpoint: string): string {
  return `${API_CONFIG.baseURL}${endpoint}`;
}

/**
 * Helper to build full assets URL
 */
export function getAssetsUrl(path: string): string {
  // Remove leading slash if present
  const cleanPath = path.startsWith('/') ? path.slice(1) : path;
  return `${API_CONFIG.assetsURL}/${cleanPath}`;
}

/**
 * Check if backend is available
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(getApiUrl(API_CONFIG.endpoints.health), {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    return response.ok;
  } catch (error) {
    console.error('[API] Backend health check failed:', error);
    return false;
  }
}

export default API_CONFIG;
