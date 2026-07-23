import { VinylRecord, SpinLog, WishlistItem } from '../types/vinyl';

// Seed initial collection records
const INITIAL_RECORDS: VinylRecord[] = [
  {
    id: 'rec-1',
    title: 'Currents',
    artist: 'Tame Impala',
    releaseYear: 2015,
    genre: 'Psychedelic Rock',
    coverUrl: 'https://upload.wikimedia.org/wikipedia/en/9/9b/Tame_Impala_-_Currents.png',
    catalogNumber: '4730677',
    createdAt: '2024-01-15T10:00:00Z',
    spinsCount: 14,
    lastSpunAt: '2026-07-12T20:30:00Z',
    pressings: [
      {
        id: 'press-1',
        recordId: 'rec-1',
        label: 'Modular Recordings / Interscope',
        country: 'US',
        releaseYear: 2015,
        formatDetails: 'Standard 2xLP Black Vinyl',
        catalogNumber: '4730677',
        discogsId: 7240212,
      },
    ],
  },
  {
    id: 'rec-2',
    title: 'OK Computer',
    artist: 'Radiohead',
    releaseYear: 1997,
    genre: 'Alternative Rock',
    coverUrl: 'https://upload.wikimedia.org/wikipedia/en/a/a1/Radiohead.okcomputer.albumart.jpg',
    catalogNumber: 'NODATA 02',
    createdAt: '2024-02-10T14:20:00Z',
    spinsCount: 22,
    lastSpunAt: '2026-07-10T18:00:00Z',
    pressings: [
      {
        id: 'press-2',
        recordId: 'rec-2',
        label: 'Parlophone',
        country: 'UK',
        releaseYear: 1997,
        formatDetails: 'Original UK 2xLP Gatefold',
        catalogNumber: 'NODATA 02',
        discogsId: 105260,
      },
    ],
  },
  {
    id: 'rec-3',
    title: 'Random Access Memories',
    artist: 'Daft Punk',
    releaseYear: 2013,
    genre: 'Electronic / Disco',
    coverUrl: 'https://upload.wikimedia.org/wikipedia/en/a/a7/Random_Access_Memories.jpg',
    catalogNumber: '88883716861',
    createdAt: '2024-03-01T09:00:00Z',
    spinsCount: 18,
    lastSpunAt: '2026-07-08T22:15:00Z',
    pressings: [
      {
        id: 'press-3',
        recordId: 'rec-3',
        label: 'Columbia Records',
        country: 'US',
        releaseYear: 2013,
        formatDetails: '180g Gatefold 2xLP',
        catalogNumber: '88883716861',
        discogsId: 4570505,
      },
    ],
  },
  {
    id: 'rec-4',
    title: 'The Slow Rush',
    artist: 'Tame Impala',
    releaseYear: 2020,
    genre: 'Psychedelic Pop',
    coverUrl: 'https://upload.wikimedia.org/wikipedia/en/9/97/Tame_Impala_-_The_Slow_Rush.png',
    catalogNumber: '00602508273766',
    createdAt: '2024-05-12T11:45:00Z',
    spinsCount: 8,
    lastSpunAt: '2026-06-20T19:00:00Z',
    pressings: [
      {
        id: 'press-4',
        recordId: 'rec-4',
        label: 'Interscope Records',
        country: 'US',
        releaseYear: 2020,
        formatDetails: 'Limited Edition Red & Yellow Splatter 2xLP',
        catalogNumber: '00602508273766',
        discogsId: 14786377,
      },
    ],
  },
  {
    id: 'rec-5',
    title: 'Madvillainy',
    artist: 'Madvillain (MF DOOM & Madlib)',
    releaseYear: 2004,
    genre: 'Hip Hop',
    coverUrl: 'https://upload.wikimedia.org/wikipedia/en/5/5e/Madvillainy_cover.png',
    catalogNumber: 'STH2065',
    createdAt: '2024-06-01T16:00:00Z',
    spinsCount: 19,
    lastSpunAt: '2026-07-01T21:00:00Z',
    pressings: [
      {
        id: 'press-5',
        recordId: 'rec-5',
        label: 'Stones Throw Records',
        country: 'US',
        releaseYear: 2004,
        formatDetails: 'Standard Black Vinyl',
        catalogNumber: 'STH2065',
        discogsId: 247075,
      },
    ],
  },
];

const INITIAL_WISHLIST: WishlistItem[] = [
  {
    id: 'wish-1',
    title: 'Demon Days',
    artist: 'Gorillaz',
    notes: 'Looking for the VMP Red vinyl pressing',
    priority: 'HIGH',
    createdAt: '2026-06-01T10:00:00Z',
  },
  {
    id: 'wish-2',
    title: 'Rumours',
    artist: 'Fleetwood Mac',
    notes: 'Prefers 45 RPM Hoffman/Gray mastering',
    priority: 'MEDIUM',
    createdAt: '2026-06-15T12:00:00Z',
  },
];

class VinylDatabaseService {
  private records: VinylRecord[] = [...INITIAL_RECORDS];
  private wishlist: WishlistItem[] = [...INITIAL_WISHLIST];
  private spinsLog: SpinLog[] = [
    { id: 'spin-1', recordId: 'rec-1', spunAt: '2026-07-12T20:30:00Z', notes: 'Late night chill spin' },
    { id: 'spin-2', recordId: 'rec-2', spunAt: '2026-07-10T18:00:00Z', notes: 'Side B tracks are incredible' },
  ];

  public getAllRecords(): VinylRecord[] {
    return [...this.records];
  }

  public getRecordById(id: string): VinylRecord | undefined {
    return this.records.find((r) => r.id === id);
  }

  public addRecord(recordData: Omit<VinylRecord, 'id' | 'createdAt' | 'spinsCount'>): VinylRecord {
    const newRecord: VinylRecord = {
      ...recordData,
      id: `rec-${Date.now()}`,
      createdAt: new Date().toISOString(),
      spinsCount: 0,
    };
    this.records.unshift(newRecord);
    return newRecord;
  }

  public logSpin(recordId: string, notes?: string): SpinLog {
    const record = this.getRecordById(recordId);
    if (record) {
      record.spinsCount += 1;
      record.lastSpunAt = new Date().toISOString();
    }
    const newSpin: SpinLog = {
      id: `spin-${Date.now()}`,
      recordId,
      spunAt: new Date().toISOString(),
      notes,
    };
    this.spinsLog.unshift(newSpin);
    return newSpin;
  }

  public getWishlist(): WishlistItem[] {
    return [...this.wishlist];
  }

  public getSpinsLog(): SpinLog[] {
    return [...this.spinsLog];
  }
}

export const dbService = new VinylDatabaseService();
