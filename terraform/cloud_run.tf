locals {
  image_base = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.services.repository_id}"
}

resource "google_cloud_run_v2_service" "registry" {
  name     = "deployment-registry"
  location = var.region

  deletion_protection = false

  template {
    service_account = google_service_account.registry.email

    containers {
      image = "${local.image_base}/deployment-registry:${var.image_tag}"

      ports {
        container_port = 8080
      }

      env {
        name  = "MongoDb__DatabaseName"
        value = "deployment-registry"
      }

      env {
        name  = "MongoDb__CollectionName"
        value = "deployments"
      }

      env {
        name = "MongoDb__ConnectionString"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.mongo_connection_string.secret_id
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }

  depends_on = [
    google_project_service.apis,
    google_secret_manager_secret_iam_member.registry_mongo_secret,
  ]
}

resource "google_cloud_run_v2_service" "insights" {
  name     = "deployment-insights"
  location = var.region

  deletion_protection = false

  template {
    service_account = google_service_account.insights.email

    containers {
      image = "${local.image_base}/deployment-insights:${var.image_tag}"

      ports {
        container_port = 8000
      }

      env {
        name  = "REGISTRY_URL"
        value = google_cloud_run_v2_service.registry.uri
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "256Mi"
        }
      }
    }
  }

  depends_on = [
    google_project_service.apis,
    google_cloud_run_v2_service_iam_member.insights_invokes_registry,
  ]
}

# Expose insights publicly — it's the user-facing API
resource "google_cloud_run_v2_service_iam_member" "insights_public" {
  name     = google_cloud_run_v2_service.insights.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
