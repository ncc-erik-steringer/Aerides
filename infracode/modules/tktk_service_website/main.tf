/*
  Infracode for a static website (S3). Also includes the user that has
  access to update the website.
*/

resource "aws_s3_bucket" "service_website" {
  bucket = "tktk-service-website"
  acl = "public-read"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "s3:GetObject"
        Resource = "arn:aws:s3:::tktk-service-website/*"
      }
    ]
  })
  website {
    index_document = "index.html"
    error_document = "error.html"
    routing_rules = jsonencode([
      {
        Condition = {
          KeyPrefixEquals = "src/"
        }
        Redirect = {
          ReplaceKeyPrefixWith = "source/"
        }
      }
    ])
  }
  tags = {
    component = "website"
  }
}

resource "aws_iam_user" "website_user_gabe" {
  name = "gabe"
  tags = {
    dept = "developers"
    component = "website"
  }
}

resource "aws_iam_user_policy" "website_user_gabe_policy" {
  name = "permissions-1"
  user = aws_iam_user.website_user_gabe.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "arn:aws:s3:::tktk-service-website/*"
      }
    ]
  })
}
