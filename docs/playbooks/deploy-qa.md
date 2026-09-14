# Playbook: deploy a qa

## Objetivo

Publicar una version candidata en `qa` antes de promover a produccion.

## Preparacion inicial

1. Crear o confirmar el bucket S3 de qa, por ejemplo `ajha-me-qa`.
2. Crear o confirmar la distribucion CloudFront de qa, por ejemplo `qa.ajha.me`.
3. Crear el GitHub Environment `qa`.
4. Configurar variables del environment:

```text
AWS_ACCOUNT_ID=<id-de-la-cuenta-aws>
AWS_REGION=us-east-1
AWS_ROLE_TO_ASSUME=arn:aws:iam::<id-de-la-cuenta-aws>:role/ajha-me-hugo-qa-github-actions
S3_BUCKET=ajha-me-qa
SITE_BASE_URL=https://qa.ajha.me/
CLOUDFRONT_DISTRIBUTION_ID=<id-cloudfront-qa>
```

5. En GitHub Environment `qa`, restringir deployments a la rama `qa`.
6. En AWS IAM, crear el rol `ajha-me-hugo-qa-github-actions` con la trust policy `environment:qa`.
7. Adjuntar al rol una policy limitada al bucket y distribucion de qa.

## Promocion desde dev

1. Confirmar que `develop` ya fue validado en `dev`.
2. Abrir pull request de `develop` hacia `qa`.
3. Revisar contenido, navegacion, assets y cambios visuales.
4. Confirmar que el job `Validate Hugo build` pase correctamente.
5. Hacer merge a `qa`.
6. GitHub Actions ejecutara el deploy al environment `qa`.
7. Validar `https://qa.ajha.me/`.

## Deploy manual

1. Entrar al repositorio `ajha63/ajha.me.hugo`.
2. Ir a **Actions**.
3. Seleccionar **Deploy Hugo site to AWS**.
4. Elegir **Run workflow**.
5. Seleccionar `stage=qa`.
6. Ejecutar el workflow.
7. Revisar que la build use `SITE_BASE_URL=https://qa.ajha.me/`.

## Checklist de validacion

1. Comparar el contenido contra dev y confirmar que solo incluye cambios esperados.
2. Revisar enlaces internos y externos.
3. Verificar responsive en desktop y movil.
4. Confirmar imagenes optimizadas en WebP.
5. Revisar que CloudFront sirva la version nueva despues de la invalidacion.
6. Registrar hallazgos antes de promover a produccion.
