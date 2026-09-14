# GitHub Actions OIDC para AWS

Este proyecto debe publicar `ajha.me` desde GitHub Actions hacia buckets S3 privados, exponiendo el sitio por CloudFront. La recomendacion es usar **OIDC** en lugar de access keys permanentes.

Repositorio creado:

- URL: `https://github.com/ajha63/ajha.me.hugo`
- Visibilidad: `public`
- Owner login: `ajha63`
- Owner ID: `560156`
- Repository ID: `1369952238`

## Variables por GitHub Environment

Crear tres GitHub Environments: `dev`, `qa` y `prod`.

Estado actual en GitHub:

- `dev`, `qa` y `prod` ya fueron creados en `ajha63/ajha.me.hugo`.
- `dev` tiene politica de deployment limitada a la rama `develop`.
- `qa` tiene politica de deployment limitada a la rama `qa`.
- `prod` tiene politica de deployment limitada a la rama `main`.
- `prod` requiere aprobacion del usuario `ajha63` antes de desplegar y no permite bypass de administradores.

Cada environment debe tener estas variables:

```text
AWS_ACCOUNT_ID=554982632606
AWS_REGION=us-east-1
AWS_ROLE_TO_ASSUME=<arn-del-rol-del-stage>
S3_BUCKET=<bucket-del-stage>
SITE_BASE_URL=https://<host-del-stage>/
CLOUDFRONT_DISTRIBUTION_ID=<id-cloudfront-del-stage>
```

`CLOUDFRONT_DISTRIBUTION_ID` puede omitirse si ese stage todavia no tiene distribucion CloudFront.

## Modelo de ambientes

| Stage | Rama sugerida | URL sugerida | Bucket sugerido |
| --- | --- | --- | --- |
| `dev` | `develop` | `https://dev.ajha.me/` | `ajha-me-dev` |
| `qa` | `qa` | `https://qa.ajha.me/` | `ajha-me-qa` |
| `prod` | `main` | `https://ajha.me/` | `hugo-ajha-me` |

Produccion usa el rol administrado por CDK:

```text
AWS_ROLE_TO_ASSUME=arn:aws:iam::554982632606:role/AjhaMeCdkGitHubDeploy
S3_BUCKET=hugo-ajha-me
CLOUDFRONT_DISTRIBUTION_ID=E1P9ZMYQ99M9A
```

## Trust policy OIDC

Crear un rol IAM distinto por stage. Como el repositorio fue creado despues del 15 de julio de 2026, usar el formato inmutable de GitHub OIDC con owner ID y repository ID.

### Dev

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:ajha63@560156/ajha.me.hugo@1369952238:environment:dev"
        }
      }
    }
  ]
}
```

### QA

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:ajha63@560156/ajha.me.hugo@1369952238:environment:qa"
        }
      }
    }
  ]
}
```

### Prod

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<AWS_ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:ajha63@560156/ajha.me.hugo@1369952238:environment:prod"
        }
      }
    }
  ]
}
```

## Permissions policy por rol

Usar una policy por stage, cambiando `<S3_BUCKET>` y `<CLOUDFRONT_DISTRIBUTION_ID>`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListTargetBucket",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::<S3_BUCKET>"
    },
    {
      "Sid": "PublishStaticSiteObjects",
      "Effect": "Allow",
      "Action": [
        "s3:DeleteObject",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::<S3_BUCKET>/*"
    },
    {
      "Sid": "InvalidateCloudFront",
      "Effect": "Allow",
      "Action": "cloudfront:CreateInvalidation",
      "Resource": "arn:aws:cloudfront::<AWS_ACCOUNT_ID>:distribution/<CLOUDFRONT_DISTRIBUTION_ID>"
    }
  ]
}
```

Si un stage no usa CloudFront todavia, no agregues el statement `InvalidateCloudFront`.

## Buenas practicas aplicadas

- OIDC en vez de credenciales AWS permanentes.
- Un rol IAM separado por stage.
- Un bucket y una distribucion CloudFront separados por stage.
- `permissions` minimo en GitHub Actions: `contents: read` y `id-token: write` solo en el job que despliega.
- GitHub Environments para separar variables, aprobaciones y reglas de ramas.
- Politicas de ramas por environment: `develop`, `qa` y `main`.
- Validacion de build en pull requests antes de desplegar.
- Version fija de Hugo.
- Descarga de Hugo con verificacion SHA256.
- `allowed-account-ids` para evitar asumir credenciales de una cuenta AWS inesperada.
- `concurrency` para evitar despliegues simultaneos al mismo stage.
- Dependabot habilitado para actualizar acciones de GitHub.
