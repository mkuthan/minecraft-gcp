variable "project" {
  type = string
}

variable "region" {
  type = string
}

variable "zone" {
  type = string
}

variable "bucket_location" {
  type = string
}

variable "app_engine_location" {
  type = string
}

variable "cloud_scheduler_region" {
  type = string
}

variable "disk_size_gb" {
  type = string
}

variable "minecraft_version" {
  type = string
}

variable "minecraft_port" {
  type = number
  default = 25565
}

variable "rcon_port" {
  type = number
  default = 28016
}
