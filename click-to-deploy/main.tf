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

data "google_project" "current" {
  project_id = var.project_id
}

locals {
  services = [
    "aiplatform.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "compute.googleapis.com",
    "firestore.googleapis.com",
    "iam.googleapis.com",
    "iap.googleapis.com",
    "logging.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "serviceusage.googleapis.com",
    "storage.googleapis.com",
  ]

  runtime_roles = [
    "roles/aiplatform.user",
    "roles/datastore.user",
    "roles/logging.logWriter",
    "roles/serviceusage.serviceUsageConsumer",
  ]

  secret_project_id = coalesce(var.secret_stored_project, var.project_id)
  effective_image = coalesce(
    var.container_image,
    "${var.data_location}-docker.pkg.dev/${var.project_id}/${var.artifact_repo}/${var.service_name}:latest"
  )
  effective_domain = coalesce(
    var.lb_domain,
    "${google_compute_global_address.web.address}.sslip.io"
  )
  iap_audience = "/projects/${data.google_project.current.number}/global/backendServices/${google_compute_backend_service.web.generated_id}"
}

# -----------------------------------------------------------------------------
# Enable Required Google Cloud APIs
# -----------------------------------------------------------------------------

resource "google_project_service" "enabled" {
  for_each           = toset(local.services)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# -----------------------------------------------------------------------------
# Least-Privilege Runtime Service Account & IAM
# -----------------------------------------------------------------------------

resource "google_service_account" "runtime" {
  project      = var.project_id
  account_id   = "${var.service_name}-runtime"
  display_name = "VinylVault Cloud Run Runtime Service Account"
  depends_on   = [google_project_service.enabled]
}

resource "google_project_iam_member" "runtime_roles" {
  for_each = toset(local.runtime_roles)
  project  = var.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.runtime.email}"
}

# -----------------------------------------------------------------------------
# Artifact Registry, Cloud Storage & Firestore
# -----------------------------------------------------------------------------

resource "google_artifact_registry_repository" "images" {
  project       = var.project_id
  location      = var.data_location
  repository_id = var.artifact_repo
  format        = "DOCKER"
  description   = "Container images for VinylVault Multimodal Visual Cataloging Studio"
  depends_on    = [google_project_service.enabled]
}

resource "google_storage_bucket" "cover_art" {
  project                     = var.project_id
  name                        = "${var.project_id}-vinyl-vault-data"
  location                    = var.data_location
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = true
  depends_on                  = [google_project_service.enabled]
}

resource "google_storage_bucket_iam_member" "runtime_cover_art_admin" {
  bucket = google_storage_bucket.cover_art.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_firestore_database" "vinylvault" {
  project                     = var.project_id
  name                        = var.firestore_database_id
  location_id                 = var.data_location
  type                        = "FIRESTORE_NATIVE"
  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"
  deletion_policy             = "DELETE"
  depends_on                  = [google_project_service.enabled]
}

# -----------------------------------------------------------------------------
# Dynamic Secrets in Secret Manager (No Hardcoded Credentials)
# -----------------------------------------------------------------------------

resource "random_password" "app_session_secret" {
  length  = 32
  special = false
}

resource "google_secret_manager_secret" "app_session_secret" {
  project   = local.secret_project_id
  secret_id = "${var.service_name}-session-secret"
  replication {
    auto {}
  }
  depends_on = [google_project_service.enabled]
}

resource "google_secret_manager_secret_version" "app_session_secret_version" {
  secret      = google_secret_manager_secret.app_session_secret.id
  secret_data = random_password.app_session_secret.result
}

resource "google_secret_manager_secret_iam_member" "runtime_session_secret_accessor" {
  project   = local.secret_project_id
  secret_id = google_secret_manager_secret.app_session_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

resource "google_secret_manager_secret" "discogs_token" {
  project   = local.secret_project_id
  secret_id = "${var.service_name}-discogs-token"
  replication {
    auto {}
  }
  depends_on = [google_project_service.enabled]
}

resource "google_secret_manager_secret_iam_member" "runtime_discogs_accessor" {
  project   = local.secret_project_id
  secret_id = google_secret_manager_secret.discogs_token.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.runtime.email}"
}

# -----------------------------------------------------------------------------
# Cloud Run Service (Argolis-Compliant Load-Balancer-Only Ingress)
# -----------------------------------------------------------------------------

resource "google_cloud_run_v2_service" "web" {
  project             = var.project_id
  name                = var.service_name
  location            = var.data_location
  deletion_protection = false
  ingress             = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account  = google_service_account.runtime.email
    timeout          = "3600s"
    session_affinity = true

    scaling {
      min_instance_count = 0
      max_instance_count = 4
    }

    containers {
      image = local.effective_image

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = "global"
      }
      env {
        name  = "FIRESTORE_DATABASE_ID"
        value = google_firestore_database.vinylvault.name
      }
      env {
        name  = "GCS_BUCKET_NAME"
        value = google_storage_bucket.cover_art.name
      }
      env {
        name  = "IAP_EXPECTED_AUDIENCE"
        value = local.iap_audience
      }
      env {
        name = "APP_SESSION_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.app_session_secret.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  depends_on = [
    google_project_iam_member.runtime_roles,
    google_secret_manager_secret_version.app_session_secret_version,
    google_secret_manager_secret_iam_member.runtime_session_secret_accessor,
    google_firestore_database.vinylvault,
    google_storage_bucket.cover_art,
  ]
}

resource "google_project_service_identity" "iap" {
  provider   = google-beta
  project    = var.project_id
  service    = "iap.googleapis.com"
  depends_on = [google_project_service.enabled]
}

resource "google_cloud_run_v2_service_iam_member" "iap_invoker" {
  project  = var.project_id
  location = google_cloud_run_v2_service.web.location
  name     = google_cloud_run_v2_service.web.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_project_service_identity.iap.email}"
}

# -----------------------------------------------------------------------------
# External HTTPS Application Load Balancer + Serverless NEG + Backend IAP
# -----------------------------------------------------------------------------

resource "google_compute_global_address" "web" {
  project    = var.project_id
  name       = "${var.service_name}-ip"
  depends_on = [google_project_service.enabled]
}

resource "google_compute_region_network_endpoint_group" "web" {
  project               = var.project_id
  name                  = "${var.service_name}-neg"
  region                = var.data_location
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = var.service_name
  }

  depends_on = [google_project_service.enabled]
}

resource "google_compute_backend_service" "web" {
  project               = var.project_id
  name                  = "${var.service_name}-backend"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  protocol              = "HTTPS"
  timeout_sec           = 3600

  backend {
    group = google_compute_region_network_endpoint_group.web.id
  }

  iap {
    enabled = true
  }

  lifecycle {
    ignore_changes = [iap]
  }
}

resource "google_iap_web_backend_service_iam_member" "deployer_access" {
  count               = var.gcp_account_name != "" ? 1 : 0
  project             = var.project_id
  web_backend_service = google_compute_backend_service.web.name
  role                = "roles/iap.httpsResourceAccessor"
  member              = "user:${var.gcp_account_name}"
}

resource "google_compute_url_map" "web" {
  project         = var.project_id
  name            = "${var.service_name}-urlmap"
  default_service = google_compute_backend_service.web.id
}

resource "google_compute_managed_ssl_certificate" "web" {
  project = var.project_id
  name    = "${var.service_name}-cert"
  managed {
    domains = [local.effective_domain]
  }
  depends_on = [google_project_service.enabled]
}

resource "google_compute_target_https_proxy" "web" {
  project          = var.project_id
  name             = "${var.service_name}-https-proxy"
  url_map          = google_compute_url_map.web.id
  ssl_certificates = [google_compute_managed_ssl_certificate.web.id]
}

resource "google_compute_global_forwarding_rule" "https" {
  project               = var.project_id
  name                  = "${var.service_name}-https"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  ip_address            = google_compute_global_address.web.id
  port_range            = "443"
  target                = google_compute_target_https_proxy.web.id
}

resource "google_compute_url_map" "redirect" {
  project = var.project_id
  name    = "${var.service_name}-http-redirect"
  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
  depends_on = [google_project_service.enabled]
}

resource "google_compute_target_http_proxy" "redirect" {
  project = var.project_id
  name    = "${var.service_name}-http-proxy"
  url_map = google_compute_url_map.redirect.id
}

resource "google_compute_global_forwarding_rule" "http" {
  project               = var.project_id
  name                  = "${var.service_name}-http"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  ip_address            = google_compute_global_address.web.id
  port_range            = "80"
  target                = google_compute_target_http_proxy.redirect.id
}
