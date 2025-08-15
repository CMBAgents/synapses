'use client';

import { useState, useEffect, useRef } from 'react';
import { ModelConfig } from '@/app/utils/types';
import CredentialInput from './credential-input';

interface ModelSelectorProps {
  models: ModelConfig[];
  selectedModelId: string;
  onModelChange: (modelId: string) => void;
  onCredentialsChange?: (credentials: Record<string, Record<string, string>>) => void;
}

export default function ModelSelector({ models, selectedModelId, onModelChange, onCredentialsChange }: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState<ModelConfig | undefined>(
    models.find(model => model.id === selectedModelId) || models[0]
  );
  const [credentials, setCredentials] = useState<Record<string, Record<string, string>>>({});
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, right: 0 });
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Update the selected model when the selectedModelId prop changes
  useEffect(() => {
    const model = models.find(model => model.id === selectedModelId) || models[0];
    setSelected(model);
  }, [selectedModelId, models]);

  // Add click outside handler to close the dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    // Add event listener when dropdown is open
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    // Clean up the event listener
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // If there's only one model, don't show the selector
  if (models.length <= 1) {
    return null;
  }

  const toggleDropdown = () => {
    if (!isOpen && buttonRef.current) {
      // Calculate position when opening the dropdown
      const rect = buttonRef.current.getBoundingClientRect();
      setDropdownPosition({
        top: rect.bottom + window.scrollY,
        right: window.innerWidth - rect.right
      });
    }
    setIsOpen(!isOpen);
  };

  const closeDropdown = () => setIsOpen(false);

  const handleModelSelect = (model: ModelConfig) => {
    setSelected(model);
    onModelChange(model.id);
    closeDropdown();
  };

  const handleCredentialsChange = (modelId: string, newCredentials: Record<string, string>) => {
    console.log('ModelSelector handleCredentialsChange:', { modelId, newCredentials });
    const updatedCredentials = {
      ...credentials,
      [modelId]: newCredentials
    };
    console.log('Updated credentials in ModelSelector:', updatedCredentials);
    setCredentials(updatedCredentials);
    
    // Call parent callback if provided
    if (onCredentialsChange) {
      console.log('Calling parent onCredentialsChange with:', updatedCredentials);
      onCredentialsChange(updatedCredentials);
    }
  };



  return (
    <div className="relative inline-block text-left w-full" ref={dropdownRef}>
      <div>
        <button
          ref={buttonRef}
          type="button"
          className="inline-flex justify-between items-center w-full rounded-md border border-white/30 shadow-sm px-4 py-2 bg-transparent text-sm font-medium text-white hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white/50"
          id="model-selector"
          aria-haspopup="true"
          aria-expanded={isOpen}
          onClick={toggleDropdown}
        >
          <span className="flex items-center">
            <span className="ml-1 mr-2">{selected?.name || 'Select Model'}</span>
          </span>
          <svg
            className="-mr-1 ml-2 h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
      
      {/* Show credential input if the selected model requires credentials */}
      {selected?.requiresCredentials && selected.credentialType && (
        <>
          <CredentialInput
            credentialType={selected.credentialType}
            onCredentialsChange={(newCredentials) => handleCredentialsChange(selected.id, newCredentials)}
          />
        </>
      )}

      {isOpen && (
        <div
          className="origin-top-right rounded-md shadow-lg bg-black/80 backdrop-blur-sm ring-1 ring-white/20 z-[100]"
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="model-selector"
          style={{
            maxHeight: '80vh',
            overflowY: 'auto',
            position: 'fixed',
            top: `${dropdownPosition.top}px`,
            right: `${dropdownPosition.right}px`,
            width: buttonRef.current ? `${buttonRef.current.offsetWidth}px` : '14rem'
          }}
        >
          <div className="py-1" role="none">
            {models.map((model) => (
              <button
                key={model.id}
                className={`${
                  selected?.id === model.id ? 'bg-white/20 text-white' : 'text-white/80'
                } block w-full text-left px-4 py-2 text-sm hover:bg-white/10`}
                role="menuitem"
                onClick={() => handleModelSelect(model)}
              >
                <div className="flex flex-col">
                  <span className="font-medium">{model.name}</span>
                  {model.description && (
                    <span className="text-xs text-white/60">{model.description}</span>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
