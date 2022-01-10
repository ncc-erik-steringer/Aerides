#  Copyright (c) 2022 Erik Steringer and NCC Group
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

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
