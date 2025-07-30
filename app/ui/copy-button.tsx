'use client'

import { useState } from 'react'
import { FiCopy, FiCheck } from 'react-icons/fi'

interface CopyButtonProps {
  text: string
}

export default function CopyButton({ text }: CopyButtonProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  return (
    <button
      onClick={handleCopy}
      className="absolute top-2 right-2 p-1.5 rounded-md bg-gray-700 dark:bg-gray-800 text-white hover:bg-gray-600 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 copy-button shadow-md"
      aria-label="Copy code"
      title="Copy to clipboard"
      style={{ opacity: 1, zIndex: 50 }}
    >
      {copied ? (
        <FiCheck className="h-4 w-4 text-green-500" />
      ) : (
        <FiCopy className="h-4 w-4" />
      )}
    </button>
  )
}
