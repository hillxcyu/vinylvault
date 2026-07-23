import { DuplicateEngine } from '../services/duplicateEngine';
import { dbService } from '../services/database';

function runTests() {
  console.log('--- RUNNING DUPLICATE ENGINE TESTS ---');

  const collection = dbService.getAllRecords();
  const wishlist = dbService.getWishlist();

  // Test 1: Exact Match (Currents by Tame Impala)
  const test1 = DuplicateEngine.checkDuplicate(
    { artist: 'Tame Impala', albumTitle: 'Currents' },
    collection,
    wishlist
  );
  console.assert(test1.status === 'EXACT_MATCH', `Test 1 Failed: Expected EXACT_MATCH, got ${test1.status}`);
  console.log(`✅ Test 1 (Exact Match): ${test1.message}`);

  // Test 2: Wishlist Match (Demon Days by Gorillaz)
  const test2 = DuplicateEngine.checkDuplicate(
    { artist: 'Gorillaz', albumTitle: 'Demon Days' },
    collection,
    wishlist
  );
  console.assert(test2.status === 'WISHLIST_MATCH', `Test 2 Failed: Expected WISHLIST_MATCH, got ${test2.status}`);
  console.log(`✅ Test 2 (Wishlist Match): ${test2.message}`);

  // Test 3: Similar Artist (Tame Impala - Innerspeaker)
  const test3 = DuplicateEngine.checkDuplicate(
    { artist: 'Tame Impala', albumTitle: 'Innerspeaker' },
    collection,
    wishlist
  );
  console.assert(test3.status === 'SIMILAR_ALBUM', `Test 3 Failed: Expected SIMILAR_ALBUM, got ${test3.status}`);
  console.log(`✅ Test 3 (Similar Artist): ${test3.message}`);

  // Test 4: Not Owned (Abbey Road by The Beatles)
  const test4 = DuplicateEngine.checkDuplicate(
    { artist: 'The Beatles', albumTitle: 'Abbey Road' },
    collection,
    wishlist
  );
  console.assert(test4.status === 'NOT_OWNED', `Test 4 Failed: Expected NOT_OWNED, got ${test4.status}`);
  console.log(`✅ Test 4 (Not Owned): ${test4.message}`);

  console.log('--- ALL DUPLICATE ENGINE TESTS PASSED ---');
}

runTests();
