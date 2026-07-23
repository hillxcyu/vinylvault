import { VinylRecord, WishlistItem, DuplicateCheckResult, GeminiScanResult } from '../types/vinyl';

function normalizeString(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
    .trim();
}

/**
 * Duplicate Shield Engine
 * Evaluates scanned metadata or manual query against user's owned collection and wishlist.
 */
export class DuplicateEngine {
  public static checkDuplicate(
    query: { artist: string; albumTitle: string; catalogNumber?: string },
    collection: VinylRecord[],
    wishlist: WishlistItem[]
  ): DuplicateCheckResult {
    const normQueryArtist = normalizeString(query.artist);
    const normQueryTitle = normalizeString(query.albumTitle);
    const queryCatNo = query.catalogNumber ? normalizeString(query.catalogNumber) : null;

    if (!normQueryArtist && !normQueryTitle) {
      return {
        status: 'NOT_OWNED',
        message: 'Insufficient album information provided.',
      };
    }

    // 1. Check for Exact or Variant Matches in Collection
    for (const record of collection) {
      const normRecArtist = normalizeString(record.artist);
      const normRecTitle = normalizeString(record.title);

      const isArtistMatch = normQueryArtist && (normRecArtist.includes(normQueryArtist) || normQueryArtist.includes(normRecArtist));
      const isTitleMatch = normQueryTitle && (normRecTitle.includes(normQueryTitle) || normQueryTitle.includes(normRecTitle));

      if (isArtistMatch && isTitleMatch) {
        // Check if catalog number matches a specific pressing
        if (queryCatNo) {
          const matchingPressing = record.pressings.find(
            (p) => p.catalogNumber && normalizeString(p.catalogNumber) === queryCatNo
          );

          if (matchingPressing) {
            return {
              status: 'EXACT_MATCH',
              matchingRecord: record,
              matchingPressing,
              message: `ALREADY IN COLLECTION! You own this exact pressing (${matchingPressing.formatDetails || 'Standard'}).`,
            };
          }
        }

        // Title and Artist match, but catalog # is different or unspecified -> Variant Match / Owned Copy
        const primaryPressing = record.pressings[0];
        return {
          status: 'EXACT_MATCH',
          matchingRecord: record,
          matchingPressing: primaryPressing,
          message: `ALREADY IN COLLECTION! You own 1 copy of "${record.title}" by ${record.artist} (${primaryPressing?.formatDetails || 'Pressing info saved'}).`,
        };
      }
    }

    // 2. Check Wishlist Matches
    for (const item of wishlist) {
      const normWishArtist = normalizeString(item.artist);
      const normWishTitle = normalizeString(item.title);

      if (
        normQueryArtist &&
        normQueryTitle &&
        (normWishArtist.includes(normQueryArtist) || normQueryArtist.includes(normWishArtist)) &&
        (normWishTitle.includes(normQueryTitle) || normQueryTitle.includes(normWishTitle))
      ) {
        return {
          status: 'WISHLIST_MATCH',
          message: `ON YOUR WISHLIST! Priority: ${item.priority}. Notes: ${item.notes || 'No notes'}`,
        };
      }
    }

    // 3. Check for Same Artist (Similar Records Owned)
    const artistRecords = collection.filter((r) => {
      const normRecArtist = normalizeString(r.artist);
      return normQueryArtist && (normRecArtist.includes(normQueryArtist) || normQueryArtist.includes(normRecArtist));
    });

    if (artistRecords.length > 0) {
      const titles = artistRecords.map((r) => `"${r.title}"`).join(', ');
      return {
        status: 'SIMILAR_ALBUM',
        message: `NOT OWNED, but you own ${artistRecords.length} other record(s) by ${query.artist}: ${titles}.`,
      };
    }

    // 4. No Match - Safe to Buy!
    return {
      status: 'NOT_OWNED',
      message: `NOT IN COLLECTION. Safe to buy! No matching records found for "${query.albumTitle}".`,
    };
  }
}
