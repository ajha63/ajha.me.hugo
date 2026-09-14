# Infraestructura AWS con CDK

La infraestructura de produccion de `ajha.me` se define en `infra/cdk` con AWS
CDK v2 y Python. El stack se despliega en la cuenta `554982632606`, region
`us-east-1`, porque la Web ACL de CloudFront y el certificado ACM deben residir
en esa region.

## Recursos administrados

- Bucket privado `hugo-ajha-me`, con cifrado SSE-S3, versionado y bloqueo total
  de acceso publico.
- Distribucion CloudFront existente, actualizada para usar el bucket mediante
  Origin Access Control (OAC).
- Certificado ACM existente para `ajha.me`.
- WAF Web ACL `hugo-ajha-me` con reglas administradas de AWS en modo `Count`.
- CloudFront Function para resolver URLs Hugo como `/sobre-mi/` hacia
  `/sobre-mi/index.html` sin habilitar el website endpoint de S3.
- Roles IAM OIDC para GitHub Actions con confianza limitada al repositorio.

`Pay-As-You-Go` y `Single site configuration` son opciones comerciales o del
asistente de consola; no son propiedades configurables de CloudFormation. El
stack usa el comportamiento de pago por uso y una sola distribucion.

## Preparacion local

```bash
cd infra/cdk
/usr/bin/python3 -m venv .venv
source .venv/bin/activate
python -m pip install --requirement requirements-dev.txt
npm ci
```

La cuenta ya esta bootstrappeada con CDK. Para verificarla:

```bash
npx cdk bootstrap aws://554982632606/us-east-1 --profile alhernan
```

## Validacion

```bash
cd infra/cdk
source .venv/bin/activate
python -m pytest
npx cdk synth AjhaMeStack
npx cdk diff AjhaMeStack --profile alhernan
```

## Primer despliegue y migracion

El stack existente usa `ajha-me-site`. El nuevo codigo lo conserva con
`RemovalPolicy.RETAIN`, crea `hugo-ajha-me`, carga el build actual y solo despues
actualiza la distribucion. Esto evita cambiar CloudFront hacia un bucket vacio.

```bash
hugo --gc --minify --baseURL https://ajha.me/ \
  --cacheDir .hugo_cache

cd infra/cdk
source .venv/bin/activate
npx cdk deploy AjhaMeStack \
  --profile alhernan \
  --context include_site_content=true \
  --require-approval broadening
```

No elimines `ajha-me-site` durante la validacion. Primero confirma que todas las
rutas, imagenes y cabeceras funcionen desde `https://ajha.me`.

## Pipeline GitHub Actions

`.github/workflows/deploy-infrastructure.yml` ejecuta pruebas y `cdk synth` en
pull requests. Los cambios en `main` despliegan usando el environment `prod`,
que requiere aprobacion manual.

Variable requerida en el environment `prod`:

```text
AWS_ROLE_TO_ASSUME=arn:aws:iam::554982632606:role/AjhaMeCdkGitHubDeploy
```

El workflow del sitio usa el mismo rol para publicar en S3 e invalidar
CloudFront. Sus variables de produccion deben quedar asi:

```text
AWS_ACCOUNT_ID=554982632606
AWS_REGION=us-east-1
S3_BUCKET=hugo-ajha-me
SITE_BASE_URL=https://ajha.me/
CLOUDFRONT_DISTRIBUTION_ID=E1P9ZMYQ99M9A
```

## Activar bloqueo en WAF

El modo inicial es `Count`, recomendado para observar falsos positivos. Revisa
metricas y solicitudes muestreadas durante varios dias. Para activar bloqueo,
cambia cada `override_action` de `count` a `none`, ejecuta pruebas, revisa
`cdk diff` y despliega mediante el environment protegido `prod`.
