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
    if (pathname.includes('astronomy')) return 'astronomy';
    if (pathname.includes('finance')) return 'finance';
    return 'astronomy'; // fallback
  };
  
  const handleLibraryClick = (libraryName: string) => {
    const domain = getDomain();
    // Naviguer vers la page de chat avec la librairie pré-sélectionnée
    router.push(`/${domain}?library=${encodeURIComponent(libraryName)}`);
  };
  
  return (
    <div className="flex flex-col bg-white/10 backdrop-blur-sm rounded-xl shadow-lg p-4 text-sm w-[900px] max-h-[400px] overflow-y-auto mb-6 border border-white/20">
      <h2 className="text-lg font-semibold text-center text-white mb-3">
        {title}
      </h2>

      <table className="w-full table-fixed border-collapse border border-white/30 text-center text-white">
        <thead>
          <tr className="bg-white/20">
            <th className="border border-white/30 px-2 py-1 w-12">Rank</th>
            <th className="border border-white/30 px-2 py-1 w-32">Library</th>
            <th className="border border-white/30 px-2 py-1 w-40">GitHub</th>
            <th className="border border-white/30 px-2 py-1 w-16">Stars</th>
          </tr>
        </thead>
        <tbody>
          {libraries.map(({ rank, name, github_url, stars, hasContextFile, contextFileName }) => (
            <tr key={name} className="hover:bg-white/10">
              <td className="border border-white/30 px-2 py-1">{rank}</td>
              <td className="border border-white/30 px-2 py-1">
                <div className="flex flex-col">
                  <button 
                    onClick={() => handleLibraryClick(name)}
                    className="font-medium text-white hover:text-blue-200 hover:underline cursor-pointer text-left transition-colors duration-200"
                  >
                    {name}
                  </button>
                  {hasContextFile && (
                    <div className="flex items-center mt-1">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-1"></div>
                      <span className="text-xs text-green-200">Context available</span>
                    </div>
                  )}
                  {!hasContextFile && (
                    <div className="flex items-center mt-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full mr-1"></div>
                      <span className="text-xs text-gray-300">No context</span>
                    </div>
                  )}
                </div>
              </td>
              <td className="border border-white/30 px-2 py-1 break-all">
                <a
                  href={github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-200 underline hover:text-blue-100"
                >
                  {github_url}
                </a>
              </td>
              <td className="border border-white/30 px-2 py-1">{stars}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
