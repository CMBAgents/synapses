export interface ContextFile {
  name: string;
  content: string;
  domain: 'astronomy' | 'finance' | 'biochemistry' | 'machinelearning';
}

export async function loadContextFile(domain: 'astronomy' | 'finance' | 'biochemistry' | 'machinelearning', fileName: string): Promise<string | null> {
  try {
    const response = await fetch(`/api/context?domain=${domain}&action=loadContextFile&fileName=${fileName}`);
    if (response.ok) {
      const data = await response.json();
      return data.content;
    }
    return null;
  } catch (error) {
    console.error(`Error loading context file ${fileName} for domain ${domain}:`, error);
    return null;
  }
}

export async function getContextFilesForDomain(domain: 'astronomy' | 'finance' | 'biochemistry' | 'machinelearning'): Promise<ContextFile[]> {
  try {
    const response = await fetch(`/api/context?domain=${domain}&action=getContextFiles`);
    if (response.ok) {
      return await response.json();
    }
    return [];
  } catch (error) {
    console.error(`Error loading context files for domain ${domain}:`, error);
    return [];
  }
}

export async function hasContextFile(domain: 'astronomy' | 'finance' | 'biochemistry' | 'machinelearning', fileName: string): Promise<boolean> {
  try {
    const response = await fetch(`/api/context?domain=${domain}&action=hasContextFile&fileName=${fileName}`);
    if (response.ok) {
      const data = await response.json();
      return data.hasFile;
    }
    return false;
  } catch (error) {
    return false;
  }
}

export async function updateLibrariesWithContextStatus(domain: 'astronomy' | 'finance' | 'biochemistry' | 'machinelearning') {
  try {
    const response = await fetch(`/api/context?domain=${domain}&action=updateLibrariesWithContextStatus`);
    if (response.ok) {
      const data = await response.json();
      return data.data;
    }
    return null;
  } catch (error) {
    console.error(`Error updating context status for domain ${domain}:`, error);
    return null;
  }
}

export async function updateAllLibrariesWithContextStatus() {
  const domains: Array<'astronomy' | 'finance' | 'biochemistry' | 'machinelearning'> = ['astronomy', 'finance', 'biochemistry', 'machinelearning'];
  const results = await Promise.all(
    domains.map(domain => updateLibrariesWithContextStatus(domain))
  );
  return results;
} 