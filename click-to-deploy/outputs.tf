# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

output "app_url" {
  description = "External HTTPS Load Balancer URL protected by Identity-Aware Proxy (IAP)."
  value       = "https://${local.effective_domain}"
}

output "lb_ip" {
  description = "Global static IP address of the External HTTPS Application Load Balancer."
  value       = google_compute_global_address.web.address
}

output "cloud_run_service" {
  description = "Deployed Cloud Run service name."
  value       = google_cloud_run_v2_service.web.name
}

output "backend_service" {
  description = "Backend service name with IAP enabled."
  value       = google_compute_backend_service.web.name
}

output "firestore_database" {
  description = "Provisioned Firestore Native database name."
  value       = google_firestore_database.vinylvault.name
}

output "cover_art_bucket" {
  description = "GCS bucket storing deskewed cover art and uploaded media."
  value       = google_storage_bucket.cover_art.name
}

output "artifact_registry_repo" {
  description = "Artifact Registry Docker repository URI."
  value       = "${var.data_location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}"
}

output "runtime_service_account" {
  description = "Least-privilege Cloud Run runtime service account email."
  value       = google_service_account.runtime.email
}
