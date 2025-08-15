import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import CopyScript from "./ui/copy-script";

// Import fonts for headings
import { Jersey_10 } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });
const jerseyFont = Jersey_10({ weight: "400", subsets: ["latin"], variable: "--font-jersey" });

export const metadata: Metadata = {
  title: "Multi-Domain Tools Help Assistant",
  description: "Interactive help assistant for Machine Learning, Astrophysics & Cosmology and Finance & Trading",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no" />
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
        {children}
        <CopyScript />
      </body>
    </html>
  );
}
