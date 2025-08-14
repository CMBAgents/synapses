import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import "katex/dist/katex.min.css";
import { ThemeProvider } from "./context/theme-context";
import CopyScript from "./ui/copy-script";

// Import fonts for headings
import { Jersey_10 } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });
const jerseyFont = Jersey_10({ weight: "400", subsets: ["latin"], variable: "--font-jersey" });

export const metadata: Metadata = {
  title: "Multi-Domain Tools Help Assistant",
  description: "Interactive help assistant for Machine Learning, Astrophysics & Cosmology and Finance & Trading",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Context files should be pre-built and included in the deployment
  // No runtime context generation is needed

  return (
    <html lang="en" suppressHydrationWarning className={`${inter.className} ${jerseyFont.variable}`}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no" />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  // Function to get URL parameters - more robust implementation
                  function getUrlParam(name) {
                    try {
                      if (typeof window !== 'undefined') {
                        const urlParams = new URLSearchParams(window.location.search);
                        return urlParams.get(name);
                      }
                    } catch (e) {
                      console.error('Error getting URL params:', e);
                    }
                    return null;
                  }

                  // Check for URL parameter first (highest priority)
                  const urlTheme = getUrlParam('theme');
                  const isValidTheme = urlTheme === 'dark' || urlTheme === 'light';

                  // Determine theme: URL param > localStorage > system preference
                  let theme;
                  if (isValidTheme) {
                    theme = urlTheme;
                    // Save to localStorage to persist the choice
                    try {
                      localStorage.setItem('theme', theme);
                    } catch (e) {
                      console.error('Error saving theme to localStorage:', e);
                    }
                  } else {
                    // Check for saved theme preference or use browser default
                    try {
                      theme = localStorage.getItem('theme');
                    } catch (e) {
                      console.error('Error reading theme from localStorage:', e);
                    }

                    if (!theme) {
                      theme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
                    }
                  }

                  // Apply theme immediately to prevent flash
                  if (theme === 'dark') {
                    document.documentElement.classList.add('dark');
                    document.documentElement.style.backgroundColor = '#1a202c';
                    if (document.body) document.body.style.backgroundColor = '#1a202c';
                  } else {
                    document.documentElement.classList.remove('dark');
                    document.documentElement.style.backgroundColor = '#ffffff';
                    if (document.body) document.body.style.backgroundColor = '#ffffff';
                  }
                } catch (e) {
                  console.error('Error in theme initialization script:', e);
                }
              })()
            `,
          }}
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Add copy buttons to code blocks after the page loads
              document.addEventListener('DOMContentLoaded', function() {
                setTimeout(function() {
                  const preElements = document.querySelectorAll('pre');
                  preElements.forEach(function(pre) {
                    // Make sure the pre element has position relative
                    pre.style.position = 'relative';
                    pre.style.overflow = 'visible';
                  });
                }, 1000);
              });
            `,
          }}
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  // Function to get URL parameters
                  function getUrlParam(name) {
                    try {
                      if (typeof window !== 'undefined') {
                        const urlParams = new URLSearchParams(window.location.search);
                        return urlParams.get(name);
                      }
                    } catch (e) {
                      console.error('Error getting URL params:', e);
                    }
                    return null;
                  }

                  // Check for scale parameter
                  const urlScale = getUrlParam('scale');
                  if (urlScale) {
                    const scaleValue = parseFloat(urlScale);
                    if (!isNaN(scaleValue) && scaleValue > 0) {
                      // Apply scaling directly to the html element
                      document.documentElement.style.fontSize = (16 * scaleValue) + 'px';
                    }
                  }
                } catch (e) {
                  console.error('Error in scale initialization script:', e);
                }
              })();
            `,
          }}
        />
      </head>
      <body className="min-h-screen" suppressHydrationWarning>
        <ThemeProvider>
          {children}
          <CopyScript />
        </ThemeProvider>
      </body>
    </html>
  );
}
