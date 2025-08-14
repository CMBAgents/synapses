'use client';

import { useState } from 'react';

interface CredentialInputProps {
  credentialType: string;
  onCredentialsChange: (credentials: Record<string, string>) => void;
}

export default function CredentialInput({ credentialType, onCredentialsChange }: CredentialInputProps) {
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
            <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Vertex AI Credentials Required
              </h4>
              <div className="space-y-2">
                <div>
                  <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                    Service Account Key File
                  </label>
                  <div className="space-y-2">
                    <div className="relative">
                      <input 
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
                                
                                handleInputChange('serviceAccountKey', jsonContent);
                                console.log('After setting serviceAccountKey, current state:', credentials);
                                
                                handleInputChange('projectId', projectId);
                                console.log('After setting projectId, current state:', credentials);
                                
                                handleInputChange('location', location);
                                console.log('After setting location, current state:', credentials);
                                
                                console.log('All credentials set, final state:', credentials);
                                
                              } catch (error) {
                                console.error('Error processing service account file:', error);
                                alert('Invalid JSON file. Please select a valid service account key file.');
                                setSelectedFileName('');
                              }
                            };
                            reader.readAsText(file);
                          }
                        }}
                        className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent file:mr-4 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900 dark:file:text-blue-300"
                      />
                      {!selectedFileName && (
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none text-gray-400 dark:text-gray-500 text-sm">
                          Click to select a JSON service account key file
                        </div>
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
                    {credentials.projectId && (
                      <div className="text-xs text-blue-600 dark:text-blue-400">
                        📍 Project ID: {credentials.projectId}
                      </div>
                    )}
                    {credentials.location && (
                      <div className="text-xs text-blue-600 dark:text-blue-400">
                        🌍 Location: {credentials.location}
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
      <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          OpenAI API Key Required
        </h4>
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
              API Key
            </label>
            <input
              type="password"
              placeholder="sk-..."
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-xs"
              value={credentials.apiKey || ''}
              onChange={(e) => handleInputChange('apiKey', e.target.value)}
            />
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          Your API key is stored locally and never sent to our servers.
        </p>
      </div>
    );
  }

  if (credentialType === 'deepseek') {
    return (
      <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-md border border-gray-200 dark:border-gray-700">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          DeepSeek API Key Required
        </h4>
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
              API Key
            </label>
            <input
              type="password"
              placeholder="sk-..."
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-xs"
              value={credentials.apiKey || ''}
              onChange={(e) => handleInputChange('apiKey', e.target.value)}
            />
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          Your API key is stored locally and never sent to our servers.
        </p>
      </div>
    );
  }

  return null;
}
