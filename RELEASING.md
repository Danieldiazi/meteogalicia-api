# Publicar una versión en PyPI

El workflow `.github/workflows/publish.yml` publica el paquete al publicar una
release estable en GitHub. Usa Trusted Publishing (OIDC), sin tokens de PyPI
guardados como secretos.

## Configuración inicial (una sola vez)

1. En [Settings → Environments](https://github.com/Danieldiazi/meteogalicia-api/settings/environments),
   crea un entorno llamado `pypi`. Si quieres revisar cada publicación antes de
   subirla, añade tu usuario como required reviewer.
2. En [PyPI → meteogalicia-api → Publishing](https://pypi.org/manage/project/meteogalicia-api/settings/publishing/),
   añade un Trusted Publisher de tipo GitHub con estos valores:

   | Campo | Valor |
   | --- | --- |
   | Owner | `Danieldiazi` |
   | Repository name | `meteogalicia-api` |
   | Workflow name | `publish.yml` |
   | Environment name | `pypi` |

   Workflow name es el nombre del archivo, sin `.github/workflows/`.
   No necesitas crear un proyecto nuevo ni un API token.
3. Integra los cambios del workflow en `main` antes de crear la release.

## Publicar cada nueva versión

1. Integra en `main` los cambios que quieres distribuir.
2. Cambia `VERSION` en `setup.py` a una versión nueva (por ejemplo,
   `0.1.3`) y guarda el cambio en `main`.
3. Comprueba que los tests de GitHub Actions pasan.
4. Abre [Releases → Draft a new release](https://github.com/Danieldiazi/meteogalicia-api/releases/new).
5. Crea una etiqueta nueva `v0.1.3` apuntando al commit de `main` que contiene
   ese cambio. El prefijo `v` es obligatorio y el número debe coincidir con
   `VERSION` en `setup.py`.
6. Escribe el título y las notas de la versión. No marques la opción de
   prerelease si quieres publicarla en PyPI. Pulsa **Publish release**.
7. En [Actions](https://github.com/Danieldiazi/meteogalicia-api/actions),
   revisa **Publish to PyPI**. Si has configurado un required reviewer en
   `pypi`, aprueba el despliegue.
8. Comprueba que la nueva versión aparece en
   [PyPI](https://pypi.org/project/meteogalicia-api/).

El workflow ejecuta los tests, construye un wheel y un archivo fuente,
valida sus metadatos y comprueba la coincidencia entre etiqueta y versión.
Solo después los publica. El job de publicación recibe el permiso OIDC;
el job que ejecuta el código y construye el paquete no lo recibe.

Las pull requests ejecutan la comprobación y construcción, pero no publican.
Los borradores y los pushes tampoco publican. Las prereleases publicadas
se validan y construyen, pero no se suben a PyPI.

## Si falla

- **La etiqueta no coincide:** corrige la versión o crea la release con la
  etiqueta correcta. Reejecutar el workflow no cambia el código de una etiqueta.
- **Trusted Publisher no encontrado:** comprueba los cuatro valores anteriores,
  incluido `publish.yml` y el entorno `pypi`.
- **Archivo ya existente:** PyPI no permite sustituir archivos ya publicados;
  utiliza una nueva versión para publicar código modificado.
- **Fallo temporal antes de subir los archivos:** usa **Re-run failed jobs**.
  Si la subida fue parcial, comprueba primero qué archivos aparecen en PyPI.

Esta configuración no cambia por sí misma la versión de `setup.py` ni crea
una release.
