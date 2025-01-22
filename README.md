# benchling_pubchem
A benchling app that utilizes the pubchem API to grab molecules and smiles and unicorns.

## App Structure
The app is organized into a main app, `local_app`, that is built in a Docker container and loaded onto Lambda. This 
app rips a bunch off from [this Benchling tutorial app](https://github.com/benchling/app-examples-python/tree/main/examples/chem-sync-local-flask), but with some key additions:
* instead of environmental variables for app secrets, it uses `boto3` to grab AWS secrets instead
* the main Flask server in `local_app/app.py` is replaced with the Lambda standard logic, which uses a `handler()` app to process an `event`.

__Importantly__ there is a _second_ Lambda function that calls the above mentioned lambda function. This second Lambda function, `benchling_pubchem_starter.py`, is there to immediately acknowledge Benchling with a 200 code, and call the actual `benchling_pubchem` lambda function. Benchling has a 3 second timer for it to receive an OK, so this dual-Lambda setup allows for fast acknowledgement and still maintains a nicely contained container for the actual Benchling app and PubChem logic.

## Installation
Some steps are abbreviated for brevity.
1. Create a AWS ECR registry for the Dockerfile we're about to create.
2. If you have the AWS CLI, use it to login to Docker 
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ***.dkr.ecr.us-east-1.amazonaws.com
```
3. Clone the repo using `git clone git@github.com:Arkea-Bio-Corp/benchling_pubchem.git`, update `local_app/benchling_app/views/constants.py` with the necessary constants for your cloud environment.
4. Build, tag, and upload to your image to the ECR registry created above:
```
docker build -t new_registry . 
docker tag new_registry:latest ***.dkr.ecr.us-east-1.amazonaws.com/new_registry:latest 
docker push ***.dkr.ecr.us-east-1.amazonaws.com/new_registry:latest
```
5. Create a Lambda function, and use the new registry image as its base.
6. Create a _second_ Lambda function, and copy in the contents of `benchling_pubchem_starter.py`. No additional layers are necessary. Specify your first lambda function by name on line 12. Create a URL in Lambda for this function.
7. Adjust your Lambda permissions to allow function two (`starter`) to invoke function one (`benchling_pubchem`).
8. Create a secret in AWS Secrets Manager, and set it up to work with the secret pulling in `local_app/benchling_app/setup.py`.
9. Create your secret with the necessary info from Benchling.
10. Use the `manifest.yaml` to create the app in your Benchling tenant.
11. Add the URL created above to your Benchling tenant app webhook field.
12. A test of the webhook should return an all green 200!

Create a canvas in a notebook and specify the PubChem search app to utilize it..
