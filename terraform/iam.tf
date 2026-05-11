resource "google_service_account" "registry" {
  account_id   = "deployment-registry"
  display_name = "Deployment Registry Service Account"
}

resource "google_service_account" "insights" {
  account_id   = "deployment-insights"
  display_name = "Deployment Insights Service Account"
}

# Registry SA needs to read the MongoDB connection string secret
resource "google_secret_manager_secret_iam_member" "registry_mongo_secret" {
  secret_id = google_secret_manager_secret.mongo_connection_string.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.registry.email}"
}

# Insights SA needs to invoke the Registry Cloud Run service
resource "google_cloud_run_v2_service_iam_member" "insights_invokes_registry" {
  name     = google_cloud_run_v2_service.registry.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.insights.email}"
}
