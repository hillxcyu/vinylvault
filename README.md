# VinylVault — Multimodal Visual Cataloging & Media Asset Intelligence Studio

**VinylVault** is a reusable reference application and live demonstration of **Multimodal Visual Cataloging, Perspective Deskew, and AI Media Asset Intelligence** built on **Vertex AI (Gemini 3.6 Flash & Gemini 3.1 Flash TTS)**, **Cloud Firestore**, **Cloud Storage**, and **Cloud Run**.

While showcased through a physical vinyl record archive, the end-to-end architecture serves as a blueprint for **media archives, retail collectibles, luxury/authenticated goods, and physical inventory digitization**—turning skewed, real-world smartphone photos into structured, deduplicated, enriched catalog records in seconds.

## Key Capabilities

* **Multimodal Vision & Perspective Deskew (`deskew_service.py`, `gemini_service.py`):** Automatically detects 4-corner item boundaries in angled smartphone photos using Gemini Vision polygon segmentation (with OpenCV contour fallback), applies perspective homography warping, and generates clean WebP thumbnails.
* **Real-Time Anti-Duplicate Detection (`main.py`, `database.py`):** Evaluates newly scanned items against existing Firestore catalog entries using multimodal + metadata matching before ingestion, preventing duplicate inventory or purchases.
* **Catalog Enrichment & Conversational Intelligence (`discogs_service.py`, `classical_service.py`, `gemini_service.py`):** Enriches scanned records with external release metadata (Discogs, iTunes, classical opus/movement taxonomies), generates deep listening/inspection guides, and powers a streaming multimodal chat assistant.
* **Multilingual Audio Pronunciation (`gemini_service.py`):** Synthesizes clear spoken pronunciations for foreign-language artist names, composers, and catalog titles via Gemini Flash TTS.
* **Enterprise-Ready Serverless Architecture (`click-to-deploy/`):** Deployed on Cloud Run (`INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER`) behind an External HTTPS Application Load Balancer with Identity-Aware Proxy (IAP), least-privilege runtime IAM, Firestore, and Cloud Storage.

## Architecture Overview

```text
User Browser ──▶ External HTTPS ALB + IAP ──▶ Cloud Run (FastAPI + Jinja2/JS)
                                                  │
        ┌─────────────────────────────────────────┼─────────────────────────────────────────┐
        ▼                                         ▼                                         ▼
Vertex AI (global)                       Cloud Firestore                           Cloud Storage
• gemini-3.6-flash (Vision/Chat)         • Catalog Records & Spins                 • Deskewed WebP Covers
• gemini-3.1-flash-tts-preview (Audio)   • Chronicle & Listening Guides            • Original Uploads
```

## Quick Start

### Option 1: Click-to-Deploy (Terraform)

The `click-to-deploy/` directory provides C2D-compliant Terraform for provisioning APIs, Firestore, Cloud Storage, Artifact Registry, Cloud Build / Cloud Run, External HTTPS Load Balancer, IAP, and least-privilege IAM:

```bash
cd click-to-deploy
terraform init
terraform apply \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="data_location=us-central1"
```

See [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for complete setup, access, walkthrough, and seller pitch instructions.

### Option 2: Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r click-to-deploy/requirements.txt

export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="global"
export FIRESTORE_DATABASE_ID="vinylvault"
export GCS_BUCKET_NAME="YOUR_PROJECT_ID-vinyl-vault-data"

uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## Repository Structure

* `main.py` — FastAPI application, REST/streaming endpoints, and static asset routing
* `gemini_service.py` — Vertex AI Gemini Vision, streaming chat, and TTS pronunciation client
* `deskew_service.py` — EXIF orientation normalization, polygon segmentation, and perspective warp
* `database.py` — Firestore persistence layer with local JSON fallback (`data_store/`)
* `gcs_service.py` — Cloud Storage cover-art upload and retrieval manager
* `discogs_service.py` & `classical_service.py` — External catalog and classical music enrichment
* `click-to-deploy/` — C2D-compliant Terraform, supply-chain-pinned `requirements.txt`, `Dockerfile`, and `org_policy/`
* `docs/DEMO_GUIDE.md` — 4-Pillar Seller & Technical Demo Guide

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
