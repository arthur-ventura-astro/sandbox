locals {
  astro_account = "700010564577"
  astro_root = "arn:aws:iam::${local.astro_account}:root"
}

output "astro_root" {
  value = local.astro_root
}
output "astro_account" {
  value = local.astro_account
}