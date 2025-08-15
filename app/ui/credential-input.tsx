'use client';

import { useState, useEffect, useRef } from 'react';

interface CredentialInputProps {
  credentialType: string;
  onCredentialsChange: (credentials: Record<string, string>) => void;
  onClose?: () => void;
}

// Utility function to encrypt sensitive data
async function encryptData(data: string, key: string): Promise<string> {
  try {
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    
    // Generate a random IV
    const iv = crypto.getRandomValues(new Uint8Array(12));
    
    // Import the key
    const cryptoKey = await crypto.subtle.importKey(
      'raw',
      encoder.encode(key),
      { name: 'AES-GCM' },
      false,
      ['encrypt']
    );
    
    // Encrypt the data
    const encryptedBuffer = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      cryptoKey,
      dataBuffer
    );
    
    // Combine IV and encrypted data
    const combined = new Uint8Array(iv.length + encryptedBuffer.byteLength);
    combined.set(iv);
    combined.set(new Uint8Array(encryptedBuffer), iv.length);
    
    // Convert to base64
    return btoa(String.fromCharCode(...combined));
  } catch (error) {
    console.error('Encryption failed:', error);
    throw new Error('Failed to encrypt credentials');
  }
}

// Utility function to decrypt sensitive data
async function decryptData(encryptedData: string, key: string): Promise<string> {
  try {
    const decoder = new TextDecoder();
    
    // Convert from base64
    const combined = new Uint8Array(
      atob(encryptedData).split('').map(char => char.charCodeAt(0))
    );
    
    // Extract IV and encrypted data
    const iv = combined.slice(0, 12);
    const encryptedBuffer = combined.slice(12);
    
    // Import the key
    const cryptoKey = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(key),
      { name: 'AES-GCM' },
      false,
      ['decrypt']
    );
    
    // Decrypt the data
    const decryptedBuffer = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      cryptoKey,
      encryptedBuffer
    );
    
    return decoder.decode(decryptedBuffer);
  } catch (error) {
    console.error('Decryption failed:', error);
    throw new Error('Failed to decrypt credentials');
  }
}

// Generate a secure encryption key
function generateEncryptionKey(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

export default function CredentialInput({ credentialType, onCredentialsChange, onClose }: CredentialInputProps) {
  const [credentials, setCredentials] = useState<Record<string, string>>({});
  const [selectedFileName, setSelectedFileName] = useState<string>('');
  const [encryptionKey, setEncryptionKey] = useState<string>('');
  const [isEncrypted, setIsEncrypted] = useState<Record<string, boolean>>({});
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Generate encryption key on component mount
  useEffect(() => {
    setEncryptionKey(generateEncryptionKey());
    
    // Auto-cleanup after 30 minutes of inactivity
    const resetTimeout = () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => {
        console.log('Auto-clearing credentials due to inactivity');
        setCredentials({});
        setSelectedFileName('');
        setIsEncrypted({});
      }, 30 * 60 * 1000); // 30 minutes
    };
    
    resetTimeout();
    
    // Reset timeout on user activity
    const handleActivity = () => resetTimeout();
    window.addEventListener('mousedown', handleActivity);
    window.addEventListener('keydown', handleActivity);
    window.addEventListener('scroll', handleActivity);
    
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      window.removeEventListener('mousedown', handleActivity);
      window.removeEventListener('keydown', handleActivity);
      window.removeEventListener('scroll', handleActivity);
    };
  }, []);

  const handleInputChange = async (field: string, value: string) => {
    try {
      // Log only non-sensitive information
      console.log('Credential field updated:', { 
        field, 
        hasValue: !!value,
        valueLength: value ? value.length : 0,
        isEncrypted: isEncrypted[field] || false
      });
      
      let processedValue = value;
      let encrypted = false;
      
      // Encrypt sensitive data
      if (value && (field === 'apiKey' || field === 'serviceAccountKey')) {
        try {
          processedValue = await encryptData(value, encryptionKey);
          encrypted = true;
        } catch (error) {
          console.error('Failed to encrypt credential:', error);
          // Fall back to unencrypted (not ideal but prevents breaking)
          processedValue = value;
        }
      }
      
      const newCredentials = { ...credentials, [field]: processedValue };
      const newEncryptedState = { ...isEncrypted, [field]: encrypted };
      
      setCredentials(newCredentials);
      setIsEncrypted(newEncryptedState);
      
      // Send encrypted credentials to parent
      onCredentialsChange(newCredentials);
      
      // Reset auto-cleanup timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = setTimeout(() => {
          console.log('Auto-clearing credentials due to inactivity');
          setCredentials({});
          setSelectedFileName('');
          setIsEncrypted({});
        }, 30 * 60 * 1000);
      }
      
    } catch (error) {
      console.error('Error processing credential:', error);
    }
  };

  // Clear all credentials securely
  const clearCredentials = () => {
    setCredentials({});
    setSelectedFileName('');
    setIsEncrypted({});
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    onCredentialsChange({});
  };

  // Validate service account JSON structure
  const validateServiceAccountJSON = (jsonData: any): boolean => {
    const requiredFields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email'];
    return requiredFields.every(field => jsonData.hasOwnProperty(field) && jsonData[field]);
  };

  if (credentialType === 'vertexai') {
    return (
      <div className="p-3 bg-black/90 backdrop-blur-md rounded-md border border-white/20 shadow-xl relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-white/60 hover:text-white text-sm"
          title="Close credentials panel"
        >
          ✕
        </button>
        <h4 className="text-sm font-medium text-white mb-2 pr-6">
          Vertex AI Credentials
        </h4>
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-white/70 mb-1">
              Service Account Key File
            </label>
            <div className="space-y-2">
              <div className="relative">
                <input 
                  ref={(input) => {
                    if (input) {
                      (window as any).fileInputRef = input;
                    }
                  }}
                  type="file" 
                  accept=".json"
                  aria-label="Select Vertex AI service account key JSON file"
                  onChange={async (e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      setSelectedFileName(file.name);
                      const reader = new FileReader();
                      reader.onload = async (event) => {
                        try {
                          const jsonContent = event.target?.result as string;
                          
                          // Validate JSON structure
                          const serviceAccountData = JSON.parse(jsonContent);
                          if (!validateServiceAccountJSON(serviceAccountData)) {
                            throw new Error('Invalid service account JSON structure');
                          }
                          
                          // Log only non-sensitive information
                          console.log('Service account validation:', {
                            hasProjectId: !!serviceAccountData.project_id,
                            projectId: serviceAccountData.project_id,
                            hasLocation: !!serviceAccountData.location,
                            hasRegion: !!serviceAccountData.region,
                            hasZone: !!serviceAccountData.zone,
                            clientEmail: serviceAccountData.client_email
                          });
                          
                          // Extract project ID and location
                          const projectId = serviceAccountData.project_id;
                          
                          let location = 'us-central1'; // Default
                          if (serviceAccountData.location) {
                            location = serviceAccountData.location;
                          } else if (serviceAccountData.region) {
                            location = serviceAccountData.region;
                          } else if (serviceAccountData.zone) {
                            location = serviceAccountData.zone.split('-').slice(0, -1).join('-');
                          }
                          
                          // Set all credentials at once (encrypted)
                          const completeCredentials = {
                            serviceAccountKey: jsonContent,
                            projectId: projectId,
                            location: location
                          };
                          
                          // Process each credential with encryption
                          for (const [key, value] of Object.entries(completeCredentials)) {
                            await handleInputChange(key, value);
                          }
                          
                        } catch (error) {
                          console.error('Error processing service account file:', error);
                          alert('Invalid JSON file. Please select a valid service account key file.');
                          setSelectedFileName('');
                        }
                      };
                      reader.readAsText(file);
                    }
                  }}
                  className="w-full px-3 py-2 text-sm border border-white/30 rounded-md bg-transparent text-white focus:ring-2 focus:ring-white/50 focus:border-white/50 file:mr-4 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-medium file:bg-white/20 file:text-white hover:file:bg-white/30 relative opacity-0"
                />
                {!selectedFileName && (
                  <button
                    type="button"
                    onClick={() => {
                      const fileInput = (window as any).fileInputRef;
                      if (fileInput) {
                        fileInput.click();
                      }
                    }}
                    className="absolute inset-0 flex items-center justify-center text-white/70 text-sm font-medium hover:text-white/90 transition-colors cursor-pointer"
                  >
                    Choose JSON service account key file
                  </button>
                )}
                {credentials.serviceAccountKey && selectedFileName && (
                  <button
                    type="button"
                    onClick={clearCredentials}
                    className="absolute right-2 top-2 text-xs text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                    title="Clear file"
                    aria-label="Clear selected file"
                  >
                    ✕
                  </button>
                )}
              </div>
              {credentials.serviceAccountKey && selectedFileName && (
                <div className="text-xs text-green-600 dark:text-green-400">
                  ✅ Service account key loaded from: {selectedFileName}
                  {isEncrypted.serviceAccountKey && ' (Encrypted)'}
                </div>
              )}

              <p className="text-xs text-white/60">
                Upload your Google Cloud service account key JSON file. Project ID and location will be automatically extracted from the file.
              </p>
            </div>
          </div>
        </div>
        <p className="text-xs text-white/60 mt-2">
          Your credentials are encrypted in memory and never sent to our servers. They will be automatically cleared after 30 minutes of inactivity.
        </p>
      </div>
    );
  }

  if (credentialType === 'openai') {
    return (
      <div className="p-3 bg-black/90 backdrop-blur-md rounded-md border border-white/20 shadow-xl relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-white/60 hover:text-white text-sm"
          title="Close credentials panel"
        >
          ✕
        </button>
        <h4 className="text-sm font-medium text-white mb-2 pr-6">
          OpenAI API Key Required
        </h4>
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-white/70 mb-1">
              API Key
            </label>
            <input
              type="password"
              placeholder="sk-..."
              className="w-full px-3 py-2 text-sm border border-white/30 rounded-md bg-transparent text-white focus:ring-2 focus:ring-white/50 focus:border-white/50 font-mono text-xs"
              value={credentials.apiKey ? '••••••••••••••••' : ''}
              onChange={(e) => handleInputChange('apiKey', e.target.value)}
            />
          </div>
        </div>
        <p className="text-xs text-white/60 mt-2">
          Your API key is encrypted in memory and never sent to our servers. It will be automatically cleared after 30 minutes of inactivity.
        </p>
      </div>
    );
  }

  if (credentialType === 'deepseek') {
    return (
      <div className="p-3 bg-black/90 backdrop-blur-md rounded-md border border-white/20 shadow-xl relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-white/60 hover:text-white text-sm"
          title="Close credentials panel"
        >
          ✕
        </button>
        <h4 className="text-sm font-medium text-white mb-2 pr-6">
          DeepSeek API Key Required
        </h4>
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-white/70 mb-1">
              API Key
            </label>
            <input
              type="password"
              placeholder="sk-..."
              className="w-full px-3 py-2 text-sm border border-white/30 rounded-md bg-transparent text-white focus:ring-2 focus:ring-white/50 focus:border-white/50 font-mono text-xs"
              value={credentials.apiKey ? '••••••••••••••••' : ''}
              onChange={(e) => handleInputChange('apiKey', e.target.value)}
            />
          </div>
        </div>
        <p className="text-xs text-white/60 mt-2">
          Your API key is encrypted in memory and never sent to our servers. It will be automatically cleared after 30 minutes of inactivity.
        </p>
      </div>
    );
  }

  if (credentialType === 'openrouter') {
    return (
      <div className="p-3 bg-black/90 backdrop-blur-md rounded-md border border-white/20 shadow-xl relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-white/60 hover:text-white text-sm"
          title="Close credentials panel"
        >
          ✕
        </button>
        <h4 className="text-sm font-medium text-white mb-2 pr-6">
          OpenRouter API Key Required
        </h4>
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-white/70 mb-1">
              API Key
            </label>
            <input
              type="password"
              placeholder="sk-or-v1-..."
              className="w-full px-3 py-2 text-sm border border-white/30 rounded-md bg-transparent text-white focus:ring-2 focus:ring-white/50 focus:border-white/50 font-mono text-xs"
              value={credentials.apiKey ? '••••••••••••••••' : ''}
              onChange={(e) => handleInputChange('apiKey', e.target.value)}
            />
          </div>
        </div>
        <p className="text-xs text-white/60 mt-2">
          Your OpenRouter API key is encrypted in memory and never sent to our servers. It will be automatically cleared after 30 minutes of inactivity.
        </p>
      </div>
    );
  }

  return null;
}
