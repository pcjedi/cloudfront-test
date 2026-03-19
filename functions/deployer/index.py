"""Custom CloudFormation resource that uploads the website HTML to S3.

On Create/Update: puts index.html in the target bucket.
On Delete:        removes index.html from the bucket so the bucket can be deleted cleanly.
"""
import json
import logging
import urllib.parse
import urllib.request

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# CloudFormation always sends a pre-signed HTTPS S3 URL as the response endpoint.
_ALLOWED_RESPONSE_SCHEMES = {"https"}
_ALLOWED_RESPONSE_SUFFIXES = (".amazonaws.com",)


def send(event, context, status, data=None, reason=None):
    """Send a response to the CloudFormation pre-signed URL."""
    raw_url = event["ResponseURL"]
    parsed = urllib.parse.urlparse(raw_url)

    if parsed.scheme not in _ALLOWED_RESPONSE_SCHEMES:
        raise ValueError(f"ResponseURL scheme '{parsed.scheme}' is not allowed")
    if not any(parsed.netloc.endswith(suffix) for suffix in _ALLOWED_RESPONSE_SUFFIXES):
        raise ValueError(f"ResponseURL host '{parsed.netloc}' is not an allowed amazonaws.com domain")

    # Reconstruct URL from individually validated components so the value is not tainted.
    response_url = urllib.parse.urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
    )

    body = json.dumps(
        {
            "Status": status,
            "Reason": reason or f"See CloudWatch log stream: {context.log_stream_name}",
            "PhysicalResourceId": event.get("PhysicalResourceId", context.log_stream_name),
            "StackId": event["StackId"],
            "RequestId": event["RequestId"],
            "LogicalResourceId": event["LogicalResourceId"],
            "Data": data or {},
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        url=response_url,
        data=body,
        method="PUT",
        headers={"Content-Type": "", "Content-Length": len(body)},
    )
    urllib.request.urlopen(req)


def handler(event, context):
    logger.info("Event: %s", json.dumps(event))
    props = event["ResourceProperties"]
    bucket = props["BucketName"]
    html_content = props["HtmlContent"]

    try:
        s3 = boto3.client("s3")

        if event["RequestType"] in ("Create", "Update"):
            s3.put_object(
                Bucket=bucket,
                Key="index.html",
                Body=html_content.encode("utf-8"),
                ContentType="text/html; charset=utf-8",
                CacheControl="max-age=86400",
            )
            logger.info("Uploaded index.html to s3://%s/index.html", bucket)

        elif event["RequestType"] == "Delete":
            s3.delete_object(Bucket=bucket, Key="index.html")
            logger.info("Deleted index.html from s3://%s/index.html", bucket)

        send(event, context, "SUCCESS")

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Deployer failed")
        send(event, context, "FAILED", reason=str(exc))
