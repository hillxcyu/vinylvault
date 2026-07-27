import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

INITIAL_RECORDS = [
    {
        "id": "rec-webarchive-001",
        "title": "Bach: French Suites BWV 812-817 (法国组曲 2LP)",
        "artist": "Michio Kobayashi (小林道夫)",
        "releaseYear": 1978,
        "genre": "Baroque / Classical",
        "coverUrl": "/static/extracted_covers/shopping_cover_2.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_3.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_4.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_5.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_6.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_7.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_8.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_9.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_10.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_11.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_12.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_13.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_14.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_15.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_16.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_17.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_18.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_19.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_20.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_21.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_22.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_23.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_24.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_25.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_26.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_27.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_28.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_29.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_30.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_31.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_32.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_33.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_34.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_35.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_36.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_37.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_38.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_39.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_40.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_41.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_42.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_43.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_44.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_45.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_46.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_47.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_48.jpg",
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
        "coverUrl": "/static/extracted_covers/shopping_cover_49.jpg",
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

class VinylDatabase:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.wishlist = list(INITIAL_WISHLIST)
        self.records = self._load_records()
        self.spins_log = self._load_spins()
        self.chronicle = self._load_chronicle()

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

        if not loaded:
            loaded = list(INITIAL_RECORDS)

        filtered = [r for r in loaded if r.get("id") != "rec-001" and r.get("title") != "In Rainbows"]
        if len(filtered) != len(loaded):
            self._save_json(RECORDS_FILE, filtered)
        return filtered

    def _load_spins(self) -> List[Dict[str, Any]]:
        if os.path.exists(SPINS_FILE):
            try:
                with open(SPINS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data:
                        return data
            except Exception as e:
                print(f"Error reading spins.json: {e}")
        initial_spins = [
            {"id": "spin-1", "recordId": "rec-webarchive-001", "spunAt": "2026-07-14T07:00:00Z", "notes": "Bach French Suites - Excellent pressing"},
            {"id": "spin-2", "recordId": "rec-webarchive-009", "spunAt": "2026-07-14T06:30:00Z", "notes": "Dvořák Cello Concerto performance"}
        ]
        self._save_json(SPINS_FILE, initial_spins)
        return initial_spins

    def _save_json(self, filepath: str, data: Any):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing to {filepath}: {e}")

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

    def get_chronicle(self) -> Optional[Dict[str, Any]]:
        if not hasattr(self, "chronicle") or self.chronicle is None:
            self.chronicle = self._load_chronicle()
        return self.chronicle

    def save_records(self):
        self._save_json(RECORDS_FILE, self.records)

    def save_spins(self):
        self._save_json(SPINS_FILE, self.spins_log)

    def get_all_records(self) -> List[Dict[str, Any]]:
        return self.records

    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        for r in self.records:
            if r["id"] == record_id:
                return r
        return None

    def add_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        new_id = f"rec-user-{len(self.records) + 100}"
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
        return record_data

    def log_spin(self, record_id: str, notes: str = "") -> Dict[str, Any]:
        rec = self.get_record_by_id(record_id)
        now_str = datetime.utcnow().isoformat() + "Z"
        if rec:
            rec["spinsCount"] += 1
            rec["lastSpunAt"] = now_str
            self.save_records()
        spin_entry = {
            "id": f"spin-{len(self.spins_log) + 1}",
            "recordId": record_id,
            "spunAt": now_str,
            "notes": notes
        }
        self.spins_log.insert(0, spin_entry)
        self.save_spins()
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
            return True
        return False

db = VinylDatabase()
