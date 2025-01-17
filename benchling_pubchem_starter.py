import json
import boto3

client = boto3.client("lambda")


def lambda_handler(event, context):
    # this lambda function calls the other lambda function, which is created by the
    # Dockerfile in this root dir.

    response = client.invoke(
        FunctionName="benchling_pubchem",
        # payload MUST be bytes, so encode the dictionary we get from event and pass
        # along to our other benchling Lambda function.
        Payload=json.dumps(event, indent=2).encode("utf-8"),
        InvocationType="Event",
    )

    return {  # ACK a 200 to Benchling as fast as possible
        "statusCode": 200,
        "body": json.dumps("payload sent to benchling_pubchem lambda function"),
    }
