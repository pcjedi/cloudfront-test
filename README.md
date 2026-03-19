# cloudfront-test

A SAM template that deploys a static HTML page to a private S3 bucket and serves it globally via Amazon CloudFront. CI/CD is handled by GitHub Actions.

## Architecture

```
Browser → CloudFront Distribution → Origin Access Control (OAC) → S3 Bucket (private)
```

- **S3 bucket** – private, server-side encrypted. The bucket is never exposed to the public internet.
- **CloudFront** – HTTPS-only (HTTP → HTTPS redirect), HTTP/2+3, configurable price class.
- **OAC** – modern replacement for OAI; CloudFront signs every request to S3 with SigV4.
- **GitHub Actions** – deploys the stack and syncs website files on push/PR, tears down PR stacks on close.

## Repository layout

```
template.yaml              # SAM / CloudFormation template
web/
  index.html               # Static website content
.github/workflows/
  deploy.yaml              # Build, deploy stack, sync files, invalidate cache
  delete.yaml              # Tear down PR stacks on PR close
```

## CI/CD

### deploy.yaml

Triggered on **push to `main`** and **pull requests**:

1. Builds and deploys the SAM stack.
2. Syncs `web/` to the S3 bucket.
3. Invalidates the CloudFront cache.
4. On PRs, comments the CloudFront URL on the pull request.

Push to `main` deploys to both `staging` and `production` environments. PRs deploy to `staging` only.

### delete.yaml

Triggered when a **pull request is closed**:

1. Empties and deletes the S3 bucket.
2. Deletes the SAM stack.

## Prerequisites

- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- AWS credentials configured (`aws configure` or environment variables)

## Manual deploy

```bash
sam build
sam deploy --guided
```

The CloudFront URL is printed in the Outputs section after deployment.

### Parameters

| Parameter    | Default         | Description |
|--------------|-----------------|-------------|
| `PriceClass` | `PriceClass_100`| `PriceClass_100` (US/CA/EU), `PriceClass_200` (+ Asia/ME/Africa), `PriceClass_All` |

## Cleanup

```bash
# Empty the bucket first, then delete the stack
aws s3 rm s3://<bucket-name> --recursive
sam delete
```
