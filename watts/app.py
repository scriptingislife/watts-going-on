import boto3
import json
import os
import logging
from datetime import datetime
from pytz import timezone

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.content_encoding import ContentEncoding
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem

ENV = os.environ.get("ENV", "")
SERVICE = os.environ.get("SERVICE", "watts")
SOURCE = os.environ.get("SOURCE", "watts-ifttt")
VERSION = os.environ.get("VERSION", "")
DD_API_KEY_PARAM = os.environ.get("DD_API_KEY_PARAM", "DDApiKey")

if ENV == "staging":
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)

def timestamp_conversion(createdAt):
    # Convert 'CreatedAt' datetime provided by IFTTT to ISO 8601
    d = datetime.strptime(createdAt, "%B %d, %Y at %I:%M%p")
    ny_time = timezone('America/New_York').localize(d)
    utc_time = ny_time.astimezone(timezone('UTC'))
    return utc_time.strftime("%Y-%m-%dT%H:%M:%S%z")

def get_param(name):
    # Get an SSM parameter by name
    logging.debug("Fetching SSM parameter")
    ssm = boto3.client('ssm')
    parameter = ssm.get_parameter(Name=name, WithDecryption=True)
    return parameter['Parameter']['Value']

def send_dd_log(payload):
    logging.debug("Logging data: " + str(payload))
    body = HTTPLog(
        [
            HTTPLogItem(
                ddsource=SOURCE,
                ddtags=f"env:{ENV},version:{VERSION}",
                message=json.dumps(payload),
                service=SERVICE,
            ),
        ]
    )

    configuration = Configuration()
    configuration.api_key["apiKeyAuth"] = get_param(DD_API_KEY_PARAM)
    with ApiClient(configuration) as api_client:
        api_instance = LogsApi(api_client)
        response = api_instance.submit_log(content_encoding=ContentEncoding.DEFLATE, body=body)
        print(response)


def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        if "CreatedAt" not in body.keys() and "date" not in body.keys():
            logging.error("Timestamp not in request body")
            raise KeyError
    except Exception as e:
        logging.error("Failed to load request body")
        logging.debug(e)
        logging.debug(event["body"])
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "oopsies. please include a legit body"
            })
        }

    if "timestamp" not in body.keys():
        # Convert IFTTT time to a format Datadog accepts
        timestamp = body.get("CreatedAt", body.get("date"))
        body["timestamp"] = timestamp_conversion(timestamp)

    logging.info("Logging ride created at " + str(body["timestamp"]))
    send_dd_log(body)
    logging.info("Done")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "uploaded"
        }),
    }
