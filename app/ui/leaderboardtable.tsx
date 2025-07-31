"use client";

type LibraryEntry = {
  rank: number;
  name: string;
  github_url: string;
  stars: number;
};

type LeaderboardTableProps = {
  title: string;
  libraries: LibraryEntry[];
};

export default function LeaderboardTable({ title, libraries }: LeaderboardTableProps) {
  return (
    <div className="flex flex-col bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 text-sm w-[900px] max-h-[400px] overflow-y-auto mb-6">
      <h2 className="text-lg font-semibold text-center text-gray-900 dark:text-gray-100 mb-3">
        {title}
      </h2>

      <table className="w-full table-fixed border-collapse border border-gray-300 dark:border-gray-700 text-center text-gray-900 dark:text-gray-100">
        <thead>
          <tr className="bg-gray-100 dark:bg-gray-700">
            <th className="border border-gray-300 dark:border-gray-600 px-2 py-1 w-12">Rank</th>
            <th className="border border-gray-300 dark:border-gray-600 px-2 py-1 w-32">Library</th>
            <th className="border border-gray-300 dark:border-gray-600 px-2 py-1 w-40">GitHub</th>
            <th className="border border-gray-300 dark:border-gray-600 px-2 py-1 w-16">Stars</th>
          </tr>
        </thead>
        <tbody>
          {libraries.map(({ rank, name, github_url, stars }) => (
            <tr key={name} className="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td className="border border-gray-300 dark:border-gray-600 px-2 py-1">{rank}</td>
              <td className="border border-gray-300 dark:border-gray-600 px-2 py-1">{name}</td>
              <td className="border border-gray-300 dark:border-gray-600 px-2 py-1 break-all">
                <a
                  href={github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 dark:text-blue-400 underline"
                >
                  {github_url}
                </a>
              </td>
              <td className="border border-gray-300 dark:border-gray-600 px-2 py-1">{stars}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
