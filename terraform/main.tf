terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(var.credentials_path)
}

resource "google_storage_bucket" "raw" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = false
}

resource "google_bigquery_dataset" "bronze" {
  dataset_id = "bronze"
  location   = var.bq_location
}

resource "google_bigquery_dataset" "ecommerce_pipeline_staging" {
  dataset_id = "ecommerce_pipeline_staging"
  location   = var.bq_location
}

resource "google_bigquery_dataset" "ecommerce_pipeline_gold" {
  dataset_id = "ecommerce_pipeline_gold"
  location   = var.bq_location
}