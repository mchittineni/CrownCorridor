# CIS AWS 2.1 - S3 Public Access Misconfiguration

resource "aws_s3_bucket" "example" {
  bucket = "test-public-bucket"
}

resource "aws_s3_bucket_public_access_block" "example" {
  bucket                  = aws_s3_bucket.example.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
