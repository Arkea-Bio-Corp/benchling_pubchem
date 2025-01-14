import json

from benchling_sdk.apps.helpers.webhook_helpers import verify
from local_app.benchling_app.handler import handle_webhook
from local_app.benchling_app.setup import app_definition_id
from local_app.lib.logger import get_logger

logger = get_logger()


def handler(event, context):
    # For security, don't do anything else without first verifying the webhook
    app_def_id = app_definition_id()

    # Important! To verify webhooks, we need to pass the body as an unmodified string
    # Flask's request.data is bytes, so decode to string. Passing bytes or JSON won't work
    verify(app_def_id, event, event["headers"])

    logger.debug("Received webhook message: %s", event["body"])

    handle_webhook(event)
    return {"statusCode": 200, "body": json.dumps("we did it")}
