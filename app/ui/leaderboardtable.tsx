"use client";

import { useRouter, usePathname } from 'next/navigation';

type LibraryEntry = {
  rank: number;
  name: string;
  github_url: string;
  stars: number;
  hasContextFile?: boolean;
  contextFileName?: string;
};

type LeaderboardTableProps = {
  title: string;
  libraries: LibraryEntry[];
};

export default function LeaderboardTable({ title, libraries }: LeaderboardTableProps) {
  const router = useRouter();
  const pathname = usePathname();
  
  // Déterminer le domaine basé sur le pathname
  const getDomain = () => {
    if (pathname.includes('/leaderboard/astronomy')) return 'astronomy';
    if (pathname.includes('/leaderboard/finance')) return 'finance';
    if (pathname.includes('/leaderboard/biochemistry')) return 'biochemistry';
    if (pathname.includes('/leaderboard/machinelearning')) return 'machinelearning';
    if (pathname.includes('/chat/astronomy')) return 'astronomy';
    if (pathname.includes('/chat/finance')) return 'finance';
    if (pathname.includes('/chat/biochemistry')) return 'biochemistry';
    if (pathname.includes('/chat/machinelearning')) return 'machinelearning';
    if (pathname.includes('astronomy')) return 'astronomy';
    if (pathname.includes('finance')) return 'finance';
    if (pathname.includes('biochemistry')) return 'biochemistry';
    if (pathname.includes('machinelearning')) return 'machinelearning';
    return 'astronomy'; // fallback
  };
  
  const handleLibraryClick = (libraryName: string) => {
    const domain = getDomain();
    // Navigate to the chat page with the pre-selected library
    router.push(`/chat/${domain}?library=${encodeURIComponent(libraryName)}`);
  };
  
  return (
    <div className="flex flex-col bg-white/10 backdrop-blur-sm rounded-xl shadow-lg p-2 sm:p-4 text-xs sm:text-sm w-full max-w-[350px] sm:max-w-[600px] md:max-w-[900px] max-h-[70vh] border border-white/20">
      {title && (
        <h2 className="text-base sm:text-lg font-semibold text-center text-white mb-2 sm:mb-3">
          {title}
        </h2>
      )}

      <div className="flex-1 overflow-y-auto min-h-0">
        <table className="w-full table-fixed border-collapse border border-white/30 text-center text-white">
        <thead>
          <tr className="bg-white/20">
            <th className="border border-white/30 px-1 sm:px-2 py-1 w-8 sm:w-12">Rank</th>
            <th className="border border-white/30 px-1 sm:px-2 py-1">Library</th>
            <th className="border border-white/30 px-1 sm:px-2 py-1 w-8 sm:w-12 md:w-16">
              <span className="hidden sm:inline">GitHub</span>
              <span className="sm:hidden">Git</span>
            </th>
            <th className="border border-white/30 px-1 sm:px-2 py-1 w-12 sm:w-16">
              <svg width="16" height="16" className="mx-auto" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </th>
          </tr>
        </thead>
        <tbody>
          {libraries.map(({ rank, name, github_url, stars, hasContextFile, contextFileName }) => (
            <tr key={name} className="hover:bg-white/10">
              <td className="border border-white/30 px-1 sm:px-2 py-1 text-xs sm:text-sm">{rank}</td>
              <td className="border border-white/30 px-1 sm:px-2 py-1">
                <div className="flex items-center justify-between">
                  <div className="flex flex-col flex-1 min-w-0">
                    <span className="font-medium text-white text-left text-xs sm:text-sm truncate">
                      {name}
                    </span>
                    {hasContextFile && (
                      <div className="flex items-center mt-1">
                        <div className="w-1.5 sm:w-2 h-1.5 sm:h-2 bg-green-400 rounded-full mr-1"></div>
                        <span className="text-xs text-green-200 hidden sm:inline">Context available</span>
                        <span className="text-xs text-green-200 sm:hidden">✓</span>
                      </div>
                    )}
                    {!hasContextFile && (
                      <div className="flex items-center mt-1">
                        <div className="w-1.5 sm:w-2 h-1.5 sm:h-2 bg-gray-400 rounded-full mr-1"></div>
                        <span className="text-xs text-gray-300 hidden sm:inline">No context</span>
                        <span className="text-xs text-gray-300 sm:hidden">✗</span>
                      </div>
                    )}
                  </div>
                  <button 
                    onClick={() => handleLibraryClick(name)}
                    className="ml-1 sm:ml-2 p-1 text-white hover:text-blue-200 transition-colors duration-200 hover:bg-white/10 rounded flex-shrink-0"
                    title="Open chat"
                  >
                    <svg width="16" height="16" className="sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                    </svg>
                  </button>
                </div>
              </td>
              <td className="border border-white/30 px-1 sm:px-2 py-1">
                <div className="flex justify-center">
                  <a
                    href={github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-white hover:text-blue-200 transition-colors duration-200 hover:bg-white/10 rounded p-1"
                    title="View on GitHub"
                  >
                    <svg width="16" height="16" className="sm:w-5 sm:h-5 md:w-6 md:h-6" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.30.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                  </a>
                </div>
              </td>
              <td className="border border-white/30 px-1 sm:px-2 py-1 text-xs sm:text-sm">
                <span className="hidden sm:inline">{stars}</span>
                <span className="sm:hidden">{stars > 1000 ? `${Math.round(stars/1000)}k` : stars}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
        </div>
    </div>
  );
}
