import json

from functools import cache
from boto3 import session as bt3sess
from botocore.exceptions import ClientError

from benchling_sdk.apps.framework import App
from benchling_sdk.auth.client_credentials_oauth2 import ClientCredentialsOAuth2
from benchling_sdk.benchling import Benchling
from benchling_sdk.models.webhooks.v0 import WebhookEnvelopeV0


def init_app_from_webhook(webhook: WebhookEnvelopeV0) -> App:
    return App(webhook.app.id, _benchling_from_webhook(webhook))


@cache
def get_secret():
    """Use AWS Secrets to get app details"""
    secret_name = "prod/benchling_pubchem"
    region_name = "us-east-1"

    session = bt3sess.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    return json.loads(get_secret_value_response["SecretString"])


@cache
def app_definition_id() -> str:
    # App definition ID is available to "global" apps. It uniquely identifies the Benchling App
    # above the tenant context.
    app_def_id = get_secret()["APP_DEFINITION_ID"]
    assert app_def_id is not None, "Missing APP_DEFINITION_ID from environment"
    return app_def_id


def _benchling_from_webhook(webhook: WebhookEnvelopeV0) -> Benchling:
    return Benchling(webhook.base_url, _auth_method())


@cache
def _auth_method() -> ClientCredentialsOAuth2:
    client_id = get_secret()["CLIENT_ID"]
    assert client_id is not None, "Missing CLIENT_ID from environment"
    client_secret = _client_secret_from_file()
    return ClientCredentialsOAuth2(client_id, client_secret)


def _client_secret_from_file() -> str:
    client_secret = get_secret()["CLIENT_SECRET"]
    assert client_secret is not None, "Missing CLIENT_SECRET from environment"
    return client_secret
