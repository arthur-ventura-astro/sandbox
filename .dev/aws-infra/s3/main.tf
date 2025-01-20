locals {
  data_bucket = "${module.data.project_name}-data"
}

resource "aws_s3_bucket" "data_bucket" {
  bucket = local.data_bucket
}

resource "aws_s3_bucket_public_access_block" "data_bucket" {
  bucket = aws_s3_bucket.data_bucket.id

  block_public_acls   = false
  block_public_policy = false
}