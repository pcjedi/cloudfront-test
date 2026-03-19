# cloudfront-test

A SAM template that deploys a static HTML page to a private S3 bucket and serves it globally via Amazon CloudFront.

## Architecture

```
Browser → CloudFront Distribution → Origin Access Control (OAC) → S3 Bucket (private)
```

- **S3 bucket** – private, server-side encrypted, versioning enabled.  The bucket is never exposed to the public internet.
- **CloudFront** – HTTPS-only (HTTP → HTTPS redirect), HTTP/2+3, configurable price class.
- **OAC** – modern replacement for OAI; CloudFront signs every request to S3 with SigV4.
- **Lambda custom resource** – uploads `index.html` on stack create/update and cleans up on delete.

## Repository layout

```
template.yaml              # SAM / CloudFormation template (single source of truth for the HTML)
functions/
  deployer/
    index.py               # Lambda handler for the S3 deployer custom resource
```

## Prerequisites

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- AWS credentials configured (`aws configure` or environment variables)

## Deploy

```bash
# 1. Build (packages the Lambda deployer)
sam build

# 2. Deploy (guided first time – saves config to samconfig.toml)
sam deploy --guided

# 3. After deployment the CloudFront URL is printed in the Outputs section:
#    CloudFrontURL  https://d1234abcd.cloudfront.net
```

### Parameters

| Parameter    | Default         | Description |
|--------------|-----------------|-------------|
| `PriceClass` | `PriceClass_100`| `PriceClass_100` (US/CA/EU), `PriceClass_200` (+ Asia/ME/Africa), `PriceClass_All` |

## Cleanup

```bash
sam delete
```

> **Note:** The S3 bucket will be emptied by the custom resource during stack deletion, allowing CloudFormation to remove it automatically.
