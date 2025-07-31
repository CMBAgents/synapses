import libs from "./libraries.json";

export type LibraryEntry = {
  rank: number;
  name: string;
  github_url: string;
  stars: number;
};

export const astronomyLibs: LibraryEntry[] = libs.astronomy;
export const financeLibs: LibraryEntry[] = libs.finance;
