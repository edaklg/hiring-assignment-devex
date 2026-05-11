resource "google_secret_manager_secret" "mongo_connection_string" {
  secret_id = "mongo-connection-string"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "mongo_connection_string" {
  secret      = google_secret_manager_secret.mongo_connection_string.id
  secret_data = var.mongo_connection_string
}
