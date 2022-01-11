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
  Infracode for the support staff. For this demo, the support staff access the
  account through IAM Role Sessions (Cognito AuthN), while this code defines the IAM Role resource
  plus the associated policy.
*/

resource "aws_iam_role" "support_iam_role" {
  name = "support-staff"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = "cognito-identity.amazonaws.com"
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "cognito-identity.amazonaws.com:aud" = "us-east:12345678-ffff-ffff-ffff-123456"
          }
        }
      }
    ]
  })
  tags = {
    dept = "support"
  }
}

resource "aws_iam_role_policy" "support_iam_role_policy" {
  name = "support-permissions-1"
  role = aws_iam_role.support_iam_role.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "autoscaling:Get*",
          "elasticloadbalancing:List*",
          "elasticloadbalancing:Get*",
          "iam:PassRole"
        ],
        Resource = "*"
      }
    ]
  })
}

