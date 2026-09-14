from pathlib import Path
from typing import Any

import aws_cdk as cdk
from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_wafv2 as wafv2,
)
from constructs import Construct


ACCOUNT_ID = "554982632606"
DOMAIN_NAME = "ajha.me"
CONTENT_BUCKET_NAME = "hugo-ajha-me"
LEGACY_BUCKET_NAME = "ajha-me-site"
CERTIFICATE_ARN = (
    "arn:aws:acm:us-east-1:554982632606:certificate/"
    "ba4af298-6b63-47dc-b08d-9a36efe1b40e"
)
GITHUB_OIDC_PROVIDER_ARN = (
    "arn:aws:iam::554982632606:oidc-provider/token.actions.githubusercontent.com"
)
GITHUB_REPOSITORY_SUBJECT = "repo:ajha63/ajha.me.hugo@1369952238"


class AjhaMeStack(cdk.Stack):
    """Production infrastructure for the ajha.me Hugo site."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # This resource already belongs to AjhaMeStack. Keep it during the
        # migration so the previous site remains recoverable.
        legacy_bucket = s3.Bucket(
            self,
            "SiteBucket",
            bucket_name=LEGACY_BUCKET_NAME,
            website_index_document="index.html",
            website_error_document="index.html",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        content_bucket = s3.Bucket(
            self,
            "ContentBucket",
            bucket_name=CONTENT_BUCKET_NAME,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            versioned=True,
            enforce_ssl=True,
            removal_policy=cdk.RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="ExpireOldObjectVersions",
                    noncurrent_version_expiration=cdk.Duration.days(30),
                )
            ],
        )

        web_acl = wafv2.CfnWebACL(
            self,
            "SiteWebACL",
            name="hugo-ajha-me",
            description="Managed protections for ajha.me in Count mode",
            scope="CLOUDFRONT",
            default_action=wafv2.CfnWebACL.DefaultActionProperty(allow={}),
            visibility_config=self._visibility_config("ajhaMeWebAcl"),
            rules=[
                self._managed_rule("AWSManagedRulesAmazonIpReputationList", 0),
                self._managed_rule("AWSManagedRulesCommonRuleSet", 1),
                self._managed_rule("AWSManagedRulesKnownBadInputsRuleSet", 2),
            ],
        )

        response_headers_policy = cloudfront.ResponseHeadersPolicy(
            self,
            "SecurityHeadersPolicy",
            response_headers_policy_name="AjhaMeStack-SecurityHeaders",
            security_headers_behavior=cloudfront.ResponseSecurityHeadersBehavior(
                content_type_options=cloudfront.ResponseHeadersContentTypeOptions(
                    override=True
                ),
                frame_options=cloudfront.ResponseHeadersFrameOptions(
                    frame_option=cloudfront.HeadersFrameOption.DENY,
                    override=True,
                ),
                referrer_policy=cloudfront.ResponseHeadersReferrerPolicy(
                    referrer_policy=(
                        cloudfront.HeadersReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN
                    ),
                    override=True,
                ),
                strict_transport_security=cloudfront.ResponseHeadersStrictTransportSecurity(
                    access_control_max_age=cdk.Duration.days(365),
                    include_subdomains=True,
                    preload=True,
                    override=True,
                ),
                xss_protection=cloudfront.ResponseHeadersXSSProtection(
                    protection=True,
                    mode_block=True,
                    override=True,
                ),
            ),
        )

        html_cache_policy = cloudfront.CachePolicy(
            self,
            "HtmlCachePolicy",
            cache_policy_name="AjhaMeStack-HtmlNoStore",
            comment="HTML revalidates on every request",
            default_ttl=cdk.Duration.seconds(0),
            min_ttl=cdk.Duration.seconds(0),
            max_ttl=cdk.Duration.days(1),
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True,
        )

        asset_cache_policy = cloudfront.CachePolicy(
            self,
            "AssetCachePolicy",
            cache_policy_name="AjhaMeStack-AssetLongLived",
            comment="Long-lived cache for fingerprinted static assets",
            default_ttl=cdk.Duration.days(365),
            min_ttl=cdk.Duration.days(1),
            max_ttl=cdk.Duration.days(365),
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True,
        )

        url_rewrite_function = cloudfront.Function(
            self,
            "HugoUrlRewriteFunction",
            function_name="hugo-ajha-me-url-rewrite",
            comment="Map Hugo directory URLs to index.html in private S3",
            runtime=cloudfront.FunctionRuntime.JS_2_0,
            code=cloudfront.FunctionCode.from_inline(
                """
function handler(event) {
  var request = event.request;
  var uri = request.uri;

  if (uri.endsWith('/')) {
    request.uri = uri + 'index.html';
  } else if (!uri.split('/').pop().includes('.')) {
    request.uri = uri + '/index.html';
  }

  return request;
}
""".strip()
            ),
        )

        origin_access_control = cloudfront.S3OriginAccessControl(
            self,
            "SiteOAC",
            origin_access_control_name="hugo-ajha-me-oac",
            description="Private S3 access for the ajha.me distribution",
            signing=cloudfront.Signing.SIGV4_ALWAYS,
        )
        s3_origin = origins.S3BucketOrigin.with_origin_access_control(
            content_bucket,
            origin_access_control=origin_access_control,
        )

        certificate = acm.Certificate.from_certificate_arn(
            self,
            "SiteCertificate",
            CERTIFICATE_ARN,
        )

        function_associations = [
            cloudfront.FunctionAssociation(
                event_type=cloudfront.FunctionEventType.VIEWER_REQUEST,
                function=url_rewrite_function,
            )
        ]

        distribution = cloudfront.Distribution(
            self,
            "SiteDistribution",
            comment="Hugo-ajha-me Personal web site.",
            default_root_object="index.html",
            domain_names=[DOMAIN_NAME],
            certificate=certificate,
            web_acl_id=web_acl.attr_arn,
            default_behavior=cloudfront.BehaviorOptions(
                origin=s3_origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD,
                cache_policy=html_cache_policy,
                response_headers_policy=response_headers_policy,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                function_associations=function_associations,
                compress=True,
            ),
            additional_behaviors={
                "css/*": cloudfront.BehaviorOptions(
                    origin=s3_origin,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                    cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD,
                    cache_policy=asset_cache_policy,
                    response_headers_policy=response_headers_policy,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    compress=True,
                ),
                "images/*": cloudfront.BehaviorOptions(
                    origin=s3_origin,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                    cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD,
                    cache_policy=asset_cache_policy,
                    response_headers_policy=response_headers_policy,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    compress=True,
                ),
            },
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=404,
                    response_page_path="/index.html",
                    ttl=cdk.Duration.seconds(0),
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=404,
                    response_page_path="/index.html",
                    ttl=cdk.Duration.seconds(0),
                ),
            ],
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            http_version=cloudfront.HttpVersion.HTTP2_AND_3,
            enable_ipv6=True,
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
        )

        self._add_github_roles(content_bucket, distribution)
        self._add_initial_site_deployment(content_bucket, distribution)

        cdk.CfnOutput(
            self,
            "BucketName",
            value=content_bucket.bucket_name,
            description="Private S3 content bucket",
            export_name="AjhaMeStack-BucketName",
        )
        cdk.CfnOutput(
            self,
            "BucketWebsiteUrl",
            value=legacy_bucket.bucket_website_url,
            description="Legacy bucket website endpoint retained for migration",
            export_name="AjhaMeStack-BucketWebsiteUrl",
        )
        cdk.CfnOutput(
            self,
            "DistributionId",
            value=distribution.distribution_id,
            description="CloudFront distribution ID",
            export_name="AjhaMeStack-DistributionId",
        )
        cdk.CfnOutput(
            self,
            "DistributionDomainName",
            value=distribution.distribution_domain_name,
            description="CloudFront distribution domain name",
            export_name="AjhaMeStack-DistributionDomainName",
        )
        cdk.CfnOutput(
            self,
            "WafWebAclArn",
            value=web_acl.attr_arn,
            description="CloudFront WAF Web ACL ARN in Count mode",
            export_name="AjhaMeStack-WafWebAclArn",
        )
        cdk.CfnOutput(
            self,
            "SiteUrl",
            value=f"https://{DOMAIN_NAME}",
            description="Public site URL",
        )
        cdk.CfnOutput(
            self,
            "GitHubDeployRoleArn",
            value=f"arn:aws:iam::{ACCOUNT_ID}:role/AjhaMeCdkGitHubDeploy",
            description="OIDC role used by GitHub Actions",
        )

    @staticmethod
    def _visibility_config(
        metric_name: str,
    ) -> wafv2.CfnWebACL.VisibilityConfigProperty:
        return wafv2.CfnWebACL.VisibilityConfigProperty(
            cloud_watch_metrics_enabled=True,
            metric_name=metric_name,
            sampled_requests_enabled=True,
        )

    @classmethod
    def _managed_rule(
        cls,
        name: str,
        priority: int,
    ) -> wafv2.CfnWebACL.RuleProperty:
        return wafv2.CfnWebACL.RuleProperty(
            name=name,
            priority=priority,
            override_action=wafv2.CfnWebACL.OverrideActionProperty(count={}),
            statement=wafv2.CfnWebACL.StatementProperty(
                managed_rule_group_statement=(
                    wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                        name=name,
                        vendor_name="AWS",
                    )
                )
            ),
            visibility_config=cls._visibility_config(f"{name}Metric"),
        )

    def _add_github_roles(
        self,
        content_bucket: s3.Bucket,
        distribution: cloudfront.Distribution,
    ) -> None:
        oidc_provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            self,
            "GitHubOidcProvider",
            GITHUB_OIDC_PROVIDER_ARN,
        )

        read_role = iam.Role(
            self,
            "GitHubReadRole",
            role_name="AjhaMeCdkGitHubRead",
            description="Read-only validation role for ajha.me",
            max_session_duration=cdk.Duration.hours(1),
            assumed_by=iam.WebIdentityPrincipal(
                oidc_provider.open_id_connect_provider_arn,
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                        "token.actions.githubusercontent.com:sub": (
                            f"{GITHUB_REPOSITORY_SUBJECT}:ref:refs/heads/main"
                        ),
                    }
                },
            ),
        )
        content_bucket.grant_read(read_role)

        deploy_role = iam.Role(
            self,
            "GitHubDeployRole",
            role_name="AjhaMeCdkGitHubDeploy",
            description="Production deploy role for ajha.me GitHub Actions",
            max_session_duration=cdk.Duration.hours(1),
            assumed_by=iam.WebIdentityPrincipal(
                oidc_provider.open_id_connect_provider_arn,
                conditions={
                    "StringEquals": {
                        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                        "token.actions.githubusercontent.com:sub": (
                            f"{GITHUB_REPOSITORY_SUBJECT}:environment:prod"
                        ),
                    }
                },
            ),
        )
        content_bucket.grant_read_write(deploy_role)
        distribution.grant_create_invalidation(deploy_role)
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="AssumeCdkBootstrapRoles",
                actions=["sts:AssumeRole"],
                resources=[f"arn:aws:iam::{ACCOUNT_ID}:role/cdk-hnb659fds-*"],
            )
        )
        deploy_role.add_to_policy(
            iam.PolicyStatement(
                sid="ReadCdkBootstrapVersion",
                actions=["ssm:GetParameter"],
                resources=[
                    f"arn:aws:ssm:us-east-1:{ACCOUNT_ID}:parameter/cdk-bootstrap/"
                    "hnb659fds/version"
                ],
            )
        )

    def _add_initial_site_deployment(
        self,
        content_bucket: s3.Bucket,
        distribution: cloudfront.Distribution,
    ) -> None:
        include_site_content = str(
            self.node.try_get_context("include_site_content") or "false"
        ).lower() in {"1", "true", "yes"}
        if not include_site_content:
            return

        site_path = Path(__file__).resolve().parents[3] / "public"
        if not (site_path / "index.html").is_file():
            raise ValueError(
                "public/index.html is required when include_site_content=true. "
                "Run Hugo before CDK deploy."
            )

        deployment = s3deploy.BucketDeployment(
            self,
            "InitialSiteDeployment",
            sources=[s3deploy.Source.asset(str(site_path))],
            destination_bucket=content_bucket,
            prune=False,
            retain_on_delete=True,
            memory_limit=512,
        )
        distribution.node.add_dependency(deployment)
