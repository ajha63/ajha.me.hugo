# Playbook: deploy a dev

## Objetivo

Publicar cambios de integracion temprana en el ambiente `dev`.

## Preparacion inicial

1. Crear o confirmar el bucket S3 de dev, por ejemplo `ajha-me-dev`.
2. Crear o confirmar la distribucion CloudFront de dev, por ejemplo `dev.ajha.me`.
3. Crear el GitHub Environment `dev`.
4. Configurar variables del environment:

```text
AWS_ACCOUNT_ID=<id-de-la-cuenta-aws>
AWS_REGION=us-east-1
AWS_ROLE_TO_ASSUME=arn:aws:iam::<id-de-la-cuenta-aws>:role/ajha-me-hugo-dev-github-actions
S3_BUCKET=ajha-me-dev
SITE_BASE_URL=https://dev.ajha.me/
CLOUDFRONT_DISTRIBUTION_ID=<id-cloudfront-dev>
```

5. En GitHub Environment `dev`, restringir deployments a la rama `develop`.
6. En AWS IAM, crear el rol `ajha-me-hugo-dev-github-actions` con la trust policy `environment:dev`.
7. Adjuntar al rol una policy limitada al bucket y distribucion de dev.

## Deploy automatico

1. Crear una rama de trabajo desde `develop`.
2. Hacer cambios en contenido, estilos o layouts.
3. Abrir pull request hacia `develop`.
4. Confirmar que el job `Validate Hugo build` pase correctamente.
5. Hacer merge a `develop`.
6. GitHub Actions ejecutara el deploy al environment `dev`.
7. Validar `https://dev.ajha.me/`.

## Deploy manual

1. Entrar al repositorio `ajha63/ajha.me.hugo`.
2. Ir a **Actions**.
3. Seleccionar **Deploy Hugo site to AWS**.
4. Elegir **Run workflow**.
5. Seleccionar `stage=dev`.
6. Ejecutar el workflow.
7. Confirmar que la invalidacion de CloudFront termine sin errores.

## Checklist de validacion

1. La home carga sin errores.
2. Las paginas `/sobre-mi/`, `/experiencia/`, `/servicios/`, `/posts/` y `/contacto/` responden.
3. Las imagenes se ven correctamente.
4. No hay contenido de prueba accidental.
5. El sitemap y `robots.txt` existen.
