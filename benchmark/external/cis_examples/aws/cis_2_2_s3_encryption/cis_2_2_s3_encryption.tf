# CIS AWS 2.2 - S3 Bucket Encryption Disabled

resource "aws_s3_bucket" "unencrypted" {
  bucket = "test-unencrypted-bucket"
}
