import libs from "./libraries.json";

export type LibraryEntry = {
  rank: number;
  name: string;
  stars: number;
};

export const astronomyLibs: LibraryEntry[] = libs.astronomy;
export const financeLibs: LibraryEntry[] = libs.finance;
