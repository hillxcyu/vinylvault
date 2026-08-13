import json
import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


INITIAL_RECORDS = [
    {
        "id": "rec-webarchive-001",
        "title": "Bach: French Suites BWV 812-817 (法国组曲 2LP)",
        "artist": "Michio Kobayashi (小林道夫)",
        "releaseYear": 1978,
        "genre": "Baroque / Classical",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_2.jpg",
        "catalogNumber": "IMP-2026-001",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-001",
                "recordId": "rec-webarchive-001",
                "label": "Japanese Pressing (2LP)",
                "country": "US / Japan",
                "releaseYear": 1978,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-001"
            }
        ]
    },
    {
        "id": "rec-webarchive-002",
        "title": "Sibelius & Bruch: Violin Concertos",
        "artist": "Isaac Stern (伊萨克·斯特恩)",
        "releaseYear": 1972,
        "genre": "Violin Concerto",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_3.jpg",
        "catalogNumber": "IMP-2026-002",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-002",
                "recordId": "rec-webarchive-002",
                "label": "RCA / CBS Masterworks",
                "country": "US / Japan",
                "releaseYear": 1972,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-002"
            }
        ]
    },
    {
        "id": "rec-webarchive-003",
        "title": "Beethoven: Symphony No. 7 in A major, Op. 92",
        "artist": "Otto Klemperer / Philharmonia Orchestra",
        "releaseYear": 1961,
        "genre": "Symphony",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_4.jpg",
        "catalogNumber": "IMP-2026-003",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-003",
                "recordId": "rec-webarchive-003",
                "label": "EMI / Angel Records (2LP)",
                "country": "US / Japan",
                "releaseYear": 1961,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-003"
            }
        ]
    },
    {
        "id": "rec-webarchive-004",
        "title": "Verdi: Opera Arias & Duets",
        "artist": "Plácido Domingo / Giuseppe Verdi",
        "releaseYear": 1974,
        "genre": "Opera / Vocal",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_5.jpg",
        "catalogNumber": "IMP-2026-004",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 12,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-004",
                "recordId": "rec-webarchive-004",
                "label": "RCA Red Seal Half-Speed Master",
                "country": "US / Japan",
                "releaseYear": 1974,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-004"
            }
        ]
    },
    {
        "id": "rec-webarchive-005",
        "title": "Baroque Recorder & Flute Works (Telemann / van Eyck)",
        "artist": "Frans Brüggen (弗朗斯·布鲁根)",
        "releaseYear": 1973,
        "genre": "Baroque Chamber",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_6.jpg",
        "catalogNumber": "IMP-2026-005",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 0,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-005",
                "recordId": "rec-webarchive-005",
                "label": "Telefunken / Japan Pressing",
                "country": "US / Japan",
                "releaseYear": 1973,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-005"
            }
        ]
    },
    {
        "id": "rec-webarchive-006",
        "title": "Strauss: Waltzes & Ballet Music",
        "artist": "Willi Boskovsky / Vienna Philharmonic",
        "releaseYear": 1966,
        "genre": "Classical Orchestral",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_7.jpg",
        "catalogNumber": "IMP-2026-006",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-006",
                "recordId": "rec-webarchive-006",
                "label": "Decca / Concert Classics",
                "country": "US / Japan",
                "releaseYear": 1966,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-006"
            }
        ]
    },
    {
        "id": "rec-webarchive-007",
        "title": "Beethoven & Liszt: Piano Sonatas",
        "artist": "Piano Masterworks",
        "releaseYear": 1970,
        "genre": "Piano Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_8.jpg",
        "catalogNumber": "IMP-2026-007",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-007",
                "recordId": "rec-webarchive-007",
                "label": "Audiophile 12\" LP",
                "country": "US / Japan",
                "releaseYear": 1970,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-007"
            }
        ]
    },
    {
        "id": "rec-webarchive-008",
        "title": "Beethoven: Piano Sonatas",
        "artist": "Friedrich Gulda (弗里德里希·古尔达)",
        "releaseYear": 1968,
        "genre": "Piano Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_9.jpg",
        "catalogNumber": "IMP-2026-008",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-008",
                "recordId": "rec-webarchive-008",
                "label": "Decca / Amadeo Pressing",
                "country": "US / Japan",
                "releaseYear": 1968,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-008"
            }
        ]
    },
    {
        "id": "rec-webarchive-009",
        "title": "Schubert: Piano Quintet 'Trout' & Beethoven Piano Trio",
        "artist": "Jan Panenka (扬·帕年卡)",
        "releaseYear": 1965,
        "genre": "Chamber Music",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_10.jpg",
        "catalogNumber": "IMP-2026-009",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 12,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-009",
                "recordId": "rec-webarchive-009",
                "label": "Supraphon Pressing",
                "country": "US / Japan",
                "releaseYear": 1965,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-009"
            }
        ]
    },
    {
        "id": "rec-webarchive-010",
        "title": "Brahms: Piano Concerto No. 1 in D minor",
        "artist": "Clifford Curzon & George Szell",
        "releaseYear": 1962,
        "genre": "Piano Concerto",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_11.jpg",
        "catalogNumber": "IMP-2026-010",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 0,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-010",
                "recordId": "rec-webarchive-010",
                "label": "Decca / London Records",
                "country": "US / Japan",
                "releaseYear": 1962,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-010"
            }
        ]
    },
    {
        "id": "rec-webarchive-011",
        "title": "Scriabin: Piano Sonatas & Preludes",
        "artist": "Lazar Berman (拉扎尔·贝尔曼)",
        "releaseYear": 1977,
        "genre": "Piano Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_12.jpg",
        "catalogNumber": "IMP-2026-011",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-011",
                "recordId": "rec-webarchive-011",
                "label": "Melodiya / Deutsche Grammophon",
                "country": "US / Japan",
                "releaseYear": 1977,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-011"
            }
        ]
    },
    {
        "id": "rec-webarchive-012",
        "title": "Beethoven: Piano Concerto No. 5 'Emperor'",
        "artist": "Claudio Arrau (克劳迪奥·阿劳)",
        "releaseYear": 1964,
        "genre": "Piano Concerto",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_13.jpg",
        "catalogNumber": "IMP-2026-012",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-012",
                "recordId": "rec-webarchive-012",
                "label": "Philips Pressing",
                "country": "US / Japan",
                "releaseYear": 1964,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-012"
            }
        ]
    },
    {
        "id": "rec-webarchive-013",
        "title": "Liszt: Concert Paraphrases on Verdi Operas",
        "artist": "Claudio Arrau (克劳迪奥·阿劳)",
        "releaseYear": 1971,
        "genre": "Piano Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_14.jpg",
        "catalogNumber": "IMP-2026-013",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-013",
                "recordId": "rec-webarchive-013",
                "label": "Philips 12\" LP",
                "country": "US / Japan",
                "releaseYear": 1971,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-013"
            }
        ]
    },
    {
        "id": "rec-webarchive-014",
        "title": "Sibelius: Symphony No. 2 in D major",
        "artist": "Colin Davis / London Symphony Orchestra",
        "releaseYear": 1976,
        "genre": "Symphony",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_15.jpg",
        "catalogNumber": "IMP-2026-014",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 12,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-014",
                "recordId": "rec-webarchive-014",
                "label": "Philips R-Release",
                "country": "US / Japan",
                "releaseYear": 1976,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-014"
            }
        ]
    },
    {
        "id": "rec-webarchive-015",
        "title": "Dvořák: Symphony No. 8 in G major",
        "artist": "István Kertész / London Symphony Orchestra",
        "releaseYear": 1963,
        "genre": "Symphony",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_16.jpg",
        "catalogNumber": "IMP-2026-015",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 0,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-015",
                "recordId": "rec-webarchive-015",
                "label": "Decca / London Japan Pressing",
                "country": "US / Japan",
                "releaseYear": 1963,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-015"
            }
        ]
    },
    {
        "id": "rec-webarchive-016",
        "title": "Berlioz: Overtures (Roman Carnival / Corsair)",
        "artist": "Jean Martinon / Orchestre National de ORTF",
        "releaseYear": 1959,
        "genre": "Classical Orchestral",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_17.jpg",
        "catalogNumber": "IMP-2026-016",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-016",
                "recordId": "rec-webarchive-016",
                "label": "London Japan Pressing",
                "country": "US / Japan",
                "releaseYear": 1959,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-016"
            }
        ]
    },
    {
        "id": "rec-webarchive-017",
        "title": "Schubert: String Quartets No. 13 'Rosamunde' & No. 14",
        "artist": "Alban Berg Quartett",
        "releaseYear": 1975,
        "genre": "Chamber Music",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_18.jpg",
        "catalogNumber": "IMP-2026-017",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-017",
                "recordId": "rec-webarchive-017",
                "label": "EMI Electrola",
                "country": "US / Japan",
                "releaseYear": 1975,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-017"
            }
        ]
    },
    {
        "id": "rec-webarchive-018",
        "title": "Smetana & Dvořák: Classical String Quartets",
        "artist": "Smetana Quartet (斯美塔那四重奏)",
        "releaseYear": 1974,
        "genre": "Chamber Music",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_19.jpg",
        "catalogNumber": "IMP-2026-018",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-018",
                "recordId": "rec-webarchive-018",
                "label": "Supraphon Japan Pressing",
                "country": "US / Japan",
                "releaseYear": 1974,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-018"
            }
        ]
    },
    {
        "id": "rec-webarchive-019",
        "title": "Mozart: Piano Sonatas Nos. 8 & 9 (K. 310 & K. 311)",
        "artist": "Glenn Gould (格伦·古尔德)",
        "releaseYear": 1969,
        "genre": "Piano Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_20.jpg",
        "catalogNumber": "IMP-2026-019",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 12,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-019",
                "recordId": "rec-webarchive-019",
                "label": "Columbia Masterworks R-Release",
                "country": "US / Japan",
                "releaseYear": 1969,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-019"
            }
        ]
    },
    {
        "id": "rec-webarchive-020",
        "title": "Mendelssohn: Violin Concerto in E minor",
        "artist": "Isaac Stern & Seiji Ozawa",
        "releaseYear": 1981,
        "genre": "Violin Concerto",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_21.jpg",
        "catalogNumber": "IMP-2026-020",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 0,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-020",
                "recordId": "rec-webarchive-020",
                "label": "CBS Masterworks R-Release",
                "country": "US / Japan",
                "releaseYear": 1981,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-020"
            }
        ]
    },
    {
        "id": "rec-webarchive-021",
        "title": "Liszt: Piano Sonata in B minor & Schumann Toccata",
        "artist": "Vladimir Horowitz",
        "releaseYear": 1977,
        "genre": "Piano Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_22.jpg",
        "catalogNumber": "IMP-2026-021",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-021",
                "recordId": "rec-webarchive-021",
                "label": "RCA Victor Red Seal",
                "country": "US / Japan",
                "releaseYear": 1977,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-021"
            }
        ]
    },
    {
        "id": "rec-webarchive-022",
        "title": "Grieg & Liszt: Piano Concertos",
        "artist": "Eugene Ormandy / Philadelphia Orchestra",
        "releaseYear": 1968,
        "genre": "Piano Concerto",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_23.jpg",
        "catalogNumber": "IMP-2026-022",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-022",
                "recordId": "rec-webarchive-022",
                "label": "Columbia Masterworks",
                "country": "US / Japan",
                "releaseYear": 1968,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-022"
            }
        ]
    },
    {
        "id": "rec-webarchive-023",
        "title": "Mahler: Symphony No. 1 'Titan'",
        "artist": "Leonard Bernstein / New York Philharmonic",
        "releaseYear": 1966,
        "genre": "Symphony",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_24.jpg",
        "catalogNumber": "IMP-2026-023",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-023",
                "recordId": "rec-webarchive-023",
                "label": "Columbia Masterworks",
                "country": "US / Japan",
                "releaseYear": 1966,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-023"
            }
        ]
    },
    {
        "id": "rec-webarchive-024",
        "title": "Bach: Orchestral Suites Nos. 2 & 3",
        "artist": "Lorin Maazel / Radio-Symphonie-Orchester Berlin",
        "releaseYear": 1966,
        "genre": "Baroque Orchestral",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_25.jpg",
        "catalogNumber": "IMP-2026-024",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 12,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-024",
                "recordId": "rec-webarchive-024",
                "label": "Philips 12\" LP",
                "country": "US / Japan",
                "releaseYear": 1966,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-024"
            }
        ]
    },
    {
        "id": "rec-webarchive-025",
        "title": "Beethoven: Piano Concerto No. 5 'Emperor' (Vienna Phil)",
        "artist": "Clifford Curzon & Hans Knappertsbusch",
        "releaseYear": 1957,
        "genre": "Piano Concerto",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_26.jpg",
        "catalogNumber": "IMP-2026-025",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 0,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-025",
                "recordId": "rec-webarchive-025",
                "label": "Decca Japan Pressing",
                "country": "US / Japan",
                "releaseYear": 1957,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-025"
            }
        ]
    },
    {
        "id": "rec-webarchive-026",
        "title": "Dvořák: Symphony No. 9 'From the New World'",
        "artist": "Eugene Ormandy / Philadelphia Orchestra",
        "releaseYear": 1977,
        "genre": "Symphony",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_27.jpg",
        "catalogNumber": "IMP-2026-026",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-026",
                "recordId": "rec-webarchive-026",
                "label": "RCA Japan Pressing",
                "country": "US / Japan",
                "releaseYear": 1977,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-026"
            }
        ]
    },
    {
        "id": "rec-webarchive-027",
        "title": "Jazz Crossover Hits Vol. 1",
        "artist": "Various Jazz Artists",
        "releaseYear": 1979,
        "genre": "Jazz / Crossover",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_28.jpg",
        "catalogNumber": "IMP-2026-027",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-027",
                "recordId": "rec-webarchive-027",
                "label": "12\" LP Compilation",
                "country": "US / Japan",
                "releaseYear": 1979,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-027"
            }
        ]
    },
    {
        "id": "rec-webarchive-028",
        "title": "52nd Street",
        "artist": "Billy Joel",
        "releaseYear": 1978,
        "genre": "Pop / Rock",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_29.jpg",
        "catalogNumber": "IMP-2026-028",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-028",
                "recordId": "rec-webarchive-028",
                "label": "Columbia Records",
                "country": "US / Japan",
                "releaseYear": 1978,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-028"
            }
        ]
    },
    {
        "id": "rec-webarchive-029",
        "title": "Glass Houses",
        "artist": "Billy Joel",
        "releaseYear": 1980,
        "genre": "Pop / Rock",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_30.jpg",
        "catalogNumber": "IMP-2026-029",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 12,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-029",
                "recordId": "rec-webarchive-029",
                "label": "Columbia Records",
                "country": "US / Japan",
                "releaseYear": 1980,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-029"
            }
        ]
    },
    {
        "id": "rec-webarchive-030",
        "title": "This Is The Ventures Vol. 2",
        "artist": "The Ventures (投机者乐队)",
        "releaseYear": 1966,
        "genre": "Surf Rock / Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_31.jpg",
        "catalogNumber": "IMP-2026-030",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 0,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-030",
                "recordId": "rec-webarchive-030",
                "label": "Liberty Records LP",
                "country": "US / Japan",
                "releaseYear": 1966,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-030"
            }
        ]
    },
    {
        "id": "rec-webarchive-031",
        "title": "Tchaikovsky & Mendelssohn: Violin Concertos",
        "artist": "Isaac Stern (伊萨克·斯特恩)",
        "releaseYear": 1969,
        "genre": "Violin Concerto",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_32.jpg",
        "catalogNumber": "IMP-2026-031",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-031",
                "recordId": "rec-webarchive-031",
                "label": "CBS Masterworks",
                "country": "US / Japan",
                "releaseYear": 1969,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-031"
            }
        ]
    },
    {
        "id": "rec-webarchive-032",
        "title": "Dvořák: Symphony No. 8 in G major",
        "artist": "John Barbirolli / Hallé Orchestra",
        "releaseYear": 1958,
        "genre": "Symphony",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_33.jpg",
        "catalogNumber": "IMP-2026-032",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-032",
                "recordId": "rec-webarchive-032",
                "label": "Pye Golden Guinea R-Release",
                "country": "US / Japan",
                "releaseYear": 1958,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-032"
            }
        ]
    },
    {
        "id": "rec-webarchive-033",
        "title": "Brahms: String Sextet No. 1 in B-flat major",
        "artist": "Amadeus Quartet",
        "releaseYear": 1968,
        "genre": "Chamber Music",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_34.jpg",
        "catalogNumber": "IMP-2026-033",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-033",
                "recordId": "rec-webarchive-033",
                "label": "Deutsche Grammophon",
                "country": "US / Japan",
                "releaseYear": 1968,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-033"
            }
        ]
    },
    {
        "id": "rec-webarchive-034",
        "title": "Tchaikovsky: Symphony No. 5 in E minor",
        "artist": "Lorin Maazel / Vienna Philharmonic",
        "releaseYear": 1963,
        "genre": "Symphony",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_35.jpg",
        "catalogNumber": "IMP-2026-034",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 12,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-034",
                "recordId": "rec-webarchive-034",
                "label": "Decca / London Pressing",
                "country": "US / Japan",
                "releaseYear": 1963,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-034"
            }
        ]
    },
    {
        "id": "rec-webarchive-035",
        "title": "Bach: Sonatas for Violin & Harpsichord",
        "artist": "Reinhold Barchet & Walter Frey",
        "releaseYear": 1962,
        "genre": "Baroque Chamber",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_36.jpg",
        "catalogNumber": "IMP-2026-035",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 0,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-035",
                "recordId": "rec-webarchive-035",
                "label": "Erato R-Release",
                "country": "US / Japan",
                "releaseYear": 1962,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-035"
            }
        ]
    },
    {
        "id": "rec-webarchive-036",
        "title": "Schumann: Fantasie in C major & Carnaval",
        "artist": "Arthur Rubinstein",
        "releaseYear": 1965,
        "genre": "Piano Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_37.jpg",
        "catalogNumber": "IMP-2026-036",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-036",
                "recordId": "rec-webarchive-036",
                "label": "RCA Red Seal R-Release",
                "country": "US / Japan",
                "releaseYear": 1965,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-036"
            }
        ]
    },
    {
        "id": "rec-webarchive-037",
        "title": "Haydn: Symphonies No. 103 'Drumroll' & No. 104 'London'",
        "artist": "Herbert von Karajan / Vienna Philharmonic",
        "releaseYear": 1964,
        "genre": "Symphony",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_38.jpg",
        "catalogNumber": "IMP-2026-037",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-037",
                "recordId": "rec-webarchive-037",
                "label": "Decca / London Japan Pressing",
                "country": "US / Japan",
                "releaseYear": 1964,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-037"
            }
        ]
    },
    {
        "id": "rec-webarchive-038",
        "title": "Dvořák: Symphony No. 9 'From the New World'",
        "artist": "James Levine / Chicago Symphony Orchestra",
        "releaseYear": 1981,
        "genre": "Symphony",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_39.jpg",
        "catalogNumber": "IMP-2026-038",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-038",
                "recordId": "rec-webarchive-038",
                "label": "RCA Red Seal R-Release",
                "country": "US / Japan",
                "releaseYear": 1981,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-038"
            }
        ]
    },
    {
        "id": "rec-webarchive-039",
        "title": "The Fifth Season (Jazz Guitar)",
        "artist": "Timothy Donahue",
        "releaseYear": 1987,
        "genre": "Jazz Guitar",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_40.jpg",
        "catalogNumber": "IMP-2026-039",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 12,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-039",
                "recordId": "rec-webarchive-039",
                "label": "Landmark Records 12\" LP",
                "country": "US / Japan",
                "releaseYear": 1987,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-039"
            }
        ]
    },
    {
        "id": "rec-webarchive-040",
        "title": "Liszt: Piano Concerto No. 1 & Hungarian Fantasy",
        "artist": "György Cziffra (齐夫拉)",
        "releaseYear": 1969,
        "genre": "Piano Concerto",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_41.jpg",
        "catalogNumber": "IMP-2026-040",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 0,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-040",
                "recordId": "rec-webarchive-040",
                "label": "EMI / Angel Records",
                "country": "US / Japan",
                "releaseYear": 1969,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-040"
            }
        ]
    },
    {
        "id": "rec-webarchive-041",
        "title": "Classical Symphonic & Chamber Assortment",
        "artist": "Classical Masterworks Anthology",
        "releaseYear": 1975,
        "genre": "Classical Compilation",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_42.jpg",
        "catalogNumber": "IMP-2026-041",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-041",
                "recordId": "rec-webarchive-041",
                "label": "Collector's 12\" LP",
                "country": "US / Japan",
                "releaseYear": 1975,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-041"
            }
        ]
    },
    {
        "id": "rec-webarchive-042",
        "title": "Schubert: Complete Impromptus Op. 90 & Op. 142",
        "artist": "Ingrid Haebler (英格丽德·海布勒)",
        "releaseYear": 1967,
        "genre": "Piano Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_43.jpg",
        "catalogNumber": "IMP-2026-042",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-042",
                "recordId": "rec-webarchive-042",
                "label": "Philips 12\" LP",
                "country": "US / Japan",
                "releaseYear": 1967,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-042"
            }
        ]
    },
    {
        "id": "rec-webarchive-043",
        "title": "Adios Diamantes Adios (Latin Romantics)",
        "artist": "Los Tres Diamantes",
        "releaseYear": 1965,
        "genre": "Latin / Bolero",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_44.jpg",
        "catalogNumber": "IMP-2026-043",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-043",
                "recordId": "rec-webarchive-043",
                "label": "RCA Victor LP",
                "country": "US / Japan",
                "releaseYear": 1965,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-043"
            }
        ]
    },
    {
        "id": "rec-webarchive-044",
        "title": "The Tom Jones Story",
        "artist": "Tom Jones",
        "releaseYear": 1971,
        "genre": "Pop / Vocal",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_45.jpg",
        "catalogNumber": "IMP-2026-044",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 12,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-044",
                "recordId": "rec-webarchive-044",
                "label": "Decca / Paragon 12\" LP",
                "country": "US / Japan",
                "releaseYear": 1971,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-044"
            }
        ]
    },
    {
        "id": "rec-webarchive-045",
        "title": "What Were Once Vices Are Now Habits",
        "artist": "The Doobie Brothers (杜比兄弟)",
        "releaseYear": 1974,
        "genre": "Classic Rock",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_46.jpg",
        "catalogNumber": "IMP-2026-045",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 0,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-045",
                "recordId": "rec-webarchive-045",
                "label": "Warner Bros. Records",
                "country": "US / Japan",
                "releaseYear": 1974,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-045"
            }
        ]
    },
    {
        "id": "rec-webarchive-046",
        "title": "International (Soul / Disco)",
        "artist": "The Three Degrees",
        "releaseYear": 1975,
        "genre": "Soul / Funk / Disco",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_47.jpg",
        "catalogNumber": "IMP-2026-046",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 3,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-046",
                "recordId": "rec-webarchive-046",
                "label": "Philadelphia International",
                "country": "US / Japan",
                "releaseYear": 1975,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-046"
            }
        ]
    },
    {
        "id": "rec-webarchive-047",
        "title": "How To Play Blues Guitar (Folk Blues Instruction)",
        "artist": "Acoustic Folk Blues Masters",
        "releaseYear": 1978,
        "genre": "Folk / Blues",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_48.jpg",
        "catalogNumber": "IMP-2026-047",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 6,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-047",
                "recordId": "rec-webarchive-047",
                "label": "Kicking Mule Records",
                "country": "US / Japan",
                "releaseYear": 1978,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-047"
            }
        ]
    },
    {
        "id": "rec-webarchive-048",
        "title": "Chopin: 14 Waltzes (14 首钢琴圆舞曲)",
        "artist": "Dinu Lipatti (迪努·李帕蒂)",
        "releaseYear": 1950,
        "genre": "Piano Instrumental",
        "coverUrl": "https://storage.googleapis.com/universal-trail-492014-n5-vinyl-vault-data/covers/shopping_cover_49.jpg",
        "catalogNumber": "IMP-2026-048",
        "createdAt": "2026-07-14T07:30:00Z",
        "spinsCount": 9,
        "lastSpunAt": "2026-07-14T07:00:00Z",
        "pressings": [
            {
                "id": "press-webarchive-048",
                "recordId": "rec-webarchive-048",
                "label": "Columbia Red Label Monophonic LP",
                "country": "US / Japan",
                "releaseYear": 1950,
                "formatDetails": "12\" Mastered LP",
                "catalogNumber": "IMP-2026-048"
            }
        ]
    }
]

INITIAL_WISHLIST = [
    {
        "id": "wish-1",
        "title": "Demon Days",
        "artist": "Gorillaz",
        "notes": "VMP Red vinyl pressing preferred",
        "priority": "HIGH",
        "createdAt": "2026-06-01T10:00:00Z"
    },
    {
        "id": "wish-2",
        "title": "Rumours",
        "artist": "Fleetwood Mac",
        "notes": "45 RPM Hoffman/Gray mastering",
        "priority": "MEDIUM",
        "createdAt": "2026-06-15T12:00:00Z"
    }
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data_store")
RECORDS_FILE = os.path.join(DATA_DIR, "records.json")
SPINS_FILE = os.path.join(DATA_DIR, "spins.json")
CHRONICLE_FILE = os.path.join(DATA_DIR, "chronicle.json")
NOW_SPINNING_FILE = os.path.join(DATA_DIR, "now_spinning.json")



class FirestoreManager:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "universal-trail-492014-n5")
        self.database_id = os.environ.get("FIRESTORE_DATABASE_ID") or os.environ.get("FIRESTORE_DATABASE", "vinylvault-hk")
        self.db = None
        self.last_error = None
        self._init_firestore()


    def _init_firestore(self):
        try:
            from google.cloud import firestore
            self.db = firestore.Client(project=self.project_id, database=self.database_id)
            print(f"GCP Firestore client successfully connected to project: {self.project_id}, database: {self.database_id}")
            self.last_error = None
        except Exception as e:
            err_str = str(e)
            print(f"GCP Firestore client init error for database {self.database_id}: {err_str}")
            self.db = None
            self.last_error = f"Client Init Error: {err_str}"

    def get_records(self, timeout: float = 3.0) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        if not self.db:
            return None, self.last_error or "Firestore client is not initialized"
        try:
            docs = self.db.collection("records").get(timeout=timeout)
            records = [d.to_dict() for d in docs if d.exists and d.to_dict()]
            print(f"Loaded {len(records)} records from GCP Firestore.")
            self.last_error = None
            return records, None
        except Exception as e:
            err_str = str(e)
            print(f"Firestore get_records warning/timeout: {err_str}")
            self.last_error = f"Fetch Error: {err_str}"
            return None, err_str








    def save_all_records_batch(self, records: List[Dict[str, Any]]) -> Tuple[bool, str]:
        if not self.db:
            return False, "Firestore client is not initialized (self.db is None)"
        try:
            batch = self.db.batch()
            for r in records:
                ref = self.db.collection("records").document(r["id"])
                batch.set(ref, r)
            batch.commit()
            print(f"Batch saved {len(records)} records to Firestore.")
            return True, "OK"
        except Exception as e:
            err_str = str(e)
            print(f"Firestore batch save error: {err_str}")
            return False, err_str

    def save_record(self, record_data: Dict[str, Any]) -> bool:
        if not self.db:
            return False
        try:
            rec_id = record_data.get("id")
            if rec_id:
                self.db.collection("records").document(rec_id).set(record_data)
                print(f"Saved record '{rec_id}' ({record_data.get('title')}) to Firestore.")
                return True
        except Exception as e:
            print(f"Firestore save_record error: {e}")
        return False

    def delete_record(self, record_id: str) -> bool:
        if not self.db:
            return False
        try:
            self.db.collection("records").document(record_id).delete()
            print(f"Deleted record '{record_id}' from Firestore.")
            return True
        except Exception as e:
            print(f"Firestore delete_record error: {e}")
        return False

    def get_spins(self) -> Optional[List[Dict[str, Any]]]:
        if not self.db:
            return None
        try:
            docs = self.db.collection("spins").stream()
            spins = [d.to_dict() for d in docs]
            if spins:
                return spins
        except Exception as e:
            print(f"Firestore get_spins error: {e}")
        return None

    def save_spin(self, spin_data: Dict[str, Any]) -> bool:
        if not self.db:
            return False
        try:
            spin_id = spin_data.get("id")
            if spin_id:
                self.db.collection("spins").document(spin_id).set(spin_data)
                return True
        except Exception as e:
            print(f"Firestore save_spin error: {e}")
        return False

    def get_chronicle(self) -> Optional[Dict[str, Any]]:
        if not self.db:
            return None
        try:
            doc = self.db.collection("metadata").document("chronicle").get(timeout=2.0)
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            print(f"Firestore get_chronicle warning/timeout (using local fallback): {e}")
        return None

    def save_chronicle(self, chronicle_data: Dict[str, Any]) -> bool:
        if not self.db:
            return False
        try:
            self.db.collection("metadata").document("chronicle").set(chronicle_data)
            return True
        except Exception as e:
            print(f"Firestore save_chronicle error: {e}")
        return False




    def get_listening_guide(self, key: str) -> Optional[Dict[str, Any]]:
        if not self.db:
            return None
        try:
            doc = self.db.collection("listening_guides").document(key).get()
            if doc.exists:
                print(f"Loaded listening guide '{key}' from Firestore.")
                return doc.to_dict().get("guide")
        except Exception as e:
            print(f"Firestore get_listening_guide error: {e}")
        return None

    def save_listening_guide(self, key: str, guide_data: Dict[str, Any]) -> bool:
        if not self.db:
            return False
        try:
            self.db.collection("listening_guides").document(key).set({"guide": guide_data})
            print(f"Saved listening guide '{key}' to Firestore.")
            return True
        except Exception as e:
            print(f"Firestore save_listening_guide error: {e}")
        return False

    def get_release_assets(self, key: str) -> Optional[List[Dict[str, Any]]]:
        if not self.db:
            return None
        try:
            doc = self.db.collection("release_assets").document(key).get()
            if doc.exists:
                print(f"Loaded release assets '{key}' from Firestore.")
                return doc.to_dict().get("assets")
        except Exception as e:
            print(f"Firestore get_release_assets error: {e}")
        return None

    def save_release_assets(self, key: str, assets: List[Dict[str, Any]]) -> bool:
        if not self.db:
            return False
        try:
            self.db.collection("release_assets").document(key).set({"assets": assets})
            print(f"Saved release assets '{key}' to Firestore.")
            return True
        except Exception as e:
            print(f"Firestore save_release_assets error: {e}")
        return False

class VinylDatabase:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.firestore = FirestoreManager()
        self._has_synced_firestore = False

        self.wishlist = list(INITIAL_WISHLIST)
        
        # Load local storage first for instant server startup (< 0.1s)
        self.records = self._load_records()
        self.spins_log = self._load_spins()
        self.chronicle = self._load_chronicle()
        self.now_spinning = None  # In-memory only state (resets to Standby on cold boot)

        # Non-blocking background Firestore sync
        if self.firestore.db:
            import threading
            threading.Thread(target=self.sync_firestore_on_startup, daemon=True).start()

    def ensure_firestore_synced(self):
        """Lazy-syncs Firestore in a non-blocking background thread when /api/records is called."""
        if self._has_synced_firestore:
            return
        self._has_synced_firestore = True
        import threading
        threading.Thread(target=self.sync_firestore_on_startup, daemon=True).start()

    def sync_firestore_on_startup(self):
        """Non-blocking background sync called after web server binds to PORT."""
        if not self.firestore.db:
            print("Firestore client unavailable; skipping startup sync.")
            return

        try:
            fs_recs, err = self.firestore.get_records()
            if fs_recs is None:
                print(f"Firestore get_records returned None ({err}); preserving existing records.")
                return

            if len(fs_recs) > 0:
                print(f"Firestore active with {len(fs_recs)} records.")
                # Merge local-only records that were saved locally but missing from Firestore
                fs_ids = {r.get("id") for r in fs_recs if r.get("id")}
                missing_local = [r for r in self.records if r.get("id") and r.get("id") not in fs_ids]

                if missing_local:
                    print(f"Found {len(missing_local)} local records missing from Firestore; syncing to cloud...")
                    for loc_rec in missing_local:
                        try:
                            self.firestore.save_record(loc_rec)
                        except Exception as sync_err:
                            print(f"Failed to sync local record '{loc_rec.get('title')}' to Firestore: {sync_err}")

                self.records = fs_recs
                print(f"Startup sync complete: {len(self.records)} records active from Firestore.")
            else:
                print("Firestore collection returned 0 records. Preserving local disk records.")
                if not self.records:
                    self.records = []
                    self.save_records()

        except Exception as e:
            print(f"Background Firestore sync warning: {e}")



    def _load_records(self) -> List[Dict[str, Any]]:
        loaded = []
        if os.path.exists(RECORDS_FILE):
            try:
                with open(RECORDS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        loaded = data
            except Exception as e:
                print(f"Error reading records.json: {e}")

        # No automatic reseeding from INITIAL_RECORDS
        filtered = [r for r in loaded if r.get("id") != "rec-001" and r.get("title") != "In Rainbows"]
        
        # Deduplicate records by normalized (title, artist)
        seen_keys = set()
        deduped = []
        for r in filtered:
            key = ((r.get("title") or "").strip().lower(), (r.get("artist") or "").strip().lower())
            if key not in seen_keys:
                seen_keys.add(key)
                deduped.append(r)

        if len(deduped) != len(loaded):
            self._save_json(RECORDS_FILE, deduped)
        return deduped

    def _load_spins(self) -> List[Dict[str, Any]]:
        if os.path.exists(SPINS_FILE):
            try:
                with open(SPINS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        return data
            except Exception as e:
                print(f"Error reading spins.json: {e}")
        return []

    def export_backup(self) -> Dict[str, Any]:
        return {
            "version": "1.0",
            "exportedAt": datetime.utcnow().isoformat() + "Z",
            "records": self.records,
            "spins_log": self.spins_log,
            "wishlist": self.wishlist
        }

    def restore_backup(self, backup_data: Dict[str, Any]) -> Dict[str, Any]:
        records = backup_data.get("records", [])
        spins = backup_data.get("spins_log", [])
        wishlist = backup_data.get("wishlist", [])

        if not isinstance(records, list):
            records = []

        self.records = records
        self.spins_log = spins if isinstance(spins, list) else []
        self.wishlist = wishlist if isinstance(wishlist, list) else []

        self.save_records()
        self.save_spins()

        if self.firestore.db and self.records:
            self.firestore.save_all_records_batch(self.records)

        return {
            "restoredRecordsCount": len(self.records),
            "restoredSpinsCount": len(self.spins_log)
        }

    def restore_sample_data(self) -> Dict[str, Any]:
        sample_backup = {
            "version": "1.0",
            "records": INITIAL_RECORDS,
            "spins_log": [
                {"id": "spin-1", "recordId": "rec-webarchive-001", "spunAt": "2026-07-14T07:00:00Z", "notes": "Bach French Suites - Excellent pressing"}
            ],
            "wishlist": list(INITIAL_WISHLIST)
        }
        return self.restore_backup(sample_backup)

    def _save_json(self, filepath: str, data: Any):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing {filepath}: {e}")

    def _load_chronicle(self) -> Optional[Dict[str, Any]]:
        if os.path.exists(CHRONICLE_FILE):
            try:
                with open(CHRONICLE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        return data
            except Exception as e:
                print(f"Error reading chronicle.json: {e}")
        return None

    def save_chronicle(self, chronicle_data: Dict[str, Any]):
        self.chronicle = chronicle_data
        self._save_json(CHRONICLE_FILE, chronicle_data)
        if self.firestore.db:
            self.firestore.save_chronicle(chronicle_data)

    def get_chronicle(self) -> Optional[Dict[str, Any]]:
        if self.firestore.db:
            fs_chronicle = self.firestore.get_chronicle()
            if fs_chronicle and isinstance(fs_chronicle, dict) and fs_chronicle.get("totalClassicalRecords", 0) > 0:
                self.chronicle = fs_chronicle
                return fs_chronicle
        if not hasattr(self, "chronicle") or self.chronicle is None:
            self.chronicle = self._load_chronicle()
        return self.chronicle

    def clear_chronicle(self):
        self.chronicle = None
        self._save_json(CHRONICLE_FILE, {})
        if self.firestore.db:
            try:
                self.firestore.db.collection("metadata").document("chronicle").delete()
            except Exception as e:
                print(f"Firestore clear_chronicle error: {e}")


    def get_now_spinning(self) -> Optional[Dict[str, Any]]:
        return self.now_spinning

    def set_now_spinning(self, record_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        now_str = datetime.utcnow().isoformat() + "Z"
        if record_data:
            spinning_payload = {
                "recordId": record_data.get("id"),
                "startedAt": now_str,
                "record": record_data
            }
            self.now_spinning = spinning_payload
            return spinning_payload
        else:
            self.now_spinning = None
            return None




    def save_records(self):
        self._rebuild_record_map()
        self._save_json(RECORDS_FILE, self.records)


    def save_spins(self):
        self._save_json(SPINS_FILE, self.spins_log)

    def get_all_records(self, sync_if_needed: bool = False) -> List[Dict[str, Any]]:
        if sync_if_needed:
            if not self.firestore or not self.firestore.db:
                if self.firestore:
                    self.firestore._init_firestore()

            if self.firestore and self.firestore.db:
                try:
                    fs_recs, err = self.firestore.get_records()
                    if fs_recs is not None and len(fs_recs) > 0:
                        self.records = fs_recs
                        self._save_json(RECORDS_FILE, fs_recs)
                        self._rebuild_record_map()
                except Exception as e:
                    print(f"Error fetching direct records from Firestore: {e}")
        return self.records

    def get_all_records_with_status(self, sync_if_needed: bool = True) -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
        fs_connected = True
        fs_error = None

        if sync_if_needed:
            if not self.firestore or not self.firestore.db:
                if self.firestore:
                    self.firestore._init_firestore()

            if self.firestore and self.firestore.db:
                try:
                    fs_recs, err = self.firestore.get_records()
                    if fs_recs is not None:
                        self.records = fs_recs
                        self._save_json(RECORDS_FILE, fs_recs)
                        self._rebuild_record_map()
                    else:
                        fs_connected = False
                        fs_error = err or (self.firestore.last_error if self.firestore else "Firestore query returned None")
                except Exception as e:
                    fs_connected = False
                    fs_error = str(e)
            else:
                fs_connected = False
                fs_error = self.firestore.last_error if self.firestore else "Firestore client not initialized"

        return self.records, fs_connected, fs_error



    def _rebuild_record_map(self):
        self._record_map = {r["id"]: r for r in self.records if r and isinstance(r, dict) and r.get("id")}

    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        if hasattr(self, "_record_map") and self._record_map:
            return self._record_map.get(record_id)
        for r in self.records:
            if r.get("id") == record_id:
                return r
        return None


    def add_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        # Check for existing duplicate record by normalized title and artist
        norm_title = (record_data.get("title") or "").strip().lower()
        norm_artist = (record_data.get("artist") or "").strip().lower()

        for existing in self.records:
            e_title = (existing.get("title") or "").strip().lower()
            e_artist = (existing.get("artist") or "").strip().lower()
            if norm_title == e_title and norm_artist == e_artist:
                print(f"Prevented adding duplicate record for '{record_data.get('title')}'")
                return existing

        new_id = f"rec-user-{uuid.uuid4().hex[:8]}"

        record_data["id"] = new_id
        record_data["createdAt"] = datetime.utcnow().isoformat() + "Z"
        record_data["spinsCount"] = 0
        if "pressings" not in record_data or not record_data["pressings"]:
            record_data["pressings"] = [{
                "id": f"press-{new_id}",
                "recordId": new_id,
                "label": record_data.get("label", "Standard Release"),
                "formatDetails": "Standard Vinyl Pressing",
                "catalogNumber": record_data.get("catalogNumber", "")
            }]
        self.records.insert(0, record_data)
        self.save_records()

        fs_saved = False
        try:
            if self.firestore.db:
                fs_saved = self.firestore.save_record(record_data)
                print(f"Saved new record '{new_id}' ({record_data.get('title')}) to Firestore: {fs_saved}")
        except Exception as e:
            print(f"Error saving new record '{new_id}' to Firestore: {e}")

        self.clear_chronicle()
        return record_data


    def update_record(self, record_data: Any, record_dict_fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Updates an existing record in memory and persists to Firestore.
        Flexible signature supports both update_record(rec_dict) and update_record(rec_id, rec_dict).
        """
        if isinstance(record_data, str) and record_dict_fallback is not None:
            record_data = record_dict_fallback
        elif not isinstance(record_data, dict) and isinstance(record_dict_fallback, dict):
            record_data = record_dict_fallback

        rec_id = record_data.get("id") if isinstance(record_data, dict) else None
        if not rec_id:
            return record_data if isinstance(record_data, dict) else {}

        for i, r in enumerate(self.records):
            if r.get("id") == rec_id:
                self.records[i] = record_data
                break
        else:
            self.records.insert(0, record_data)

        self.save_records()


        try:
            if self.firestore.db:
                success = self.firestore.save_record(record_data)
                print(f"Persisted record update '{rec_id}' to Firestore: {success}")
        except Exception as e:
            print(f"Error persisting record update '{rec_id}' to Firestore: {e}")

        self.clear_chronicle()
        return record_data


    def log_spin(self, record_id: str, notes: str = "") -> Dict[str, Any]:
        rec = self.get_record_by_id(record_id)
        now_str = datetime.utcnow().isoformat() + "Z"
        if rec:
            rec["spinsCount"] += 1
            rec["lastSpunAt"] = now_str
            self.save_records()
            self.firestore.save_record(rec)
        spin_entry = {
            "id": f"spin-{len(self.spins_log) + 1}",
            "recordId": record_id,
            "spunAt": now_str,
            "notes": notes
        }
        self.spins_log.insert(0, spin_entry)
        self.save_spins()
        self.firestore.save_spin(spin_entry)
        return spin_entry

    def get_wishlist(self) -> List[Dict[str, Any]]:
        return self.wishlist

    def get_spins_log(self) -> List[Dict[str, Any]]:
        return self.spins_log

    def delete_record(self, record_id: str) -> bool:
        initial_len = len(self.records)
        self.records = [r for r in self.records if r["id"] != record_id]
        if len(self.records) < initial_len:
            self.save_records()
            self.firestore.delete_record(record_id)
            return True
        return False

db = VinylDatabase()
