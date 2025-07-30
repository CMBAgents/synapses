"use client";

type LibraryEntry = {
  rank: number;
  name: string;
  stars: number;
};

type LeaderboardTableProps = {
  title: string;
  libraries: LibraryEntry[];
};

export default function LeaderboardTable({ title, libraries }: LeaderboardTableProps) {
  return (
    <div className="flex flex-col w-72 bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 overflow-auto text-sm">
      <h2 className="text-lg font-semibold text-center text-gray-900 dark:text-gray-100 mb-3">
        {title}
      </h2>
      <table className="w-full table-fixed border-collapse border border-gray-300 dark:border-gray-700 text-center text-gray-900 dark:text-gray-100">
        <thead>
          <tr className="bg-gray-100 dark:bg-gray-700">
            <th className="border border-gray-300 dark:border-gray-600 px-2 py-1">Rank</th>
            <th className="border border-gray-300 dark:border-gray-600 px-2 py-1">Library</th>
            <th className="border border-gray-300 dark:border-gray-600 px-2 py-1">Stars</th>
          </tr>
        </thead>
        <tbody>
          {libraries.map(({ rank, name, stars }) => (
            <tr key={name} className="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td className="border border-gray-300 dark:border-gray-600 px-2 py-1">{rank}</td>
              <td className="border border-gray-300 dark:border-gray-600 px-2 py-1 truncate">{name}</td>
              <td className="border border-gray-300 dark:border-gray-600 px-2 py-1">{stars}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
