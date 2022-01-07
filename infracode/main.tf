provider "aws" {
  access_key = "fake_access_key"
  secret_key = "fake_secret_key"
  region = "us-east-1"
  s3_force_path_style = true
  skip_credentials_validation = true
  skip_metadata_api_check = true
  skip_requesting_account_id = true

  endpoints {
    ec2 = "http://localhost:4566"
    iam = "http://localhost:4566"
    lambda = "http://localhost:4566"
    s3 = "http://localhost:4566"
    secretsmanager = "http://localhost:4566"
    sts = "http://localhost:4566"
  }
}

module "api" {
  source = "./modules/tktk_service_api"
  acctid = var.acctid
}

module "principals" {
  source = "./modules/tktk_service_other_personnel"
  acctid = var.acctid
}

module "finances" {
  source = "./modules/tktk_service_finances"
  acctid = var.acctid
}

module "support" {
  source = "./modules/tktk_service_support"
  acctid = var.acctid
}

module "website" {
  source = "./modules/tktk_service_website"
  acctid = var.acctid
}

