/**
 * API Keys Service
 * Manages connection to backend for API keys with automatic reconnection
 */

import { API_CONFIG, getApiUrl } from '@/config/api';

interface ApiKeys {
  groq: string;
  gemini: string;
  pexels: string;
  huggingface: string;
  replicate: string;
  runway: string;
  stability: string;
}

interface ApiKeysResponse {
  keys: ApiKeys;
  sanitized: ApiKeys;
  status: 'connected' | 'disconnected';
}

interface ConfigHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  keys: Record<string, boolean>;
  message: string;
}

class ApiKeysService {
  private static instance: ApiKeysService;
  private keys: ApiKeys | null = null;
  private isConnected: boolean = false;
  private reconnectInterval: NodeJS.Timeout | null = null;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = Infinity; // Infinite reconnection for lifetime connection
  private baseUrl = API_CONFIG.baseURL;

  private constructor() {
    // Initialize connection on creation
    this.connect();
    // Start heartbeat to maintain connection
    this.startHeartbeat();
  }

  public static getInstance(): ApiKeysService {
    if (!ApiKeysService.instance) {
      ApiKeysService.instance = new ApiKeysService();
    }
    return ApiKeysService.instance;
  }

  /**
   * Connect to backend and fetch API keys
   */
  public async connect(): Promise<boolean> {
    try {
      console.log('[API Keys] Connecting to backend...');
      
      const response = await fetch(getApiUrl(API_CONFIG.endpoints.configKeys), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch API keys: ${response.status}`);
      }

      const data: ApiKeysResponse = await response.json();
      
      if (data.status === 'connected' && data.keys) {
        this.keys = data.keys;
        this.isConnected = true;
        this.reconnectAttempts = 0;
        console.log('[API Keys] ✅ Connected successfully');
        console.log('[API Keys] Sanitized keys:', data.sanitized);
        return true;
      } else {
        throw new Error('Backend returned disconnected status');
      }
    } catch (error) {
      console.error('[API Keys] ❌ Connection failed:', error);
      this.isConnected = false;
      this.scheduleReconnect();
      return false;
    }
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectInterval) {
      return; // Already scheduled
    }

    this.reconnectAttempts++;
    
    // Exponential backoff with max 30 seconds
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    
    console.log(`[API Keys] 🔄 Reconnecting in ${delay / 1000}s... (attempt ${this.reconnectAttempts})`);
    
    this.reconnectInterval = setTimeout(() => {
      this.reconnectInterval = null;
      this.connect();
    }, delay);
  }

  /**
   * Start heartbeat to check connection health
   * Runs every 30 seconds to ensure connection stays alive
   */
  private startHeartbeat(): void {
    setInterval(async () => {
      if (!this.isConnected) {
        console.log('[API Keys] ⚠️ Connection lost, attempting to reconnect...');
        await this.connect();
        return;
      }

      try {
        const health = await this.checkHealth();
        if (health.status === 'unhealthy') {
          console.log('[API Keys] ⚠️ Backend unhealthy, reconnecting...');
          this.isConnected = false;
          await this.connect();
        } else {
          console.log('[API Keys] ❤️ Heartbeat: Connection healthy');
        }
      } catch (error) {
        console.error('[API Keys] ❌ Heartbeat failed:', error);
        this.isConnected = false;
        this.scheduleReconnect();
      }
    }, 30000); // Check every 30 seconds
  }

  /**
   * Check backend health
   */
  public async checkHealth(): Promise<ConfigHealth> {
    const response = await fetch(getApiUrl(API_CONFIG.endpoints.configHealth));
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  }

  /**
   * Get API keys (returns null if not connected)
   */
  public getKeys(): ApiKeys | null {
    return this.keys;
  }

  /**
   * Get specific API key
   */
  public getKey(keyName: keyof ApiKeys): string | null {
    if (!this.keys) {
      console.warn(`[API Keys] Key '${keyName}' requested but not connected`);
      return null;
    }
    return this.keys[keyName] || null;
  }

  /**
   * Check if service is connected
   */
  public isServiceConnected(): boolean {
    return this.isConnected;
  }

  /**
   * Force reconnection
   */
  public async forceReconnect(): Promise<boolean> {
    console.log('[API Keys] 🔄 Force reconnecting...');
    this.reconnectAttempts = 0;
    if (this.reconnectInterval) {
      clearTimeout(this.reconnectInterval);
      this.reconnectInterval = null;
    }
    return this.connect();
  }

  /**
   * Get connection status for display
   */
  public getStatus(): {
    connected: boolean;
    attempts: number;
    keysLoaded: boolean;
  } {
    return {
      connected: this.isConnected,
      attempts: this.reconnectAttempts,
      keysLoaded: this.keys !== null,
    };
  }
}

// Export singleton instance
export const apiKeysService = ApiKeysService.getInstance();

// Export types
export type { ApiKeys, ApiKeysResponse, ConfigHealth };
