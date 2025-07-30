'use client'

import { useEffect } from 'react'

export default function CopyScript() {
  useEffect(() => {
    // Function to create and add copy buttons to code blocks
    const addCopyButtons = () => {
      // Find all pre elements
      const preElements = document.querySelectorAll('pre')
      
      preElements.forEach(pre => {
        // Skip if already processed
        if (pre.querySelector('.copy-code-button')) return
        
        // Make sure pre has position relative
        pre.style.position = 'relative'
        pre.style.overflow = 'visible'
        
        // Create copy button
        const copyButton = document.createElement('button')
        copyButton.className = 'copy-code-button'
        copyButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
        copyButton.style.position = 'absolute'
        copyButton.style.top = '0.5rem'
        copyButton.style.right = '0.5rem'
        copyButton.style.padding = '0.25rem'
        copyButton.style.background = '#4a5568'
        copyButton.style.color = 'white'
        copyButton.style.borderRadius = '0.25rem'
        copyButton.style.cursor = 'pointer'
        copyButton.style.zIndex = '50'
        copyButton.title = 'Copy to clipboard'
        
        // Add click event
        copyButton.addEventListener('click', () => {
          // Get code text
          const code = pre.querySelector('code')
          const text = code ? code.textContent || '' : pre.textContent || ''
          
          // Copy to clipboard
          navigator.clipboard.writeText(text).then(() => {
            // Show success state
            copyButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'
            copyButton.style.background = '#48bb78'
            
            // Reset after 2 seconds
            setTimeout(() => {
              copyButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
              copyButton.style.background = '#4a5568'
            }, 2000)
          }).catch(err => {
            console.error('Failed to copy text: ', err)
          })
        })
        
        // Add button to pre element
        pre.appendChild(copyButton)
      })
    }
    
    // Run initially
    addCopyButtons()
    
    // Set up a MutationObserver to detect when new code blocks are added
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          // Wait a bit for React to finish rendering
          setTimeout(addCopyButtons, 100)
        }
      })
    })
    
    // Start observing the document body for DOM changes
    observer.observe(document.body, { childList: true, subtree: true })
    
    // Clean up
    return () => {
      observer.disconnect()
    }
  }, [])
  
  return null
}
