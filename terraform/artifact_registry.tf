resource "google_artifact_registry_repository" "services" {
  repository_id = "deployment-services"
  location      = var.region
  format        = "DOCKER"
  description   = "Container images for deployment registry and insights services"

  depends_on = [google_project_service.apis]
}
