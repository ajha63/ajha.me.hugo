# Playbook: publicar nuevo post

## Objetivo

Crear, validar y promover un nuevo post del sitio `ajha.me` usando el flujo
`develop` -> `qa` -> `main`, con despliegues controlados a `dev`, `qa` y
`prod`.

Este playbook complementa:

- `docs/playbooks/deploy-dev.md`
- `docs/playbooks/deploy-qa.md`
- `docs/playbooks/deploy-prod.md`

## Ambientes y ramas

| Stage | Rama destino | URL esperada | Uso |
| --- | --- | --- | --- |
| `dev` | `develop` | `https://dev.ajha.me/` | Validacion temprana del post. |
| `qa` | `qa` | `https://qa.ajha.me/` | Revision editorial, funcional y visual. |
| `prod` | `main` | `https://ajha.me/` | Publicacion final aprobada. |

## Plantillas disponibles

El repositorio incluye un archetype especifico para posts:

```text
archetypes/posts/index.md
```

Hugo lo usa para crear cada articulo directamente como un page bundle. Esta es
la ruta oficial para posts nuevos; no copiar posts existentes salvo que se
necesite clonar deliberadamente una estructura especial.

```bash
hugo new content posts/slug-del-post
```

El archivo generado contiene esta metadata base:

```toml
+++
title = "Titulo derivado del slug"
date = "Fecha y hora RFC3339 generadas por Hugo"
draft = true
description = ""
tags = []
categories = []
+++
```

No definir `slug` en el front matter salvo que sea necesario conservar una URL
distinta al nombre del bundle. La ruta del directorio debe ser la fuente de
verdad para la URL del post.

Reglas:

1. Crear cada post como page bundle:

   ```text
   content/posts/slug-del-post/index.md
   ```

2. Usar un `slug` corto, estable y en minusculas, separado por guiones.
3. Mantener `draft = true` durante la preparacion inicial.
4. Cambiar a `draft = false` solo cuando el post este listo para solicitar
   promocion a QA o PROD, segun el flujo acordado.
5. Guardar imagenes propias del post dentro del mismo bundle cuando sean
   especificas del articulo.
6. Completar `description`, `tags` y, cuando aplique, `categories` antes de
   solicitar aprobacion.
7. No incluir secretos, credenciales, datos privados, screenshots sensibles ni
   placeholders editoriales.

## 1. Creacion de un nuevo post

1. Actualizar la rama base local:

   ```bash
   git switch develop
   git pull --ff-only
   ```

2. Crear una rama de trabajo:

   ```bash
   git switch -c post/slug-del-post
   ```

3. Crear el bundle con el archetype de posts:

   ```bash
   hugo new content posts/slug-del-post
   ```

   El resultado esperado es:

   ```text
   content/posts/slug-del-post/index.md
   ```

4. Editar el front matter:

   - `title`: titulo final o titulo de trabajo.
   - `date`: fecha local en formato ISO con zona horaria.
   - `draft`: `true` durante redaccion.
   - `description`: resumen claro, sin repetir el titulo.
   - `tags`: entre 2 y 5 etiquetas utiles.
   - `categories`: una categoria editorial cuando ayude a organizar el contenido.

5. Redactar el contenido del post en Markdown.
6. Ejecutar validacion local:

   ```bash
   hugo server --buildDrafts --navigateToChanged
   ```

7. Revisar localmente:

   - El post aparece en `/posts/` cuando se compila con drafts.
   - El titulo, fecha, descripcion y etiquetas son correctos.
   - Los enlaces internos y externos funcionan.
   - Las imagenes cargan correctamente.
   - No hay texto de prueba, notas internas o placeholders.

8. Ejecutar build:

   ```bash
   hugo --gc --minify
   ```

9. Revisar cambios antes de preparar el PR:

   ```bash
   git status --short
   git diff --check
   git diff --stat
   ```

## 2. Despliegue del nuevo post a DEV

1. Cambiar `draft = false` si el post debe verse en `dev` con el mismo
   comportamiento que tendra en ambientes superiores. Si solo se requiere una
   revision editorial temprana, documentar que el despliegue usa drafts.
2. Confirmar que el build local termina sin errores:

   ```bash
   hugo --gc --minify
   ```

3. Crear commit con alcance especifico:

   ```bash
   git add content/posts/slug-del-post
   git commit -m "Add post slug-del-post"
   ```

4. Abrir pull request desde `post/slug-del-post` hacia `develop`.
5. En el PR incluir:

   - Resumen del post.
   - Ruta creada.
   - Estado de `draft`.
   - Imagenes o assets agregados.
   - Validaciones ejecutadas.
   - Riesgos conocidos o puntos pendientes.

6. Confirmar que el job de validacion de Hugo pase correctamente.
7. Revisar y aprobar el PR hacia `develop`.
8. Hacer merge a `develop`.
9. Confirmar que GitHub Actions despliegue el stage `dev`.
10. Validar `https://dev.ajha.me/posts/slug-del-post/`.

Checklist DEV:

- El post carga por HTTPS.
- La pagina `/posts/` lista el articulo si `draft = false`.
- No hay errores visuales obvios en desktop ni movil.
- Metadata basica y descripcion se ven correctas.
- Las imagenes no exceden el peso razonable para web.
- El contenido coincide con el PR aprobado.

## 3. Peticion de aprobacion hacia QA

La promocion a QA se solicita con un PR de `develop` hacia `qa`.

1. Confirmar que `dev` fue validado.
2. Abrir PR `develop` -> `qa`.
3. En el PR documentar:

   - Link al PR original del post.
   - Link validado en `dev`.
   - Commit o SHA que se desea promover.
   - Checklist DEV completado.
   - Cambios esperados en contenido, assets y metadata.

4. Solicitar revision al responsable editorial o tecnico definido para QA.
5. No hacer merge a `qa` si hay comentarios bloqueantes, contenido incompleto o
   fallas de build.

## 4. Revision de peticiones en stage QA

El revisor de QA debe evaluar el PR `develop` -> `qa` antes de aprobarlo.

Revision del PR:

1. Confirmar que el diff solo contiene cambios esperados.
2. Revisar front matter del post:

   - `title`
   - `date`
   - `draft`
   - `description`
   - `tags`
   - `categories`

3. Revisar redaccion, ortografia, enlaces, imagenes y consistencia editorial.
4. Confirmar que el build de Hugo pasa.
5. Verificar que no se agregaron archivos generados como `public/` o
   `resources/_gen/`.
6. Revisar que no haya secretos, datos privados ni notas internas.

Decision QA:

- Aprobar si el post esta listo para validacion en `qa`.
- Pedir cambios si hay ajustes editoriales, visuales o tecnicos menores.
- Rechazar si el cambio no corresponde al alcance, rompe el sitio o expone
  informacion sensible.

Despues de aprobar:

1. Hacer merge del PR hacia `qa`.
2. Confirmar que GitHub Actions despliega el stage `qa`.
3. Validar `https://qa.ajha.me/posts/slug-del-post/`.

Checklist QA:

- El post carga en la URL esperada.
- El listado `/posts/` muestra el orden y resumen correctos.
- La navegacion hacia y desde el post funciona.
- La version movil no presenta cortes, solapamientos ni imagenes deformadas.
- Los enlaces externos abren correctamente.
- La fecha y etiquetas son correctas.
- La version en QA coincide con el commit aprobado.

## 5. Revision, aprobacion o rechazo desde stage PROD

La promocion a produccion se solicita con un PR de `qa` hacia `main`.

1. Confirmar que QA fue aprobado y desplegado.
2. Abrir PR `qa` -> `main`.
3. En el PR documentar:

   - URL validada en QA.
   - SHA o commit exacto a promover.
   - Resultado del checklist QA.
   - Impacto esperado en `https://ajha.me/`.
   - Plan de rollback.

4. Confirmar que el job de validacion de Hugo pasa.
5. El owner o aprobador de produccion revisa:

   - Diff completo del PR.
   - Post publicado en QA.
   - Archivos agregados o modificados.
   - Estado final de `draft`.
   - Riesgo de SEO, contenido o reputacion.
   - Alcance del despliegue.

Decision PROD:

- Aprobar el PR si el contenido esta listo para publicarse.
- Pedir cambios si hay ajustes no bloqueantes que deben corregirse antes de
  publicar.
- Rechazar el PR si el contenido no debe publicarse, el alcance cambio sin
  aprobacion, la build falla, QA no fue validado o existe riesgo de exponer
  informacion sensible.

Despues de aprobar:

1. Hacer merge a `main`.
2. Aprobar el deployment del environment `prod` cuando GitHub lo solicite.
3. Confirmar que finalicen la sincronizacion S3 y la invalidacion CloudFront.
4. Validar `https://ajha.me/posts/slug-del-post/`.

Checklist PROD:

- `https://ajha.me/` carga correctamente.
- `https://ajha.me/posts/slug-del-post/` carga por HTTPS.
- `/posts/` muestra el articulo.
- No hay contenido en borrador publicado accidentalmente.
- Las imagenes cargan desde CloudFront.
- La version publicada coincide con el commit aprobado.
- El sitemap refleja el nuevo contenido despues del build.

## Rollback

Usar rollback si el post publicado en PROD tiene errores criticos.

1. Identificar el commit estable anterior en `main`.
2. Crear un PR de reversa o un commit que corrija el contenido.
3. Promover el cambio por el mismo flujo `qa` -> `main` cuando el tiempo lo
   permita.
4. Si el impacto es urgente, usar el deploy manual a `prod` documentado en
   `docs/playbooks/deploy-prod.md`.
5. Validar que CloudFront ya no sirva la version defectuosa.
6. Registrar causa, correccion y hora de cierre.

## Criterio de cierre

La publicacion se considera cerrada cuando:

1. El post esta fusionado en `main`.
2. El deployment de `prod` termino sin errores.
3. CloudFront sirve la version nueva.
4. La URL final fue validada.
5. El aprobador de produccion confirma aceptacion o cierre.
