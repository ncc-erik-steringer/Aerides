/*
  Infracode for the TKTK Service's API, the "api" component as reflected
  in resource tags. The resources that are most necessary to demonstrate
  in Aerides are written out and ready to deploy on LocalStack.

  Includes:
    * IAM Role (with inline policy) + Instance Profile
    * S3 Bucket (with bucket policy)

  Excluded:
    * DynamoDB Table
    * EC2 AutoScaling Group
    * Application Load Balancer
*/

resource "aws_s3_bucket" "api_logs_bucket" {
  bucket = "tktk-service-api-logs"
  acl = "private"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action = "s3:GetObject"
        Resource = "arn:aws:s3:::tktk-service-api-logs/*"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = var.acctid,
            "aws:PrincipalTag/dept": [
              "developers",
              "operators",
              "support"
            ]
          }
        }
      }
    ]
  })
  tags = {
    component = "api"
  }
}

resource "aws_iam_role" "api_host_role" {
  name = "APIEC2BackendHostRole"
  tags = {
    component = "api"
    notexposed = "false"
  }
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "sts:AssumeRole"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
  inline_policy {
    name = "permissions-1"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Effect = "Allow"
          Action = "s3:PutObject"
          Resource = format("%s/*", aws_s3_bucket.api_logs_bucket.arn)
        },
        {
          Effect = "Allow"
          Action = [
            "dynamodb:Query",
            "dynamodb:Scan",
            "dynamodb:PutItem"
          ]
          Resource = format("arn:aws:dynamodb:us-east-1:%s:table/api_data", var.acctid)
        }
      ]
    })
  }
}

resource "aws_iam_instance_profile" "api_host_instance_profile" {
  name = "APIEC2BackendHostRoleInstanceProfile"
  role = aws_iam_role.api_host_role.name
}

resource "aws_iam_user" "api_developer_user" {
  name = "robert"
  tags = {
    dept = "developers"
    component = "api"
  }
}

resource "aws_iam_user_policy" "api_developer_user_policy" {
  user   = aws_iam_user.api_developer_user.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "autoscaling:*",
          "elasticloadbalancer:*",
          "dynamodb:*"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = "iam:PassRole"
        Resource = "*"
        Condition = {
          "StringEquals" = {
            "iam:PassedToService" = "ec2.amazonaws.com"
          }
        }
      }
    ]
  })
}

resource "aws_vpc" "api_vpc" {
  cidr_block = "10.0.1.0/24"
  tags = {
    component = "api"
  }
}

resource "aws_security_group" "api_sg" {
  ingress {
    description = "Incoming TLS"
    protocol  = "tcp"
    from_port = 443
    to_port   = 443
    cidr_blocks = ["10.0.0.0/8"]
  }

  egress {
    from_port = 0
    protocol  = "-1"
    to_port   = 0
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    component = "api"
  }
}

/*
  NOTE

  The remainder of items in here are just for demonstration, and
  show how the rest of this template would theoretically be set up.
*/

// resource "aws_dynamodb_table" "api_backend_ddb" { }

// resource "aws_autoscaling_group" "api_backend_hosts" { }

// resource "aws_alb" "api_load_balancer" { }

