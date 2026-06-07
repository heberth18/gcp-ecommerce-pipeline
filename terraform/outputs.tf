output "bucket_name" {
  description = "GCS bucket name"
  value       = google_storage_bucket.raw.name
}

output "bronze_dataset_id" {
  description = "BigQuery bronze dataset ID"
  value       = google_bigquery_dataset.bronze.dataset_id
}

output "staging_dataset_id" {
  description = "BigQuery staging dataset ID"
  value       = google_bigquery_dataset.ecommerce_pipeline_staging.dataset_id
}

output "gold_dataset_id" {
  description = "BigQuery gold dataset ID"
  value       = google_bigquery_dataset.ecommerce_pipeline_gold.dataset_id
}