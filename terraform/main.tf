terraform {
  required_version = "~> 0.14"

  required_providers {
    google = {
      source = "hashicorp/google"
      version = "3.62.0"
    }
    random = {
      source = "hashicorp/random"
      version = "3.1.0"
    }
  }

  backend "gcs" {
    bucket = "minecraft-272917-terraform"
    prefix = "main"
  }
}

provider "google" {
  project = var.project
  region = var.region
  zone = var.zone
}

locals {
  startup_script = templatefile("${path.module}/templates/startup.sh.tpl", {
    bucket = google_storage_bucket.bucket.url
    minecraft_version = var.minecraft_version
    minecraft_port = var.minecraft_port
    rcon_port = var.rcon_port
  })

  shutdown_script = templatefile("${path.module}/templates/shutdown.sh.tpl", {
    bucket = google_storage_bucket.bucket.url
  })
}

resource "random_string" "id" {
  length = 8
  special = false
  upper = false
}

//
// Minecraft Server
//

resource "google_service_account" "service_account" {
  account_id = "minecraft"
}

resource "google_storage_bucket" "bucket" {
  name = "minecraft-${random_string.id.result}"
  location = var.bucket_location
}

resource "google_compute_network" "network" {
  name = "minecraft-network"
}

resource "google_compute_disk" "disk" {
  name = "minecraft-disk"
  type = "pd-standard"
  image = "cos-cloud/cos-stable"
  size = var.disk_size_gb
}

resource "google_compute_address" "address" {
  name = "minecraft-address"
}

resource "google_compute_firewall" "firewall" {
  name = "minecraft-firewall"
  network = google_compute_network.network.id
  target_tags = ["minecraft"]

  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports = [22, var.minecraft_port, var.rcon_port]
  }
  allow {
    protocol = "icmp"
  }
}

resource "google_compute_instance" "server" {
  name = "minecraft-server"
  machine_type = "e2-medium"
  tags = ["minecraft"]

  allow_stopping_for_update = true

  metadata = {
    startup-script = local.startup_script
    shutdown-script = local.shutdown_script
  }

  boot_disk {
    source = google_compute_disk.disk.id
    auto_delete = false
  }

  network_interface {
    network = google_compute_network.network.id
    access_config {
      nat_ip = google_compute_address.address.address
    }
  }

  service_account {
    email = google_service_account.service_account.email
    scopes = ["cloud-platform"]
  }
}

//
// Cloud Functions
//

resource "google_app_engine_application" "app_engine" {
  location_id = var.app_engine_location
}

resource "google_pubsub_topic" "topic_jobs" {
  name = "ten-minutes-jobs"
}

resource "google_cloud_scheduler_job" "scheduler_job" {
  name = "ten-minutes-jobs"
  schedule = "*/10 * * * *"
  region = var.cloud_scheduler_region

  pubsub_target {
    topic_name = google_pubsub_topic.topic_jobs.id
    data = base64encode(" ")
  }
}
