# Aerides

An implementation of infrastructure-as-code scanning using dynamic tooling.

## Background

This project is a demonstration for using Scout Suite and Principal Mapper with Terraform and LocalStack. Scout and 
PMapper are "dynamic" tools that operate by interacting with the AWS APIs to retrieve data. These tools do not have 
the capability to read/interpret infrastructure-as-code (IaC) files. 

However, by deploying IaC (Terraform HCL in this case) against an instance of LocalStack, then pointing the tools at 
LocalStack, we can still perform scanning/testing to identify risks before they make it to production infrastructure.

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

## Experimenting

To try this out with your own machine, follow these steps (tested on Ubuntu 20.04):

### Prerequisites

* Python 3.8+, using a virtualenv is *highly* recommended
* [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started)
* [LocalStack](https://github.com/localstack/localstack) (installed via `pip install localstack`)
* [mitmproxy](https://mitmproxy.org/) (installed via `pip install mitmproxy`, consider using a separate virtualenv)
* [Scout Suite](https://github.com/nccgroup/ScoutSuite) (installed via `pip install scoutsuite`)
* [Principal Mapper](https://github.com/nccgroup/PMapper) (installed via `pip install principalmapper`)

### Running

Clone this repository onto your machine. Navigate into the `Aerides/infracode` directory and run:

```bash
localstack start -d  # this will take ~30s to spin up
terraform init
terraform apply -var "acctid=000000000000"
```

This will launch LocalStack (daemon mode) and deploy the Terraform code. Now it is possible to run commands and see 
the mock infrastructure. For example:

```bash
aws configure --profile localstack  # set fake access keys, set default region to us-east-1
aws --profile localstack --endpoint-url http://localhost:4566 iam list-users
```

Run PMapper against LocalStack like so:

```bash
pmapper --profile localstack graph create --localstack-endpoint http://localhost:4566
pmapper --account 000000000000 visualize  # should output 000000000000.svg if graphviz is installed
```

**In a separate shell**, navigate to the `Aerides/mitmproxy` directory and run:

```bash
mitmdump -k --listen-host 127.0.0.1 --listen-port 8080 -s proxy_aws_to_localstack.py 
```

With `mitmdump` running, go back to your first shell and run Scout Suite while using the proxy like so:

```bash
HTTP_PROXY=http://127.0.0.1:8080 \
HTTPS_PROXY=http://127.0.0.1:8080 \
AWS_CA_BUNDLE=~/.mitmproxy/mitmproxy-ca-cert.pem \
scout aws --services iam s3 ec2 vpc --region us-east-1
```

This should generate a Scout Suite report and launch your web browser with its contents. You can try a similar 
pattern with other tools. We have been able to successfully use the following tools:

* [AWS-Inventory](https://github.com/nccgroup/aws-inventory/)
* [CloudMapper](https://github.com/duo-labs/cloudmapper)
* [Prowler](https://github.com/toniblyx/prowler)
* [Cartography](https://github.com/lyft/cartography)

**Note:** This does not constitute an endorsement of support on the behalf of those projects. Due to mismatches between 
LocalStack's responses and the AWS API's responses, these tools run into unexpected errors. You'll have to limit which 
regions/services/checks the tools run and limit which test cases you attempt to perform via these tools. 

## License

MIT, see [LICENSE](./LICENSE).
