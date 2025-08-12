'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface WelcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function WelcomeModal({ isOpen, onClose }: WelcomeModalProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsVisible(true);
    } else {
      const timer = setTimeout(() => setIsVisible(false), 300);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  if (!isVisible) return null;

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center transition-opacity duration-300 ${
      isOpen ? 'opacity-100' : 'opacity-0'
    }`}>
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-8 max-w-2xl mx-4 border border-gray-700 shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Content */}
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
            Welcome to CMBAgent Info
          </h1>
          
          <p className="text-lg text-gray-300 mb-6">
            Your AI-powered assistant for cosmology and finance tools
          </p>

          <div className="grid md:grid-cols-2 gap-4 mb-8">
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-2xl mb-2">🚀</div>
              <h3 className="font-semibold mb-1">Instant Access</h3>
              <p className="text-sm text-gray-400">No setup required</p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-2xl mb-2">💡</div>
              <h3 className="font-semibold mb-1">AI-Powered</h3>
              <p className="text-sm text-gray-400">Smart code execution</p>
            </div>
          </div>

          <p className="text-gray-300 mb-6">
            Access the <strong>100 most-starred GitHub libraries</strong> in finance and astrophysics. 
            From portfolio optimization to cosmic microwave background analysis.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={onClose}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105"
            >
              Get Started
            </button>
            <Link
              href="/landing"
              className="border border-gray-600 text-gray-300 hover:text-white hover:border-gray-500 font-semibold py-3 px-6 rounded-lg transition-all duration-300"
            >
              Learn More
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
} 