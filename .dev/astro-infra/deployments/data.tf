variable "contact" {
  type = string
}
variable "cluster" {
  type = string
  sensitive = true
}
variable "organization" {
  type = string
  sensitive = true
}
variable "workspace" {
  type = string
  sensitive = true
}

variable "workspace_token" {
  type = string
  sensitive = true
}
variable "github_token" {
  type = string
  sensitive = true
}

variable "aws_access_key_id" {
  type = string
  sensitive = true
}
variable "aws_secret_access_key" {
  type = string
  sensitive = true
}

locals {
  repository = "sandbox"
}