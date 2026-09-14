# ajha.me

Sitio personal para **[ajha.me](https://ajha.me/)**, desarrollado con [Hugo](https://gohugo.io/) y preparado para publicarse como sitio estatico en AWS usando Amazon S3 y Amazon CloudFront.

El objetivo del sitio es presentar el perfil profesional de AJHA, documentar experiencia, ofrecer servicios y publicar contenido sobre cloud computing, operaciones TI, soporte, automatizacion, DevOps e inteligencia artificial aplicada.

## Estado del proyecto

Este repositorio ya contiene una base funcional de Hugo:

- Configuracion principal en `hugo.toml`.
- Contenido inicial en `content/`.
- Layouts propios en `layouts/`, sin depender todavia de un tema externo.
- Estilos base en `assets/css/main.css`.
- Un primer post en borrador en `content/posts/primer-post/index.md`.

## Referencias analizadas

### hmartinez.info: estructura adoptada

El sitio [hmartinez.info](https://hmartinez.info/) funciona como referencia estructural para un sitio personal profesional. La estructura que conviene adoptar para ajha.me es:

- **Inicio:** propuesta personal clara, areas de enfoque, metricas o pilares.
- **Sobre mi:** perfil profesional y contexto.
- **Experiencia:** proyectos, areas de especialidad y logros.
- **Servicios:** formas concretas de colaboracion.
- **Posts / Insights:** publicaciones tecnicas y reflexivas.
- **Contacto:** canales profesionales y llamada a conversar.

No se busca copiar contenido ni identidad visual; solo usar una arquitectura de informacion similar por su claridad.

### escala24x7.com: fuentes y colores adoptados

Del sitio [escala24x7.com](https://escala24x7.com/) se toma solo la direccion visual de fuentes y colores:

- Titulares: `Nexa`, con fallback a `Infra`, `Arial`, `sans-serif`.
- Texto base: `Infra`, con fallback a `Arial`, `sans-serif`.
- Colores principales:
  - Azul profundo: `#041e42`
  - Fondo oscuro: `#08192b`
  - Acento teal: `#00c19f`
  - Azul link/acento: `#0a4aa5`
  - Texto principal: `#1a1a1a`
  - Texto secundario: `#33475b`
  - Fondo claro: `#f5f8fa`
  - Lineas suaves: `#dbdcdd`

Nota: si se quieren usar exactamente `Nexa` e `Infra`, hay que incorporar archivos de fuente con licencia valida. Mientras tanto, el CSS deja esos nombres configurados y usa fallbacks seguros.

### Imagen de referencia para Posts / Insights

El banner editorial de **Posts / Insights** esta en `assets/images/editorial/posts-insights-reader-banner.png`.

- Imagen fuente: `1672 x 941 px`.
- Peso fuente: `1,509,715 bytes` aproximados, equivalente a `1.51 MB` decimal o `1.44 MiB`.
- Version publicada por Hugo: `1440 x 560 px` en formato WebP.
- Peso publicado actual: `42,866 bytes`, equivalente a `42 KB` aproximados.
- Proporcion usada en el sitio: `18:7`, pensada para banner ancho.
- Resolucion minima recomendada para reemplazos: `1440 x 560 px`.
- Mejor resolucion recomendada: `2880 x 1120 px` para cubrir pantallas retina y permitir compresion WebP/AVIF sin perder nitidez.
- Peso recomendado para la version publicada: idealmente menor a `150 KB`; aceptable hasta `250 KB` si la imagen requiere mas detalle.

Para futuras imagenes, conviene conservar espacio visual limpio hacia el lado izquierdo o centro, evitar texto incrustado y mantener la paleta azul profundo, teal, blanco y grises frios.

## Buenas practicas Hugo aplicadas

La implementacion sigue recomendaciones actuales de Hugo:

- La organizacion de `content/` refleja la estructura final de URLs del sitio.
- Las paginas de seccion usan `_index.md` cuando representan listados o secciones.
- Los articulos pueden vivir como page bundles (`content/posts/nombre/index.md`) para que imagenes y recursos queden junto al contenido.
- `assets/` se usa para CSS procesado por Hugo Pipes.
- `public/` y `resources/_gen/` se tratan como salida generada y estan ignorados por Git.
- `hugo server` se usa para desarrollo local con LiveReload.
- `hugo --gc --minify` debe usarse para builds de produccion.

Referencias:

- https://gohugo.io/getting-started/directory-structure/
- https://gohugo.io/content-management/organization/
- https://gohugo.io/getting-started/usage/
- https://gohugo.io/host-and-deploy/deploy-with-hugo-deploy/

## Estructura del proyecto

```text
.
├── assets/
│   └── css/
│       └── main.css
├── content/
│   ├── _index.md
│   ├── contacto/
│   ├── experiencia/
│   ├── posts/
│   ├── servicios/
│   └── sobre-mi/
├── layouts/
│   ├── _default/
│   │   ├── baseof.html
│   │   ├── list.html
│   │   └── single.html
│   └── index.html
├── hugo.toml
└── README.md
```

## Desarrollo local

Verificar instalacion:

```bash
hugo version
```

Levantar servidor local:

```bash
hugo server --navigateToChanged
```

Generar build de produccion:

```bash
hugo --gc --minify
```

El resultado se genera en `public/`.

## Publicacion en AWS

Arquitectura recomendada:

- Bucket S3 privado `hugo-ajha-me` para almacenar el contenido generado.
- CloudFront como punto publico de entrada.
- Origin Access Control (OAC) para que el bucket no sea publico.
- Certificado ACM en `us-east-1` para `ajha.me`.
- Route 53 apuntando el dominio a la distribucion CloudFront.
- AWS WAF con reglas administradas inicialmente en modo `Count`.
- Politicas de cache y compresion administradas por CloudFront.

Hugo ya tiene configurado un target inicial:

```toml
[deployment]
  [[deployment.targets]]
    name = 'production'
    url = 's3://hugo-ajha-me?region=us-east-1'
```

Cuando las credenciales de AWS esten configuradas y el bucket exista:

```bash
hugo --gc --minify
hugo deploy --target production --invalidateCDN
```

La infraestructura se administra con AWS CDK v2 y Python desde `infra/cdk`.
El playbook completo, incluida la migracion desde el bucket anterior, esta en
`docs/aws/infrastructure-cdk.md`.

## Pipeline GitHub Actions

Repositorio remoto creado:

- https://github.com/ajha63/ajha.me.hugo
- Visibilidad: `public`

El pipeline esta definido en `.github/workflows/deploy-hugo-aws.yml` y usa tres stages:

- `dev`: despliegue desde la rama `develop`.
- `qa`: despliegue desde la rama `qa`.
- `prod`: despliegue desde la rama `main`.

Tambien permite ejecucion manual con `workflow_dispatch`, seleccionando `dev`, `qa` o `prod`.

Documentacion operativa:

- `docs/aws/github-actions-oidc.md`
- `docs/aws/infrastructure-cdk.md`
- `docs/playbooks/deploy-dev.md`
- `docs/playbooks/deploy-qa.md`
- `docs/playbooks/deploy-prod.md`

## Proximos pasos

- Definir nombre completo, bio final y canales de contacto.
- Reemplazar textos base por contenido profesional definitivo.
- Agregar fotografia o recurso visual propio.
- Crear posts iniciales en `content/posts/`.
- Ajustar SEO: metadata social, favicon, `robots.txt` y sitemap.
- Provisionar los ambientes AWS de `dev` y `qa` cuando se definan sus dominios.
