variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for GCS bucket"
  type        = string
  default     = "us-central1"
}

variable "bq_location" {
  description = "BigQuery dataset location"
  type        = string
  default     = "US"
}

variable "bucket_name" {
  description = "GCS bucket name"
  type        = string
}

variable "credentials_path" {
  description = "Path to GCP service account credentials JSON"
  type        = string
  default     = "../secrets/gcp-credentials.json"
}