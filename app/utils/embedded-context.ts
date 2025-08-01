// This file is auto-generated. Do not edit directly.
// Generated on 2025-08-01T11:15:18.475Z

/**
 * Embedded context content for each program
 * This avoids having to load context files at runtime
 */
export const embeddedContexts: Record<string, string> = {
  'camb': "This context is loaded from URL: https://camb.readthedocs.io/en/latest/_static/camb_docs_combined.md",
  'getdist': "This context is loaded from URL: https://getdist.readthedocs.io/en/latest/_static/getdist_docs_combined.md",
  'cobaya': "This context is loaded from URL: https://cobaya.readthedocs.io/en/latest/_static/cobaya_docs_combined.md",
};

/**
 * Get the embedded context for a program
 * @param programId The ID of the program
 * @returns The embedded context content or undefined if not found
 */
export function getEmbeddedContext(programId: string): string | undefined {
  return embeddedContexts[programId];
}
