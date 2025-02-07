
resource "aws_s3_bucket" "data_bucket" {
  bucket = module.data.data_bucket
}

resource "aws_s3_bucket_public_access_block" "data_bucket" {
  bucket = aws_s3_bucket.data_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "xcom_bucket" {
  bucket = module.data.xcom_bucket
}

resource "aws_s3_bucket_public_access_block" "xcom_bucket" {
  bucket = aws_s3_bucket.xcom_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}