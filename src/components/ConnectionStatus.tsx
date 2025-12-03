import { useState, useEffect } from 'react';
import { apiKeysService } from '../services/apiKeysService';

export const ConnectionStatus = () => {
  const [status, setStatus] = useState(apiKeysService.getStatus());
  const [health, setHealth] = useState<'healthy' | 'degraded' | 'unhealthy' | 'checking'>('checking');

  useEffect(() => {
    // Update status every 5 seconds
    const interval = setInterval(() => {
      const newStatus = apiKeysService.getStatus();
      setStatus(newStatus);

      // Check health if connected
      if (newStatus.connected) {
        apiKeysService.checkHealth()
          .then(healthData => setHealth(healthData.status))
          .catch(() => setHealth('unhealthy'));
      } else {
        setHealth('unhealthy');
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleReconnect = async () => {
    setHealth('checking');
    await apiKeysService.forceReconnect();
    const newStatus = apiKeysService.getStatus();
    setStatus(newStatus);
  };

  const getStatusColor = () => {
    if (!status.connected) return 'bg-red-500';
    if (health === 'healthy') return 'bg-green-500';
    if (health === 'degraded') return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getStatusText = () => {
    if (!status.connected) {
      return status.attempts > 0 
        ? `Reconnecting... (${status.attempts})` 
        : 'Disconnected';
    }
    if (health === 'healthy') return 'Connected';
    if (health === 'degraded') return 'Connected (Degraded)';
    if (health === 'checking') return 'Checking...';
    return 'Unhealthy';
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className="bg-gray-900/90 backdrop-blur-sm border border-gray-700 rounded-lg px-4 py-2 flex items-center gap-3 shadow-lg">
        {/* Status Indicator */}
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${getStatusColor()} animate-pulse`} />
          <span className="text-sm text-gray-300">{getStatusText()}</span>
        </div>

        {/* Reconnect Button (show if not connected) */}
        {!status.connected && (
          <button
            onClick={handleReconnect}
            className="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded transition-colors"
          >
            Reconnect
          </button>
        )}

        {/* Keys Status */}
        {status.connected && status.keysLoaded && (
          <div className="text-xs text-green-400 flex items-center gap-1">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            API Keys Loaded
          </div>
        )}
      </div>
    </div>
  );
};
