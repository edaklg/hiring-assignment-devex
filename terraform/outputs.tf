output "insights_url" {
  description = "Public URL for the Deployment Insights API"
  value       = google_cloud_run_v2_service.insights.uri
}

output "registry_url" {
  description = "Internal URL for the Deployment Registry API"
  value       = google_cloud_run_v2_service.registry.uri
}

output "artifact_registry_url" {
  description = "Docker registry URL for pushing images"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.services.repository_id}"
}
