'use client';

import { useState } from 'react';

interface CredentialInputProps {
  credentialType: string;
  onCredentialsChange: (credentials: Record<string, string>) => void;
}

export default function CredentialInput({ credentialType, onCredentialsChange }: CredentialInputProps) {
  const [credentials, setCredentials] = useState<Record<string, string>>({});

  const handleInputChange = (field: string, value: string) => {
    const newCredentials = { ...credentials, [field]: value };
    setCredentials(newCredentials);
    onCredentialsChange(newCredentials);
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
              Project ID
            </label>
            <input
              type="text"
              placeholder="your-project-id"
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={credentials.projectId || ''}
              onChange={(e) => handleInputChange('projectId', e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
              Location
            </label>
            <input
              type="text"
              placeholder="us-central1"
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={credentials.location || ''}
              onChange={(e) => handleInputChange('location', e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
              Service Account Key (JSON)
            </label>
            <textarea
              placeholder="Paste your service account JSON key here..."
              rows={4}
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-xs"
              value={credentials.serviceAccountKey || ''}
              onChange={(e) => handleInputChange('serviceAccountKey', e.target.value)}
            />
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
