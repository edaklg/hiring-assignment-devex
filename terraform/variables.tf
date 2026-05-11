variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "europe-west1"
}

variable "mongo_connection_string" {
  description = "MongoDB Atlas connection string (stored in Secret Manager)"
  type        = string
  sensitive   = true
}

variable "image_tag" {
  description = "Container image tag to deploy"
  type        = string
  default     = "latest"
}
