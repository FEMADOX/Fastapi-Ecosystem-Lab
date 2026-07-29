# Clean Architecture: plan de commits, ramas y pull requests

Instrucciones operativas para modelos AI pequenos. Este documento describe
como repartir el worktree mixto entre las ramas existentes de `auth`, `items`
y `users`, crear commits Conventional Commits y abrir PRs secuenciales a
`main`.

## Objetivo

Publicar la migracion sin:

- mezclar cambios de aplicaciones en una misma rama;
- perder el worktree actual;
- duplicar commits que ya estan en `main`;
- crear PRs entre ramas de feature;
- usar `rebase`, force-push, `reset --hard` o `stash pop`;
- abrir el siguiente PR antes de fusionar el anterior.

Todos los PRs tienen como base `main`.

## Estado verificado el 2026-07-28

- La rama activa es `main`.
- El worktree contiene cambios mezclados de `auth`, `items`, `users`, `shared`
  y `sse`.
- `origin/main` y `main` apuntan al mismo commit.
- Las tres ramas existen en local y origin:
  - `refactor/auth-clean-architecture`
  - `refactor/items-clean-architecture`
  - `refactor/users-clean-architecture`
- Ninguna rama tiene commits unicos respecto a `main`.
- Las ramas solo estan atrasadas:
  - auth: 4 commits;
  - items: 7 commits;
  - users: 1 commit.

Esta condicion permite actualizarlas con `merge --ff-only`. Si cambia, el
agente debe detenerse.

## Reglas para todos los agentes

1. Ejecutar un solo agente de publicacion a la vez. Todos comparten el mismo
   worktree y el indice Git.
2. Prefijar todos los comandos de shell con `rtk`.
3. Antes de tocar una rama, ejecutar:

   ```powershell
   rtk git status --short
   rtk git branch --show-current
   rtk git fetch origin --prune
   ```

4. No usar `git add .` ni `git add -A`, excepto para crear el snapshot inicial.
5. En commits normales, hacer staging con paths explicitos.
6. No modificar codigo durante la distribucion. El snapshot es la fuente de
   verdad. Si una rama necesita correcciones, detenerse y reportarlas.
7. No hacer merge de un PR sin autorizacion explicita del usuario.
8. No continuar con la siguiente rama hasta que el PR anterior este fusionado
   y `origin/main` lo contenga.
9. Usar `.gitmessage` para commits y
   `.github/pull_request_template.md` para PRs.
10. Despues de cada commit, comprobar que no quedan cambios fuera del scope:

    ```powershell
    rtk git status --short
    rtk git show --stat --oneline HEAD
    ```

11. Antes de crear un PR, comprobar autenticacion y PRs existentes:

    ```powershell
    rtk gh auth status
    rtk gh pr list --state open --head <nombre-de-rama>
    ```

    Si ya existe un PR, no crear otro. Reportar su URL.

## Fase 0: snapshot recuperable

Esta fase la ejecuta solamente el agente coordinador.

### Precondiciones

```powershell
rtk git switch main
rtk git status --short
rtk git diff --check
rtk git diff --cached --check
rtk git diff --name-status
rtk git diff --cached --name-status
```

Detenerse si:

- aparece un `.env`, secreto, credencial o archivo generado;
- `main` no es la rama activa;
- hay conflictos sin resolver;
- `git diff --check` reporta errores dentro de archivos de la migracion.

### Crear snapshot

```powershell
rtk git switch -c wip/clean-architecture-publish-snapshot-2026-07-28
rtk git add -A
rtk git diff --cached --name-status
rtk git commit -m "chore(wip): snapshot clean architecture migration"
rtk git status --short
rtk git rev-parse HEAD
```

El agente debe guardar el hash mostrado por `git rev-parse HEAD`.

No abrir PR desde esta rama. No borrarla hasta que los tres PRs hayan sido
fusionados. No es necesario subirla a origin; hacerlo requiere autorizacion
explicita del usuario.

En los comandos siguientes se usa:

```powershell
$SnapshotBranch = "wip/clean-architecture-publish-snapshot-2026-07-28"
```

No usar `git stash`: el repositorio ya tiene historial de stash y mezclarlo
haria la recuperacion mas ambigua.

## Orden obligatorio

```text
auth PR -> merge a main
        -> items PR -> merge a main
                    -> users PR -> merge a main
```

La razon es que auth publica primero la base compartida:
`AuthenticatedAccount`, `CurrentActor`, `PasswordHasher`, `Clock`, JSON types
y verificacion JWT. Items y users consumen esas abstracciones.

## Fase 1: rama y PR de auth

### Verificar que la rama no tiene trabajo unico

```powershell
rtk git switch main
rtk git pull --ff-only origin main
rtk git rev-list --left-right --count main...refactor/auth-clean-architecture
```

El resultado esperado tiene `0` a la derecha, por ejemplo `4 0`. Si el segundo
numero no es cero, detenerse: la rama contiene commits no integrados.

### Actualizar la rama

```powershell
rtk git switch refactor/auth-clean-architecture
rtk git merge --ff-only main
```

### Restaurar solo el scope de auth y su foundation compartida

```powershell
$SnapshotBranch = "wip/clean-architecture-publish-snapshot-2026-07-28"

rtk git restore --source $SnapshotBranch --staged --worktree -- `
  learn_fastapi/src/auth `
  learn_fastapi/src/shared/application/dto.py `
  learn_fastapi/src/shared/application/security.py `
  learn_fastapi/src/shared/infrastructure/argon2_password_hasher.py `
  learn_fastapi/src/shared/infrastructure/json_types.py `
  learn_fastapi/src/shared/infrastructure/system_clock.py `
  learn_fastapi/src/shared/presentation/dependencies.py `
  learn_fastapi/src/users/domain/value_objects.py `
  learn_fastapi/src/sse `
  learn_fastapi/src/index.py `
  learn_fastapi/tests/unit/auth `
  learn_fastapi/tests/v1/auth/conftest.py `
  learn_fastapi/tests/v2/auth/conftest.py `
  learn_fastapi/tests/v1/items/conftest.py `
  learn_fastapi/tests/v1/users/test_router.py `
  learn_fastapi/tests/v1/sse/test_sse.py
```

Los tests de items/users/sse pertenecen a este PR porque dejan de importar
`auth.utils` o deben usar `AuthenticatedAccount`.

### Commit

Revisar primero:

```powershell
rtk git status --short
rtk git diff --check
rtk git diff --stat
```

No deben aparecer `learn_fastapi/src/items/**` ni
`learn_fastapi/src/users/**`, salvo `users/domain/value_objects.py` y los
tests compartidos enumerados.

```powershell
rtk git add -- `
  learn_fastapi/src/auth `
  learn_fastapi/src/shared/application/dto.py `
  learn_fastapi/src/shared/application/security.py `
  learn_fastapi/src/shared/infrastructure/argon2_password_hasher.py `
  learn_fastapi/src/shared/infrastructure/json_types.py `
  learn_fastapi/src/shared/infrastructure/system_clock.py `
  learn_fastapi/src/shared/presentation/dependencies.py `
  learn_fastapi/src/users/domain/value_objects.py `
  learn_fastapi/src/sse `
  learn_fastapi/src/index.py `
  learn_fastapi/tests/unit/auth `
  learn_fastapi/tests/v1/auth/conftest.py `
  learn_fastapi/tests/v2/auth/conftest.py `
  learn_fastapi/tests/v1/items/conftest.py `
  learn_fastapi/tests/v1/users/test_router.py `
  learn_fastapi/tests/v1/sse/test_sse.py

rtk git diff --cached --name-status
rtk git commit -m "refactor(auth): complete clean architecture boundaries"
```

### Validacion

```powershell
rtk uv run ruff check learn_fastapi
rtk uv run ruff format --check learn_fastapi
rtk uv run ty check learn_fastapi
$env:DEBUG = "True"
rtk uv run pytest --config-file=pyproject.toml
```

Todos deben pasar. No abrir PR con checks rojos.

### Push y PR

```powershell
rtk git push origin refactor/auth-clean-architecture
```

Titulo:

```text
[learn_fastapi] Complete auth clean architecture migration
```

Crear el body desde `.github/pull_request_template.md`. Marcar:

- FastAPI backend/API;
- Refactor;
- Authentication, authorization, cookies, or security behavior changed;
- los cuatro checks FastAPI;
- external services mocked or isolated.

Resumen minimo:

- mueve login, refresh, logout y registro a use cases;
- reemplaza helpers legacy por ports/adapters;
- retorna `AuthenticatedAccount` desde `CurrentUserDep`;
- elimina `auth/service.py` y `auth/utils.py`;
- migra SSE al boundary de presentation.

Crear y verificar:

```powershell
rtk gh pr create `
  --base main `
  --head refactor/auth-clean-architecture `
  --title "[learn_fastapi] Complete auth clean architecture migration" `
  --body-file C:\tmp\pr-auth-clean-architecture.md

rtk gh pr view --json number,url,title,baseRefName,headRefName,state
```

Detenerse y reportar URL, commit y checks. Esperar merge.

## Gate 1: auth debe estar fusionado

El siguiente agente ejecuta:

```powershell
rtk git switch main
rtk git pull --ff-only origin main
rtk git branch --contains refactor/auth-clean-architecture
```

Continuar solo si `main` contiene el commit de auth.

## Fase 2: rama y PR de items

### Actualizar rama

```powershell
rtk git rev-list --left-right --count main...refactor/items-clean-architecture
rtk git switch refactor/items-clean-architecture
rtk git merge --ff-only main
```

El segundo numero del `rev-list` debe ser cero.

### Restaurar scope

```powershell
$SnapshotBranch = "wip/clean-architecture-publish-snapshot-2026-07-28"

rtk git restore --source $SnapshotBranch --staged --worktree -- `
  learn_fastapi/src/items `
  learn_fastapi/src/cache/redis_client.py `
  learn_fastapi/README.md
```

### Commit

```powershell
rtk git status --short
rtk git diff --check
rtk git add -- `
  learn_fastapi/src/items `
  learn_fastapi/src/cache/redis_client.py `
  learn_fastapi/README.md
rtk git diff --cached --name-status
rtk git commit -m "refactor(items): complete clean architecture migration"
```

El commit debe:

- inyectar cache, eventos e image storage mediante ports;
- mover schemas/mappers/dependencies a presentation;
- hacer que el router invoque use cases;
- eliminar `items/service.py`, `items/cache.py` e `items/repository.py`.

### Validacion, push y PR

Ejecutar los cuatro checks FastAPI y la suite completa igual que en auth.

```powershell
rtk git push origin refactor/items-clean-architecture
```

Titulo:

```text
[learn_fastapi] Complete items clean architecture migration
```

En el PR marcar Refactor y Media/file upload behavior changed. Explicar cache,
eventos SSE, Cloudinary y eliminacion legacy. Crear el body a partir de la
plantilla y verificar el PR con `rtk gh pr view`.

```powershell
rtk gh pr create `
  --base main `
  --head refactor/items-clean-architecture `
  --title "[learn_fastapi] Complete items clean architecture migration" `
  --body-file C:\tmp\pr-items-clean-architecture.md

rtk gh pr view --json number,url,title,baseRefName,headRefName,state
```

Esperar merge antes de users.

## Gate 2: items debe estar fusionado

```powershell
rtk git switch main
rtk git pull --ff-only origin main
rtk git branch --contains refactor/items-clean-architecture
```

Continuar solo si `main` contiene el commit de items.

## Fase 3: rama y PR de users

### Actualizar rama

```powershell
rtk git rev-list --left-right --count main...refactor/users-clean-architecture
rtk git switch refactor/users-clean-architecture
rtk git merge --ff-only main
```

El segundo numero del `rev-list` debe ser cero.

### Restaurar scope

```powershell
$SnapshotBranch = "wip/clean-architecture-publish-snapshot-2026-07-28"

rtk git restore --source $SnapshotBranch --staged --worktree -- `
  learn_fastapi/src/users `
  learn_fastapi/src/utils/service.py `
  learn_fastapi/tests/unit/users `
  learn_fastapi/docs/clean-architecture-git-publish-plan.md `
  learn_fastapi/docs/clean-architecture-migration-plan.md `
  learn_fastapi/docs/clean-architecture-next-steps.md `
  .gitignore
```

`utils/service.py` se elimina en esta ultima rama porque, tras eliminar los
services de auth/items/users, ya no tiene consumidores.

### Commit de codigo

```powershell
rtk git status --short
rtk git diff --check
rtk git add -- `
  learn_fastapi/src/users `
  learn_fastapi/src/utils/service.py `
  learn_fastapi/tests/unit/users
rtk git diff --cached --name-status
rtk git commit -m "refactor(users): complete clean architecture migration"
```

### Commit de documentacion

```powershell
rtk git add -- `
  learn_fastapi/docs/clean-architecture-git-publish-plan.md `
  learn_fastapi/docs/clean-architecture-migration-plan.md `
  learn_fastapi/docs/clean-architecture-next-steps.md `
  .gitignore
rtk git diff --cached --name-status
rtk git commit -m "docs(architecture): record clean migration progress"
```

El codigo debe:

- mover autorizacion y password verification a application;
- publicar eventos desde use cases;
- usar `AuthenticatedAccount` en presentation;
- eliminar `users/service.py` y `users/repository.py`;
- cubrir permisos, password incorrecto y actualizacion admin con fakes.

### Validacion, push y PR

Ejecutar los cuatro checks FastAPI y la suite completa.

```powershell
rtk git push origin refactor/users-clean-architecture
```

Titulo:

```text
[learn_fastapi] Complete users clean architecture migration
```

Marcar Refactor, Tests y Authentication/authorization behavior changed. El
body debe destacar el fix donde un admin ahora modifica el `user_id` objetivo
y no su propia cuenta.

```powershell
rtk gh pr create `
  --base main `
  --head refactor/users-clean-architecture `
  --title "[learn_fastapi] Complete users clean architecture migration" `
  --body-file C:\tmp\pr-users-clean-architecture.md

rtk gh pr view --json number,url,title,baseRefName,headRefName,state
```

Esperar merge.

## Fase 4: verificacion final

Despues de fusionar los tres PRs:

```powershell
rtk git switch main
rtk git pull --ff-only origin main
rtk git status --short
rtk uv run ruff check learn_fastapi
rtk uv run ruff format --check learn_fastapi
rtk uv run ty check learn_fastapi
$env:DEBUG = "True"
rtk uv run pytest --config-file=pyproject.toml
rtk rg -n "auth\.utils|auth\.service|items\.service|items\.cache|items\.repository|users\.service|users\.repository" learn_fastapi/src learn_fastapi/tests
```

Resultados esperados:

- worktree limpio;
- Ruff, formato y `ty` sin errores;
- 99 o mas tests pasando;
- `rg` sin coincidencias y exit code 1, que significa "no encontrado".

Solo despues de esta verificacion se puede borrar la rama snapshot:

```powershell
rtk git branch -d wip/clean-architecture-publish-snapshot-2026-07-28
```

No usar `-D` salvo autorizacion explicita.

## Condiciones de parada

Un agente pequeno debe detenerse y pedir ayuda cuando:

- una rama tiene commits unicos a la derecha en `rev-list`;
- `merge --ff-only` falla;
- aparecen conflictos;
- faltan archivos del snapshot;
- un path fuera del ownership aparece staged;
- cualquier check falla;
- `gh pr create` indica que ya existe un PR abierto;
- `main` no contiene el PR anterior;
- el snapshot no existe o su hash no coincide con el registrado.

El agente debe reportar comando, salida relevante, rama actual y
`rtk git status --short`. No debe intentar arreglos destructivos.

## Formato de reporte de cada agente

```text
Rama:
Base main:
Snapshot usado:
Commit(s):
Archivos fuera de scope: ninguno / lista
Ruff:
Formato:
Ty:
Pytest:
Push:
PR:
Estado final del worktree:
Bloqueos o riesgos:
```

## Prompts para delegar

### Agente coordinador

```text
Lee learn_fastapi/docs/clean-architecture-git-publish-plan.md.
Ejecuta solamente la Fase 0. No distribuyas cambios ni abras PRs.
Reporta el hash del snapshot y confirma que el worktree quedo limpio.
Detente ante cualquier condicion de parada.
```

### Agente auth

```text
Lee learn_fastapi/docs/clean-architecture-git-publish-plan.md.
Confirma que existe el snapshot y ejecuta solamente Fase 1.
No edites codigo, no uses paths fuera del ownership de auth y no hagas merge
del PR. Reporta commit, checks y URL.
```

### Agente items

```text
Lee learn_fastapi/docs/clean-architecture-git-publish-plan.md.
Verifica Gate 1 y ejecuta solamente Fase 2.
No continues si auth no esta en main. No hagas merge del PR.
Reporta commit, checks y URL.
```

### Agente users

```text
Lee learn_fastapi/docs/clean-architecture-git-publish-plan.md.
Verifica Gate 2 y ejecuta solamente Fase 3.
No continues si items no esta en main. No hagas merge del PR.
Reporta commits, checks y URL.
```

### Agente verificador

```text
Lee learn_fastapi/docs/clean-architecture-git-publish-plan.md.
Ejecuta solamente Fase 4 de forma read-only, excepto el borrado opcional del
snapshot, que requiere autorizacion explicita. Reporta todos los resultados.
```
