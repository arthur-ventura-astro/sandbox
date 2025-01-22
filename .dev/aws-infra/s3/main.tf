
resource "aws_s3_bucket" "data_bucket" {
  bucket = module.data.data_bucket
}

resource "aws_s3_bucket" "xcom_bucket" {
  bucket = module.data.xcom_bucket
}