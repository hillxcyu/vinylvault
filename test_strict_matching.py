import requests
import urllib.parse
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def clean_term(text: str) -> str:
    text_no_cn = re.sub(r'[\u4e00-\u9fff]+', '', text)
    cleaned = re.sub(r'[^\w\s]', ' ', text_no_cn)
    return ' '.join(cleaned.split())

def is_relevant_match(requested_title: str, returned_title: str) -> bool:
    clean_req = clean_term(requested_title).lower()
    clean_ret = returned_title.lower()
    req_words = [w for w in clean_req.split() if len(w) > 2]

    # At least half of key words in requested title must be in returned title
    matches = sum(1 for w in req_words if w in clean_ret)
    return matches >= max(1, len(req_words) // 2)

print("Test Dvorak match:", is_relevant_match("Dvořák: Cello Concerto in B minor", "Dvořák: Cello Concerto No. 2"))
print("Test Irrelevant match:", is_relevant_match("Dvořák: Cello Concerto in B minor", "Brandenburgische Konzerte"))
