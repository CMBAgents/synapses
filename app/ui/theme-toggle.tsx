'use client'

import { useTheme } from '@/app/context/theme-context'
import { FiSun, FiMoon } from 'react-icons/fi'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={() => {
        console.log('Theme toggle button clicked')
        toggleTheme()
      }}
      className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 dark:bg-transparent dark:hover:bg-gray-800 transition-colors flex items-center justify-center"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
    >
      {theme === 'light' ? (
        <FiMoon className="w-5 h-5 text-gray-700 dark:text-white" />
      ) : (
        <FiSun className="w-5 h-5 text-yellow-500" />
      )}
    </button>
  )
}
