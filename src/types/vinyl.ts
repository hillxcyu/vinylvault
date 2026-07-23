/**
 * Data models for Vinyl Vault App
 */

export interface VinylRecord {
  id: string;
  title: string;
  artist: string;
  releaseYear?: number;
  genre?: string;
  coverUrl?: string;
  catalogNumber?: string;
  createdAt: string;
  spinsCount: number;
  lastSpunAt?: string;
  pressings: VinylPressing[];
}

export interface VinylPressing {
  id: string;
  recordId: string;
  label?: string;
  country?: string;
  releaseYear?: number;
  formatDetails?: string; // e.g., "180g Black", "Gatefold", "Blue Vinyl", "Japanese OBI Pressing"
  catalogNumber?: string;
  discogsId?: number;
}

export interface SpinLog {
  id: string;
  recordId: string;
  spunAt: string;
  notes?: string;
}

export interface WishlistItem {
  id: string;
  title: string;
  artist: string;
  notes?: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  createdAt: string;
}

export interface GeminiScanResult {
  artist: string;
  albumTitle: string;
  releaseYear?: number;
  label?: string;
  catalogNumber?: string;
  confidenceScore: number;
  detectedTextLines: string[];
}

export type DuplicateStatus = 'EXACT_MATCH' | 'VARIANT_MATCH' | 'SIMILAR_ALBUM' | 'WISHLIST_MATCH' | 'NOT_OWNED';

export interface DuplicateCheckResult {
  status: DuplicateStatus;
  matchingRecord?: VinylRecord;
  matchingPressing?: VinylPressing;
  message: string;
}
