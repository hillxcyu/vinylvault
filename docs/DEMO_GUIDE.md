# VinylVault — Multimodal Visual Cataloging & Media Asset Intelligence Seller Demo Guide

## Executive Summary & Pitch Context

- **Target Buyer Personas:** VP of Media & Archives, Head of Retail Operations & Collectibles, Director of Digital Asset Management (DAM), Chief Data & AI Officer
- **Customer Pain Point:** Organizations managing physical media archives, retail collectibles, or high-value physical inventory still rely on slow manual data entry, error-prone SKU lookup, and unstandardized smartphone photos—leading to duplicate purchases, inconsistent catalog metadata, and high operational labor costs.
- **Value Proposition:** VinylVault demonstrates how Vertex AI multimodal models (`gemini-3.6-flash` and `gemini-3.1-flash-tts-preview`), Cloud Firestore, and Cloud Storage transform skewed, real-world smartphone photos into perspective-deskewed, deduplicated, and richly enriched catalog records in under 5 seconds—cutting manual cataloging time by over 85% while preventing duplicate inventory acquisition.
- **Estimated Demo Duration:** 10–15 minutes

## How to Build

This section explains how VinylVault is architected and built end-to-end on Google Cloud using **FastAPI**, **Vertex AI Gemini**, **Cloud Firestore**, **Cloud Storage**, and **Cloud Run** behind **Identity-Aware Proxy (IAP)**.

### Step 1: Scaffold the Project & Dependencies

The application is packaged as a containerized Python 3.11 FastAPI service with supply-chain-verified dependencies:

- `click-to-deploy/requirements.in` declares direct dependencies (`fastapi`, `uvicorn`, `google-genai`, `google-cloud-aiplatform`, `google-cloud-storage`, `google-cloud-firestore`, `opencv-python-headless`, `Pillow`, `pydantic`).
- `click-to-deploy/requirements.txt` pins every direct and transitive dependency with `==` and `--hash=sha256:...` digests compiled via `uv pip compile --generate-hashes`.
- `click-to-deploy/Dockerfile` installs dependencies with `pip install --no-cache-dir --require-hashes -r requirements.txt` and launches `uvicorn main:app`.

### Step 2: Build the Multimodal Vision & Perspective Deskew Pipeline (`deskew_service.py`, `gemini_service.py`)

When a user captures or uploads a tilted photo of an album or physical item:

1. `DeskewService._fix_exif_orientation` in `deskew_service.py` normalizes mobile EXIF rotation metadata so backend pixel coordinates match browser rendering.
2. `gemini_service.py` invokes `gemini-3.6-flash` (`GOOGLE_CLOUD_LOCATION=global`) to predict the 4-corner quadrilateral polygon of the item sleeve (with an OpenCV contour-detection fallback if needed).
3. `DeskewService.auto_deskew_image` applies a perspective homography warp (`cv2.getPerspectiveTransform` and `cv2.warpPerspective`) to produce a flat, square, high-contrast WebP cover image, uploaded to Cloud Storage via `GCSStorageManager.upload_cover` in `gcs_service.py`.

### Step 3: Orchestrate Anti-Duplicate, Enrichment & Conversational Intelligence (`main.py`, `database.py`, `discogs_service.py`, `classical_service.py`)

`main.py` exposes the FastAPI endpoints powering the studio UI and multimodal workflows:

- **Duplicate Detection & Fast Extraction (`/api/scan`, `/api/scan/duplicate-check`, `/api/check-duplicate`):** Compares the incoming image and extracted title/artist/catalog number against existing records in Cloud Firestore (`FirestoreManager` in `database.py`) to flag duplicates before ingestion.
- **External Catalog & Classical Taxonomy Enrichment (`/api/fetch-release-assets`, `discogs_service.py`, `classical_service.py`):** Queries Discogs and iTunes release metadata and maps classical works (opus, movement, conductor, soloist) into structured catalog records.
- **Streaming Multimodal Chat & Audio Pronunciation (`/api/chat/stream`, `/api/listening-guide`, `/api/pronounce`):** Streams grounded collection Q&A and curatorial notes via `gemini-3.6-flash` and synthesizes foreign-language artist/composer pronunciations via `gemini-3.1-flash-tts-preview`.

### Step 4: Provision Infrastructure & Deploy to Google Cloud (`click-to-deploy/`)

The `click-to-deploy/` directory provisions the full Google Cloud stack via Terraform (`main.tf`, `variables.tf`, `providers.tf`, `outputs.tf`) using Argolis-compliant security defaults:

- Cloud Run (`INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER`) with a least-privilege runtime service account (`roles/aiplatform.user`, `roles/datastore.user`, `roles/storage.objectAdmin`, `roles/secretmanager.secretAccessor`).
- Global External HTTPS Application Load Balancer + Serverless NEG + Backend Service with Identity-Aware Proxy (IAP) enabled (`roles/run.invoker` granted exclusively to the IAP service agent).
- Cloud Firestore Native database (`vinylvault`), Cloud Storage bucket with `uniform_bucket_level_access` and `public_access_prevention`, and Secret Manager secrets.

## Pillar 1: Setup & Deployment Instructions

### 1.1 Prerequisites & IAM Permissions

- **GCP Environment:** An Argolis project or standard Google Cloud project with an active Billing Account.
- **Required IAM Roles for Deployer:** `roles/owner` (or granular `roles/run.admin`, `roles/datastore.owner`, `roles/storage.admin`, `roles/artifactregistry.admin`, `roles/compute.loadBalancerAdmin`, `roles/iap.admin`, `roles/iam.serviceAccountAdmin`, `roles/secretmanager.admin`, `roles/serviceusage.serviceUsageAdmin`).
- **Required APIs (auto-enabled by Terraform):** `aiplatform.googleapis.com`, `artifactregistry.googleapis.com`, `cloudbuild.googleapis.com`, `compute.googleapis.com`, `firestore.googleapis.com`, `iam.googleapis.com`, `iap.googleapis.com`, `logging.googleapis.com`, `run.googleapis.com`, `secretmanager.googleapis.com`, `serviceusage.googleapis.com`, `storage.googleapis.com`.
- **Vertex AI Model Access:** Ensure `gemini-3.6-flash` and `gemini-3.1-flash-tts-preview` are enabled in Vertex AI (`global` location).

### 1.2 Option A: One-Click Deployment via go/demos (Recommended)

1. Navigate to the VinylVault listing on `go/demos` and click **Deploy Demo (Click-to-Deploy)**.
2. Select your target Argolis organization and project, and choose a `data_location` (e.g., `us-central1`).
3. Wait approximately **5–8 minutes** for Terraform provisioning and container deployment to complete.

### 1.3 Option B: Manual CLI / Terraform Deployment

```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# 1. Build and push the container image to Artifact Registry
gcloud artifacts repositories create vinyl-vault-repo \
  --repository-format=docker \
  --location="${REGION}" \
  --project="${PROJECT_ID}" || true

gcloud builds submit \
  --config=cloudbuild.yaml \
  --project="${PROJECT_ID}" \
  --substitutions="_SHORT_SHA=latest" .

# 2. Provision infrastructure via Click-to-Deploy Terraform
cd click-to-deploy
terraform init
terraform apply \
  -var="project_id=${PROJECT_ID}" \
  -var="data_location=${REGION}" \
  -var="gcp_account_name=$(gcloud config get-value account)"
```

### 1.4 Deployment Verification

Verify the Cloud Run service and Load Balancer IP are healthy before your customer call:

```bash
gcloud run services list --project="${PROJECT_ID}" --region="${REGION}"
terraform -chdir=click-to-deploy output -raw app_url
```

Confirm `curl -I "$(terraform -chdir=click-to-deploy output -raw app_url)"` returns an IAP authentication redirect (`302` to `accounts.google.com`) rather than a `502` or `404`.

### 1.5 Teardown & Cost Cleanup

To avoid ongoing Cloud Run, Load Balancer, Firestore, and Storage charges after your customer session:

```bash
cd click-to-deploy
terraform destroy \
  -var="project_id=${PROJECT_ID}" \
  -var="data_location=${REGION}"
```

## Pillar 2: How to Access the Demo

### 2.1 Retrieving Entry Point URLs

- **From Click-to-Deploy:** Copy the `app_url` output from the C2D deployment completion email or dashboard.
- **From Terraform CLI:** Run `terraform -chdir=click-to-deploy output -raw app_url`.

### 2.2 Credentials & Test Personas

- **Authentication Method:** Open the `app_url` in your browser and sign in with your `@google.com` or Argolis account via **Identity-Aware Proxy (IAP)**. (If accessing as a secondary user, grant that user `roles/iap.httpsResourceAccessor` on the backend service.)
- **Optional Discogs Enrichment Token:** If you want live Discogs API enrichment beyond the built-in catalog and iTunes lookup, populate the `vinyl-vault-discogs-token` secret in Secret Manager.
- **Demo Sample Data:** The application automatically seeds a curated baseline catalog of **49+ records** (including classical, jazz, rock, and international pressings) in Firestore (`vinylvault` database) on first boot, or via `POST /api/restore-sample-data`.

### 2.3 Expected Initial Landing State

Upon opening the application URL, you should see:

- The **VinylVault Studio** dark-glass catalog interface displaying the album cover grid with genre/artist filters and collection statistics.
- A **"Scan / Upload"** action button in the top navigation bar for live camera or image-file ingestion.
- A **Daily Pick** curated spotlight card and an interactive **AI Collection Assistant** chat drawer.

## Demo Walkthrough (Pillar 3 & Pillar 4: Step-by-Step Walkthrough & Seller Talking Script)

### Opening Discovery Hook (Before Sharing Screen)

> **What to Say:** *"Many retail, media archive, and collectibles teams tell us their biggest bottleneck isn't storage—it's getting physical assets into a clean, searchable, deduplicated digital catalog without armies of manual data-entry staff. Today, how long does it take your team to photograph, identify, condition-check, and catalog a single incoming physical item—and how often do duplicates slip through?"*

### Step 1: Live Multimodal Scan & Perspective Deskew

- **What to Do (Click Sequence):**
  1. Click **Scan / Upload** in the top bar.
  2. Upload an angled or skewed photo of an album cover (for example, `test_album_cover.jpg` from the repo root, or any smartphone photo of a vinyl sleeve/book/collectible).
  3. Watch the **Corner Detection & Perspective Deskew** stage automatically frame the 4 corners and warp the image into a flat square WebP cover.
- **Expected Visual Outcome:** Within 2–4 seconds, the UI displays the original angled photo side-by-side with the **perspective-corrected, cropped cover art** and automatically populated metadata fields (Title, Artist, Release Year, Genre, Catalog Number).
- **What to Say (Seller Script):** *"Notice that the user didn't need a flatbed scanner or a photo studio. A single tilted smartphone photo goes straight to Vertex AI Gemini Vision, which predicts the exact 4-corner polygon, corrects perspective distortion, normalizes lighting, and extracts structured catalog metadata in one pass."*
- **Why Google Cloud (Differentiator Callout):** *"With Gemini 3.6 Flash on Vertex AI, you get unified multimodal reasoning—spatial polygon segmentation, multilingual OCR, and entity extraction—in a single low-latency API call, rather than stitching together separate OCR, object-detection, and LLM pipelines."*

### Step 2: Real-Time Anti-Duplicate Check & Catalog Enrichment

- **What to Do (Click Sequence):**
  1. In the scan review modal, observe the **Anti-Duplicate Status** banner. Try scanning an item already in the vault (e.g., *Bach: French Suites BWV 812-817* by *Michio Kobayashi*).
  2. Click **Enrich Metadata** (or proceed to save a new item) to pull pressing details and official cover art.
- **Expected Visual Outcome:** When a match exists in Firestore, VinylVault immediately flags a **Duplicate Detected** warning showing the existing catalog entry so the user avoids buying or ingesting a duplicate. For new items, the record is saved to **Cloud Firestore** and the deskewed WebP cover is persisted in **Cloud Storage**.
- **What to Say (Seller Script):** *"Before a record—or a retail collectible, warehouse part, or archival asset—ever hits your database, Gemini cross-checks it against your live Firestore inventory. That prevents costly duplicate purchases at the point of intake."*

### Step 3: Conversational Collection Intelligence & Multilingual Audio Pronunciation

- **What to Do (Click Sequence):**
  1. Open the **AI Collection Assistant** chat panel.
  2. Copy and paste this exact verified prompt:

```text
Which classical or baroque pressings in my vault have the most spins, and what should I spin next for a focused evening session?
```

  3. Click into any foreign-language or classical record card (e.g., *Bach: French Suites* or *Isaac Stern — Sibelius & Bruch*) and click the **Pronounce** audio icon next to the artist or composer name.
  4. Click **Generate Listening Guide** on the record detail view.
- **Expected Visual Outcome:** The streaming chat returns a grounded recommendation citing actual records from the Firestore vault. Clicking **Pronounce** plays clear spoken audio synthesized by `gemini-3.1-flash-tts-preview`. The Listening Guide displays rich historical context, pressing notes, and movement-by-movement highlights.
- **What to Say (Seller Script):** *"Beyond intake, the same multimodal foundation powers natural-language discovery across your entire catalog—and even generates native-quality audio pronunciations for international artists, SKUs, or archival terms using Gemini Flash TTS."*

### Closing & Next-Step Transition

- **Common Customer Objection & Response:**
  - *Objection:* *"Our catalog isn't vinyl records—we manage archival film reels / luxury handbags / industrial spare parts. How hard is it to adapt this?"*
  - *Response:* *"The entire pipeline—perspective deskew, anti-duplicate check, external API enrichment, and Firestore/GCS persistence—is domain-agnostic. Adapting VinylVault to your SKU taxonomy or archival schema only requires updating the Pydantic extraction schema and prompt instructions in `gemini_service.py`."*
- **Call to Action:** *"We can stand up a working prototype with 20–50 photos of your actual physical assets in a half-day Vertex AI workshop. Which product line or archive collection should we test first?"*

## Troubleshooting & Live-Demo Recovery Tips

- **Cold-Start Latency on First Scan:** Cloud Run scales to zero (`min_instance_count = 0`) when idle. Open the `app_url` and run one quick chat query 5 minutes before your customer call to warm the container.
- **Resetting Demo State:** If you added test records during a dry run and want to restore the clean baseline catalog, send a `POST /api/restore-sample-data` request (or use the UI restore action) to reset Firestore to the curated sample dataset.
- **IAP 403 Forbidden Error:** Confirm your `@google.com` or Argolis account has `roles/iap.httpsResourceAccessor` on the `vinyl-vault-backend` service in IAM & Admin → Identity-Aware Proxy.
- **Vertex AI 404 / Model Availability in New Project:** Ensure `GOOGLE_CLOUD_LOCATION=global` is set on the Cloud Run service and that the project has `aiplatform.googleapis.com` enabled.
