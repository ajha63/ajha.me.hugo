# Playbook: deploy a prod

## Objetivo

Publicar la version final en `https://ajha.me/`.

## Preparacion inicial

1. Confirmar el bucket S3 de produccion `hugo-ajha-me`.
2. Mantener el bucket S3 privado.
3. Crear una distribucion CloudFront con Origin Access Control hacia el bucket.
4. Crear certificado ACM en `us-east-1` para `ajha.me`.
5. Configurar DNS en Route 53 apuntando `ajha.me` a CloudFront.
6. Crear el GitHub Environment `prod`.
7. Configurar variables del environment:

```text
AWS_ACCOUNT_ID=554982632606
AWS_REGION=us-east-1
AWS_ROLE_TO_ASSUME=arn:aws:iam::554982632606:role/AjhaMeCdkGitHubDeploy
S3_BUCKET=hugo-ajha-me
SITE_BASE_URL=https://ajha.me/
CLOUDFRONT_DISTRIBUTION_ID=E1P9ZMYQ99M9A
```

8. En GitHub Environment `prod`, restringir deployments a la rama `main`.
9. Confirmar que `prod` requiere aprobacion del usuario `ajha63` antes de desplegar y que el bypass de administradores esta deshabilitado.
10. En AWS IAM, confirmar el rol `AjhaMeCdkGitHubDeploy` con la trust policy `environment:prod`.
11. Adjuntar al rol una policy limitada al bucket y distribucion de produccion.

## Promocion desde qa

1. Confirmar que `qa` fue validado funcional y visualmente.
2. Abrir pull request de `qa` hacia `main`.
3. Revisar diferencias de contenido, imagenes, metadata y configuracion.
4. Confirmar que el job `Validate Hugo build` pase correctamente.
5. Aprobar el pull request.
6. Hacer merge a `main`.
7. Aprobar el deployment del environment `prod` cuando GitHub lo solicite.
8. Esperar a que finalice la sincronizacion S3 y la invalidacion CloudFront.
9. Validar `https://ajha.me/`.

## Deploy manual

1. Usar deploy manual a `prod` solo para recuperacion o publicacion controlada.
2. Entrar al repositorio `ajha63/ajha.me.hugo`.
3. Ir a **Actions**.
4. Seleccionar **Deploy Hugo site to AWS**.
5. Elegir **Run workflow**.
6. Seleccionar `stage=prod`.
7. Aprobar el environment `prod`.
8. Confirmar que la version publicada corresponde al commit esperado.

## Checklist de validacion

1. `https://ajha.me/` carga con HTTPS valido.
2. Home, Sobre mi, Experiencia, Servicios, Posts y Contacto responden.
3. Las imagenes cargan desde CloudFront.
4. `sitemap.xml` y `robots.txt` estan disponibles.
5. No hay borradores publicados.
6. El contenido final no incluye placeholders.
7. La distribucion CloudFront no sirve una version anterior despues de la invalidacion.

## Rollback

1. Identificar el ultimo commit estable en `main`.
2. Crear un revert commit o volver a promover el commit estable.
3. Ejecutar el workflow de `prod`.
4. Validar `https://ajha.me/` despues de la invalidacion.
