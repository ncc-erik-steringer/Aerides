# Aerides

An implementation of infrastructure-as-code scanning using dynamic tooling.

## Background

This project is a demonstration for using Scout Suite and Principal Mapper with Terraform and LocalStack. Scout and 
PMapper are "dynamic" tools that operate by interacting with the AWS APIs to retrieve data. These tools do not have 
the capability to read/interpret infrastructure-as-code (IaC) files. 

However, by deploying IaC (Terraform in this case) against an instance of LocalStack, then pointing the tools at 
LocalStack, we can still perform scanning/evaluation for continuous integration.

## Implementation

This repository contains Terraform code that implements parts of a service, called TKTK Service. That includes S3 
buckets, VPCs + Security Groups, and IAM Users/Groups/Roles. 

This code can be deployed to LocalStack (see [infracode/main.tf](infracode/main.tf) for details).

Once deployed, it is possible to use PMapper and Scout Suite to interact with LocalStack. PMapper supports LocalStack 
out of the box (via `graph create` with the `--localstack-endpoint` parameter). However, Scout Suite does not have 
built-in support. Instead, there's a mitmproxy addon script in 
[mitmproxy/proxy_aws_to_localstack.py](mitmproxy/proxy_aws_to_localstack.py). By setting the `HTTP_PROXY`, 
`HTTPS_PROXY`, and `AWS_CA_BUNDLE` environment variables to point to a running proxy with that script, it is possible 
to point Scout Suite (and any other dynamic tools) to LocalStack.

After PMapper and Scout Suite run, they leave different outputs that can be handled with test code. In this demo, 
there are test cases that check for privlege escalation risks, restrictions on lower-priv users from calling 
s3:PutObject, IAM Policies with NotAction fields, and security groups that open ports to the world. This repo has 
GitHub Actions that will execute these test cases for Pull Requests.

