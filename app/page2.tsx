"use client";

import { useRouter } from "next/navigation";

export default function Page2() {
  const router = useRouter();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-white">
      <h1 className="text-3xl font-bold mb-6">Page 2</h1>

      <button
        onClick={() => router.push("/")}
        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-full shadow-md transition"
      >
        Retour à la page d’accueil
      </button>
    </div>
  );
}
