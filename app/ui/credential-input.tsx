'use client';

import { useState } from 'react';

interface CredentialInputProps {
  credentialType: string;
  onCredentialsChange: (credentials: Record<string, string>) => void;
  onClose?: () => void;
}

export default function CredentialInput({ credentialType, onCredentialsChange, onClose }: CredentialInputProps) {
  const [credentials, setCredentials] = useState<Record<string, string>>({});
  const [selectedFileName, setSelectedFileName] = useState<string>('');

  const handleInputChange = (field: string, value: string) => {
    console.log('handleInputChange called:', { 
      field, 
      value: value ? 'Present' : 'Missing',
      valueLength: value ? value.length : 0,
      valuePreview: value ? value.substring(0, 100) + '...' : 'None'
    });
    
    const newCredentials = { ...credentials, [field]: value };
    console.log('New credentials object:', newCredentials);
    console.log('All fields present:', {
      serviceAccountKey: !!newCredentials.serviceAccountKey,
      projectId: !!newCredentials.projectId,
      location: !!newCredentials.location
    });
    
    setCredentials(newCredentials);
    console.log('About to call onCredentialsChange with:', newCredentials);
    onCredentialsChange(newCredentials);
    console.log('onCredentialsChange called');
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
                            // Store reference to trigger click
                            (window as any).fileInputRef = input;
                          }
                        }}
                        type="file" 
                        accept=".json"
                        aria-label="Select Vertex AI service account key JSON file"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) {
                            setSelectedFileName(file.name);
                            const reader = new FileReader();
                            reader.onload = (event) => {
                              try {
                                const jsonContent = event.target?.result as string;
                                // Validate JSON and extract project info
                                const serviceAccountData = JSON.parse(jsonContent);
                                
                                console.log('Service account data parsed:', {
                                  hasProjectId: !!serviceAccountData.project_id,
                                  projectId: serviceAccountData.project_id,
                                  hasLocation: !!serviceAccountData.location,
                                  hasRegion: !!serviceAccountData.region,
                                  hasZone: !!serviceAccountData.zone
                                });
                                
                                // Extract project ID and location from the service account
                                const projectId = serviceAccountData.project_id;
                                
                                // Try to get location from service account, or use common defaults
                                let location = 'us-central1'; // Default
                                if (serviceAccountData.location) {
                                  location = serviceAccountData.location;
                                } else if (serviceAccountData.region) {
                                  location = serviceAccountData.region;
                                } else if (serviceAccountData.zone) {
                                  // Convert zone to region (e.g., us-central1-a -> us-central1)
                                  location = serviceAccountData.zone.split('-').slice(0, -1).join('-');
                                }
                                
                                console.log('Extracted credentials:', {
                                  projectId,
                                  location,
                                  jsonContentLength: jsonContent.length
                                });
                                
                                // Set all credentials at once
                                console.log('About to set credentials:', {
                                  serviceAccountKey: jsonContent ? 'Present' : 'Missing',
                                  projectId: projectId ? 'Present' : 'Missing',
                                  location: location ? 'Present' : 'Missing'
                                });
                                
                                // Create the complete credentials object
                                const completeCredentials = {
                                  serviceAccountKey: jsonContent,
                                  projectId: projectId,
                                  location: location
                                };
                                
                                console.log('Complete credentials object:', completeCredentials);
                                
                                // Set all credentials at once using a single call
                                onCredentialsChange(completeCredentials);
                                
                                // Also update local state for display
                                setCredentials(completeCredentials);
                                
                                console.log('All credentials set at once');
                                
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
                          onClick={() => {
                            setSelectedFileName('');
                            handleInputChange('serviceAccountKey', '');
                            handleInputChange('projectId', '');
                            handleInputChange('location', '');
                          }}
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
                      </div>
                    )}

                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Upload your Google Cloud service account key JSON file. Project ID and location will be automatically extracted from the file.
                    </p>
                  </div>
                </div>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Your credentials are stored locally and never sent to our servers.
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
              value={credentials.apiKey || ''}
              onChange={(e) => handleInputChange('apiKey', e.target.value)}
            />
          </div>
        </div>
        <p className="text-xs text-white/60 mt-2">
          Your API key is stored locally and never sent to our servers.
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
              value={credentials.apiKey || ''}
              onChange={(e) => handleInputChange('apiKey', e.target.value)}
            />
          </div>
        </div>
        <p className="text-xs text-white/60 mt-2">
          Your API key is stored locally and never sent to our servers.
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
              value={credentials.apiKey || ''}
              onChange={(e) => handleInputChange('apiKey', e.target.value)}
            />
          </div>
        </div>
        <p className="text-xs text-white/60 mt-2">
          Your OpenRouter API key is stored locally and never sent to our servers.
        </p>
      </div>
    );
  }

  return null;
}
