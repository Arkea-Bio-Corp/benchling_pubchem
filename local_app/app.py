import json

from benchling_sdk.apps.helpers.webhook_helpers import verify
from local_app.benchling_app.handler import handle_webhook
from local_app.benchling_app.setup import app_definition_id
from local_app.lib.logger import get_logger

logger = get_logger()
logger.setLevel("INFO")


def handler(event, context):
    print(event)
    # For security, don't do anything else without first verifying the webhook
    app_def_id = app_definition_id()

    verify(app_def_id, event["body"], event["headers"])

    logger.debug("Received webhook message: %s", event["body"])

    handle_webhook(json.loads(event["body"]))

    return {"statusCode": 200, "body": json.dumps("App work completed.")}
