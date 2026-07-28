#!/bin/bash
set -e

echo "========== 🧪 RUNNING LOCAL DOCKER API INTEGRATION TESTS =========="

BASE_URL="${1:-http://localhost:8000}"

echo "[1/6] Testing GET /api/records..."
curl -s -f "$BASE_URL/api/records" > /dev/null
echo "  ✅ GET /api/records PASSED"

echo "[2/6] Testing POST /api/check-duplicate..."
curl -s -f -X POST "$BASE_URL/api/check-duplicate" \
  -H "Content-Type: application/json" \
  -d '{"artist": "Bach", "albumTitle": "French Suites"}' > /dev/null
echo "  ✅ POST /api/check-duplicate PASSED"

echo "[3/6] Testing POST /api/listening-guide..."
curl -s -f -X POST "$BASE_URL/api/listening-guide" \
  -H "Content-Type: application/json" \
  -d '{"artist": "Bach", "albumTitle": "French Suites"}' > /dev/null
echo "  ✅ POST /api/listening-guide PASSED"

echo "[4/6] Testing POST /api/fetch-release-assets..."
curl -s -f -X POST "$BASE_URL/api/fetch-release-assets" \
  -H "Content-Type: application/json" \
  -d '{"artist": "Bach", "title": "French Suites"}' > /dev/null
echo "  ✅ POST /api/fetch-release-assets PASSED"

echo "[5/6] Testing POST /api/chat-album..."
curl -s -f -X POST "$BASE_URL/api/chat-album" \
  -H "Content-Type: application/json" \
  -d '{"artist": "Bach", "albumTitle": "French Suites", "message": "Tell me about this pressing"}' > /dev/null
echo "  ✅ POST /api/chat-album PASSED"

echo "[6/6] Testing POST /api/records..."
curl -s -f -X POST "$BASE_URL/api/records" \
  -H "Content-Type: application/json" \
  -d '{"artist": "Test Artist", "title": "Test Album Integration", "genre": "Classical", "releaseYear": 2026}' > /dev/null
echo "  ✅ POST /api/records PASSED"

echo "=================================================================="
echo "🎉 ALL LOCAL INTEGRATION TESTS PASSED 100%! SAFE TO COMMIT & PUSH."
echo "=================================================================="
