import aws_cdk as cdk
from aws_cdk.assertions import Match, Template

from ajha_me_infra.stack import AjhaMeStack


def synth_template() -> Template:
    app = cdk.App(context={"include_site_content": "false"})
    stack = AjhaMeStack(
        app,
        "AjhaMeStack",
        env=cdk.Environment(account="554982632606", region="us-east-1"),
    )
    return Template.from_stack(stack)


def test_private_content_bucket() -> None:
    template = synth_template()

    template.has_resource_properties(
        "AWS::S3::Bucket",
        {
            "BucketName": "hugo-ajha-me",
            "BucketEncryption": Match.any_value(),
            "OwnershipControls": {
                "Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]
            },
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True,
            },
            "VersioningConfiguration": {"Status": "Enabled"},
        },
    )


def test_cloudfront_distribution_settings() -> None:
    template = synth_template()

    template.has_resource_properties(
        "AWS::CloudFront::Distribution",
        {
            "DistributionConfig": Match.object_like(
                {
                    "Aliases": ["ajha.me"],
                    "Comment": "Hugo-ajha-me Personal web site.",
                    "DefaultRootObject": "index.html",
                    "Enabled": True,
                    "HttpVersion": "http2and3",
                    "IPV6Enabled": True,
                    "PriceClass": "PriceClass_100",
                    "WebACLId": Match.any_value(),
                }
            )
        },
    )


def test_waf_rules_are_in_count_mode() -> None:
    template = synth_template()

    template.has_resource_properties(
        "AWS::WAFv2::WebACL",
        {
            "Name": "hugo-ajha-me",
            "Scope": "CLOUDFRONT",
            "Rules": Match.array_with(
                [
                    Match.object_like(
                        {
                            "Name": "AWSManagedRulesCommonRuleSet",
                            "OverrideAction": {"Count": {}},
                        }
                    )
                ]
            ),
        },
    )


def test_github_deploy_role_uses_exact_environment_subject() -> None:
    template = synth_template()

    template.has_resource_properties(
        "AWS::IAM::Role",
        {
            "RoleName": "AjhaMeCdkGitHubDeploy",
            "AssumeRolePolicyDocument": {
                "Statement": Match.array_with(
                    [
                        Match.object_like(
                            {
                                "Condition": {
                                    "StringEquals": {
                                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                                        "token.actions.githubusercontent.com:sub": (
                                            "repo:ajha63@560156/ajha.me.hugo@1369952238:"
                                            "environment:prod"
                                        ),
                                    }
                                }
                            }
                        )
                    ]
                )
            },
        },
    )
