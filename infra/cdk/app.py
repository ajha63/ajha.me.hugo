#!/usr/bin/env python3

import aws_cdk as cdk

from ajha_me_infra.stack import AjhaMeStack


ACCOUNT_ID = "554982632606"
PRIMARY_REGION = "us-east-1"


app = cdk.App()

stack = AjhaMeStack(
    app,
    "AjhaMeStack",
    env=cdk.Environment(account=ACCOUNT_ID, region=PRIMARY_REGION),
    description="ajha.me static site - S3, CloudFront, OAC and WAF",
    termination_protection=True,
)

cdk.Tags.of(stack).add("Project", "ajha.me")
cdk.Tags.of(stack).add("ManagedBy", "aws-cdk")
cdk.Tags.of(stack).add("Environment", "prod")

app.synth()
