'use client';

import { useState, useEffect } from 'react';
import ChatContainer from "@/app/ui/chat-container";
import WelcomeModal from "@/app/ui/welcome-modal";
import { loadConfig, getDefaultProgram } from "@/app/utils/config";
import styles from "../styles/background.module.css";

export default function MainWithModalPage() {
  const [showWelcome, setShowWelcome] = useState(false);
  const [config, setConfig] = useState<any>(null);
  const [defaultProgram, setDefaultProgram] = useState<any>(null);

  useEffect(() => {
    // Check if user has seen the welcome modal before
    const hasSeenWelcome = localStorage.getItem('hasSeenWelcome');
    if (!hasSeenWelcome) {
      setShowWelcome(true);
    }

    // Load configuration
    const loadData = async () => {
      try {
        const configData = loadConfig();
        const defaultProgramData = getDefaultProgram();
        setConfig(configData);
        setDefaultProgram(defaultProgramData);
      } catch (error) {
        console.error('Error loading configuration:', error);
      }
    };

    loadData();
  }, []);

  const handleCloseWelcome = () => {
    setShowWelcome(false);
    localStorage.setItem('hasSeenWelcome', 'true');
  };

  if (!config || !defaultProgram) {
    return (
      <main className={styles.background}>
        <div className="flex items-center justify-center min-h-screen text-white">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p>Loading...</p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className={styles.background}>
      <div className={styles.blurOverlay}></div>
      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black opacity-40 dark:opacity-60"></div>

      {/* Content above overlay */}
      <div className="relative z-10 mx-auto my-4 sm:my-8 px-2 sm:px-4 w-full max-w-2xl lg:max-w-4xl xl:max-w-6xl text-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">
            Synapses
          </h1>
          <div className="flex gap-4">
            <button
              onClick={() => setShowWelcome(true)}
              className="text-blue-400 hover:text-blue-300 transition-colors text-sm"
            >
              Welcome Guide
            </button>
            <a 
              href="/landing" 
              className="text-blue-400 hover:text-blue-300 transition-colors text-sm"
            >
              ← Back to Landing
            </a>
          </div>
        </div>

        {/* Description */}
        <p className="text-center text-lg mb-8 max-w-2xl mx-auto italic font-semibold">
          A <strong>next-generation chatbot</strong> fluent in the language of the <strong>100 most-starred GitHub libraries</strong> in finance and astrophysics. From <strong>portfolio optimization</strong> to <em>cosmic microwave background</em> analysis, it instantly bridges <strong>code and insight</strong> — no setup required, just <em>smart execution.</em>
        </p>

        <ChatContainer
          programs={config.programs}
          defaultProgramId={defaultProgram.id}
        />
      </div>

      {/* Welcome Modal */}
      <WelcomeModal 
        isOpen={showWelcome} 
        onClose={handleCloseWelcome} 
      />
    </main>
  );
} 