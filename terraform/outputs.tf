output "project" {
  value = google_compute_instance.server.project
}

output "zone" {
  value = google_compute_instance.server.zone
}

output "server_name" {
  value = google_compute_instance.server.name
}

output "bucket_url" {
  value = google_storage_bucket.bucket.url
}

output "address" {
  value = google_compute_address.address.address
}
