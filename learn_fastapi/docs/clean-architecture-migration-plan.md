# Clean Architecture: plan de migracion completo

Estado auditado el 2026-07-27. Complementa `clean-architecture-next-steps.md`.

La publicacion por ramas, commits y PRs se documenta en
`clean-architecture-git-publish-plan.md`.

## Progreso de implementacion

| Bloque | Estado | Resultado |
| ------ | ------ | --------- |
| PR 1 - Eventos de items | Completo | Todos los eventos se publican desde use cases |
| PR 2 - CurrentUser sin ORM | Completo | `CurrentUserDep` retorna `AuthenticatedAccount` |
| PR 3 - Auth sin service | Completo | Router, cookies y use cases reemplazaron `auth/service.py` |
| PR 4 - Users sin service | Completo | Autorizacion y password se verifican en application |
| PR 5 - Legacy de items | Completo | Eliminados service, cache y repository legacy |
| PR 6 - Legacy de auth | Completo | Eliminados service y utils legacy |
| PR 7 - Legacy de users | Completo | Eliminados service y repository legacy |
| PR 8 - Tests unitarios | En progreso | Auth tokens y autorizacion de cuentas tienen fakes |
| PR 9 - Payload SSE seguro | Completo | `UsersEventRecord` no contiene `password_hash` |

La siguiente fase es ampliar los tests unitarios de application y domain hasta
cubrir todos los casos criticos descritos en PR 8.

## Regla de dependencias

```
presentation -> application -> domain
infrastructure -> application -> domain
```

El dominio y application **no** deben importar FastAPI, SQLAlchemy, Redis,
Cloudinary, modelos ORM ni excepciones HTTP.

---

## Estado actual por modulo

### items

| Capa | Estado | Observaciones |
| ------ | -------- | --------------- |
| domain | Completo | Entidades, value objects, errores, `ItemsRepository` port |
| application | ~90 % | Use cases, commands, queries, DTOs, ports (`ItemsCache`, `ItemsEventPublisher`, `ImageStorage`, `ImageUpload`) |
| infrastructure | Completo | `SQLAlchemyItemsRepository`, `RedisItemCache`, `CloudinaryImageStorage`, `SSEItemEventPublisher` |
| presentation | ~80 % | Router, schemas, mappers, dependencies. Todavia delega en `ItemsService` |

**Violaciones pendientes:**

- `application/use_cases.py:36-38` importa `image_filename_required_exception` desde `shared.presentation.exceptions`.
- `service.py` recibe `users.models.User` (ORM) en `delete_item()` y `update_item_image()`.
- `service.py:397` publica `item_image_updated` desde el servicio en vez del use case `UpdateItemImageUseCase`.
- `presentation/router.py:16` importa `invalidate_items_namespace` desde el legacy `items/cache.py` y lo ejecuta en `BackgroundTasks` tras cada escritura.
- `presentation/mappers.py:7` importa `users.models.User` para `current_actor_from_user`.

**Archivos legacy activos:**

- `items/service.py` — fachada principal del router.
- `items/repository.py` — repositorio ORM viejo.
- `items/cache.py` — cache viejo que opera sobre `ItemSchema` y `User` ORM.

### auth

| Capa | Estado | Observaciones |
| ------ | -------- | --------------- |
| domain | Completo | Entidades, errores, `AuthRepository` port |
| application | Completo | Use cases, commands, queries, DTOs, ports (`AccessTokenIssuer`, `RefreshTokenGenerator`, `RefreshTokenHasher`, `PasswordHasher`, `Clock`, `AuthEventPublisher`) |
| infrastructure | Completo | `PyJWTAccessTokenIssuer`, `SecretsRefreshTokenGenerator`, `Argon2RefreshTokenHasher`, `SQLAlchemyAuthRepository`, `SSEAuthEventPublisher` |
| presentation | ~60 % | Router, schemas, dependencies. El router delega en `AuthService` que mezcla HTTP |

**Violaciones pendientes:**

- `service.py` importa `OAuth2PasswordRequestForm`, `Request`, `Response`.
- `service.py._login()` recibe `Response` y llama `set_auth_cookies()`.
- `service.py.refresh_token()` lee cookies desde `Request`.
- `service.py.logout()` recibe `User` ORM, `Request`, `Response`, y llama `clear_auth_cookies()`.
- Todos los eventos (`auth_registered`, `auth_logged_in`, `auth_logged_out`) se publican desde el servicio, no desde use cases.
- `service.py.register()` recibe el schema `UserCreate` de presentation.

**Archivos legacy activos:**

- `auth/service.py` — fachada principal con fuerte acoplamiento HTTP.
- `auth/utils.py` — funciones de hashing y cookies duplicadas parcialmente por los adapters de infrastructure.

### users

| Capa | Estado | Observaciones |
| ------ | -------- | --------------- |
| domain | Completo | Entidades, value objects, errores, `UsersRepository` port |
| application | ~85 % | Use cases, commands, queries, DTOs, ports (`UsersEventPublisher`). El `PasswordHasher` se inyecta bien |
| infrastructure | Completo | `SQLAlchemyUsersRepository`, `SSEUsersEventPublisher`, mappers |
| presentation | ~70 % | Router, schemas, mappers, dependencies |

**Violaciones pendientes:**

- `service.py` recibe `users.models.User` (ORM) en todos los metodos publicos.
- `service.py:100` llama `verify_password` directamente desde `auth.utils` en vez del port `PasswordHasher`.
- `service.py:176` convierte ORM a dominio inline (`persisted_user_from_orm(authorized_user)`).
- `service.py:179` llama `clear_auth_cookies(response)` — acoplamiento HTTP.
- Eventos (`account_updated`, `account_deleted`) se publican desde el servicio.

**Archivos legacy activos:**

- `users/service.py` — fachada principal, recibe ORM y Response.
- `users/repository.py` — repositorio ORM viejo (usado por `shared/presentation/dependencies.py`).

### shared

| Capa | Estado | Observaciones |
| ------ | -------- | --------------- |
| domain | Completo | Value objects (`UserId`, `ItemId`, `RefreshTokenId`) |
| application | Completo | `PasswordHasher` y `Clock` protocols |
| infrastructure | Completo | `Argon2PasswordHasher`, `SystemClock`, `json_types` |
| presentation | Parcial | `dependencies.py` usa repositorio y modelos ORM legacy |

**Violaciones pendientes:**

- `shared/presentation/dependencies.py` (`get_current_user`) importa `users.models.User`, `users.repository.UsersRepository` (legacy), `auth.utils.verify_access_token` (legacy).
- `CurrentUserDep` retorna un `User` ORM que se propaga a todos los routers y servicios.

### sse

| Capa | Estado | Observaciones |
|------|--------|---------------|
| presentation | Completo | Router migrado a `sse/presentation/router.py` |
| manager | Estable | `sse_manager` no necesita cambios |

### Tests

| Ambito | Estado |
| -------- | -------- |
| HTTP integration (v1/v2) | Existen para auth, items, users, sse |
| Unit application | Solo `tests/unit/auth/test_token_use_cases.py` (2 tests) |
| Unit domain | No existen |

---

## Plan de migracion por PR

### PR 1 — Cerrar el ultimo evento de items en el use case

**Objetivo:** Todo evento de `items` se publica unicamente desde use cases.

**Archivos:**

- `items/application/use_cases.py` — `UpdateItemImageUseCase.execute()`: publicar `item_image_updated` despues de la persistencia exitosa (ya no en el servicio).
- `items/service.py` — eliminar la llamada `self.event_publisher.item_image_updated(item)` de `update_item_image()`. Eliminar `event_publisher` del constructor de `ItemsService` si ya no se usa.
- `items/presentation/dependencies.py` — dejar de pasar `SSEItemEventPublisher()` al constructor de `ItemsService` si ya no lo necesita.

**Tambien:** Eliminar la importacion de `image_filename_required_exception` desde `application/use_cases.py:36-38`. Esa excepcion de presentation debe lanzarse desde el servicio o el router al capturar `InvalidImageUploadError` del use case.

**Validacion:**

```bash
uv run ruff check learn_fastapi
uv run ruff format --check learn_fastapi
uv run ty check learn_fastapi
uv run pytest --config-file=pyproject.toml
```

---

### PR 2 — Reemplazar `CurrentUserDep` ORM por entidad de dominio

**Objetivo:** Ningun router ni servicio reciba `users.models.User` como argumento.

**Motivacion:** `CurrentUserDep` es la raiz del problema. Retorna un `User` ORM que se propaga por toda la aplicacion. Resolverlo primero desbloquea todas las demas migraciones.

**Archivos:**

1. **Crear `CurrentActor` compartido** en `shared/application/dto.py`:

   ```python
   @dataclass(frozen=True, slots=True)
   class CurrentActor:
       id: UserId
       is_superuser: bool
   ```

   (Reemplaza o extiende el `CurrentActor` que ya existe en `items/application/dto.py`)

2. **Crear `AuthenticatedAccount`** en `shared/application/dto.py`:

   ```python
   @dataclass(frozen=True, slots=True)
   class AuthenticatedAccount:
       id: UserId
       email: str
       password_hash: PasswordHash
       is_active: bool
       is_superuser: bool
   ```

   Para los casos de uso de `users` y `auth` que necesitan mas que solo `id` e `is_superuser`.

3. **Migrar `shared/presentation/dependencies.py`:**
   - Reemplazar `users.repository.UsersRepository` (legacy) por `SQLAlchemyUsersRepository` (clean) + mapper.
   - Retornar `AuthenticatedAccount` en vez de `User` ORM.
   - Actualizar `CurrentUserDep` al nuevo tipo.

4. **Actualizar todos los consumidores** de `CurrentUserDep`:
   - `items/presentation/router.py` — convertir `AuthenticatedAccount` a `CurrentActor` en el router.
   - `items/presentation/mappers.py` — `current_actor_from_user` recibe `AuthenticatedAccount` en vez de `UserModel`.
   - `items/service.py` — reemplazar `User` por `CurrentActor` o `AuthenticatedAccount`.
   - `auth/service.py` — `logout()` recibe `AuthenticatedAccount` en vez de `User`.
   - `auth/presentation/router.py` — sin cambios (ya pasa `current_user` opaco al servicio).
   - `users/service.py` — reemplazar `UserModel` por `AuthenticatedAccount`.
   - `users/presentation/router.py` — adaptar `get_me()` para construir `UserResponse` desde `AuthenticatedAccount`.

5. **Eliminar** `items/application/dto.py` (`CurrentActor` local), mover importaciones al shared.

**Validacion:** misma suite.

---

### PR 3 — Mover logica HTTP de `auth/service.py` a presentation

**Objetivo:** `AuthService` devuelve resultados de aplicacion; presentation construye la respuesta HTTP y las cookies.

**Archivos:**

1. **Crear `LoginUseCase` compuesto** (o refactorizar `_login` en el servicio) que reciba `LoginCommand` y devuelva un DTO de resultado:

   ```python
   @dataclass(frozen=True, slots=True)
   class LoginResult:
       access_token: str
       access_expires_in: int
       refresh_token_raw: str
       refresh_expires_in: int
       user_id: UserId
   ```

   El CSRF token es un concepto de presentation (cookie), no de application.

2. **Crear `RefreshTokenUseCase`** que reciba `refresh_token_raw` (string) y devuelva `RefreshedAccessToken`. Actualmente `AuthService.refresh_token()` lee cookies desde `Request` — eso debe moverse al router.

3. **Crear `LogoutUseCase`** que reciba `owner_id` y `refresh_token_raw` y revoque el token. Actualmente `AuthService.logout()` lee cookies desde `Request`.

4. **Migrar `auth/presentation/router.py`:**
   - `login()` extrae credenciales del form, llama al use case, genera `csrf_token`, llama `set_auth_cookies()`, construye `Token`.
   - `refresh_token()` lee cookies, valida CSRF, llama al use case, construye `Token`.
   - `logout()` lee cookies, llama al use case, llama `clear_auth_cookies()`.

5. **Publicar eventos desde use cases** (no desde el servicio):
   - `auth_registered` → desde `RegisterUseCase` (que recibe `AuthEventPublisher` como port).
   - `auth_logged_in` → desde `LoginUseCase` compuesto.
   - `auth_logged_out` → desde `LogoutUseCase`.

6. **`auth/service.py`** se puede eliminar (o vaciar) cuando el router no lo necesite.

**Validacion:** misma suite.

---

### PR 4 — Limpiar `users/service.py`

**Objetivo:** Eliminar el servicio de users; los routers llaman directamente a los use cases.

**Archivos:**

1. **Mover `verify_userid_and_auth_user` a un use case** o descomponerlo:
   - La verificacion del owner ya se puede hacer comparando `AuthenticatedAccount.id` vs `user_id` en presentation.
   - La verificacion de password debe usar el port `PasswordHasher` (no `auth.utils.verify_password`).

2. **Crear use cases faltantes** si hiciera falta:
   - `GetAccountUseCase` — busca por id, verifica permisos.
   - `DeleteAccountUseCase` — verifica permisos, elimina, publica evento.

3. **Publicar eventos desde use cases:**
   - `account_updated` → desde `UpdateUserUseCase`.
   - `account_deleted` → desde `DeleteAccountUseCase`.

4. **Migrar `users/presentation/router.py`** para inyectar use cases directamente.

5. **Eliminar** `users/service.py`.

6. **Eliminar** la importacion de `clear_auth_cookies` desde users (eso es responsabilidad de auth/presentation).

**Validacion:** misma suite.

---

### PR 5 — Eliminar legacy de items

**Objetivo:** Ningun router depende de los archivos legacy.

**Archivos a migrar/eliminar:**

1. **`items/service.py`** — el router debe inyectar use cases directamente:
   - Mover la conversion de schemas a domain (`_item_from_update_schema`) a `presentation/mappers.py`.
   - Mover el mapeo de excepciones domain→HTTP al router.
   - Eliminar el servicio.

2. **`items/cache.py`** — ya existe `infrastructure/cache.py` (`RedisItemCache`):
   - Eliminar `invalidate_items_namespace` del router. La invalidacion ya se hace en los use cases via `self.cache.invalidate_all()`.
   - Eliminar `BackgroundTasks` de las rutas de escritura (la invalidacion ya es sincrona en el use case).

3. **`items/repository.py`** — ya existe `infrastructure/repository.py` (`SQLAlchemyItemsRepository`):
   - Verificar que ningun import lo referencia.
   - Eliminar.

4. **Actualizar `items/presentation/router.py`:**
   - Inyectar use cases individuales o un dataclass de use cases.
   - Convertir `AuthenticatedAccount` → `CurrentActor` en el router.
   - Mapear excepciones de dominio a HTTP en el router o con un exception handler.

**Validacion:** misma suite + verificar que el router sigue devolviendo las mismas respuestas HTTP.

---

### PR 6 — Eliminar legacy de auth

**Objetivo:** `auth/utils.py` ya no contiene funciones usadas directamente.

**Archivos:**

1. **`auth/utils.py`:**
   - `hash_password` / `verify_password` → reemplazados por `Argon2PasswordHasher` en shared/infrastructure.
   - `verify_access_token` / `decode_access_token` → mover a un adapter en `auth/infrastructure/` o en `shared/presentation/dependencies.py` usar el port `AccessTokenIssuer` con un metodo `verify()`.
   - `set_auth_cookies` / `clear_auth_cookies` → ya estan en presentation scope. Mover a `auth/presentation/cookies.py` si no se hizo en PR 3.

2. **`auth/service.py`** — eliminar si PR 3 ya lo vacio.

3. **`shared/presentation/dependencies.py`** — `verify_access_token` debe usar el adapter de infrastructure, no la funcion libre de `auth/utils.py`.

**Validacion:** misma suite.

---

### PR 7 — Eliminar legacy de users

**Objetivo:** Ningun import referencia `users/repository.py` (legacy) ni `users/models.py` directamente fuera de infrastructure.

**Archivos:**

1. **`users/repository.py`** — ya existe `infrastructure/repository.py`:
   - `shared/presentation/dependencies.py` es el ultimo consumidor (ya migrado en PR 2).
   - Eliminar.

2. **`users/models.py`** — el modelo ORM solo debe importarse desde:
   - `users/infrastructure/repository.py`
   - `users/infrastructure/mappers.py`
   - Verificar que no hay importaciones desde services, routers ni application.

3. **`items/models.py`** — solo debe importarse desde `items/infrastructure/`.

4. **`auth/models.py`** — solo debe importarse desde `auth/infrastructure/`.

**Validacion:** misma suite + `grep -r "users.models" learn_fastapi/src` no debe mostrar hits fuera de infrastructure.

---

### PR 8 — Tests unitarios de application

**Objetivo:** Cada use case tiene al menos un test con fakes.

**Estructura:**

```
tests/unit/
  items/
    domain/
      test_entities.py       # Item.total_price, Item.is_owned_by, Item.has_image
    application/
      test_list_items.py     # cache hit no consulta repo, cache miss guarda resultado
      test_create_item.py    # persiste, invalida cache, publica evento
      test_update_item.py    # actualiza, invalida cache, publica evento
      test_delete_item.py    # elimina, invalida cache, publica evento
      test_create_item_image.py  # nombre duplicado lanza error, imagen se sube
      test_update_item_image.py  # imagen vieja se borra solo tras persistir
  users/
    application/
      test_register_user.py  # email duplicado lanza error, password se hashea
      test_update_user.py    # email ocupado lanza error, password se hashea
      test_delete_user.py    # usuario inexistente lanza error
  auth/
    application/
      test_login.py          # credenciales invalidas, usuario inactivo, exito
      test_token_use_cases.py   # ya existe (issue access, create refresh)
      test_revoke.py         # revoca tokens
```

**Casos criticos a cubrir:**

- Un cache hit no consulta el repositorio.
- Un cache miss consulta el repositorio y guarda el resultado.
- Las mutaciones invalidan el cache.
- Cada mutacion publica un unico evento.
- Si falla la persistencia, no se publica ningun evento.
- Si falla una actualizacion de imagen, se elimina la imagen nueva.
- La imagen antigua se elimina solo despues de actualizar la base de datos.
- Login con credenciales invalidas lanza `CredentialsError`.
- Login con usuario inactivo lanza `UserInactiveError`.
- Registro con email duplicado lanza `UserAlreadyExistsError`.

**Validacion:** misma suite.

---

### PR 9 — Security: `UsersEventRecord` no debe exponer `password_hash`

**Observacion encontrada durante la auditoria:**

`users/infrastructure/events.py` define `UsersEventRecord` con el campo
`password_hash: str` (linea 19). Este record se serializa como payload SSE
en `account_updated` y `account_deleted`. Aunque se filtra con `include={"id"}`
en las llamadas actuales, el modelo tiene la capacidad de exponer el hash.

**Accion:** Eliminar `password_hash` de `UsersEventRecord`. El hash nunca debe
salir del boundary de infrastructure/persistence.

---

## Orden recomendado

```
PR 1  Cerrar eventos items        (pequeno, sin riesgo)
PR 2  CurrentUserDep sin ORM      (desbloquea PR 3-7)
PR 3  Auth service → presentation (mediano)
PR 4  Users service → use cases   (mediano)
PR 5  Eliminar legacy items       (mediano)
PR 6  Eliminar legacy auth        (pequeno)
PR 7  Eliminar legacy users       (pequeno)
PR 8  Tests unitarios             (puede ir en paralelo desde PR 1)
PR 9  Security fix events         (trivial, puede ir en cualquier momento)
```

El PR 2 es el mas importante porque desbloquea el resto: mientras
`CurrentUserDep` devuelva un ORM model, todos los servicios y routers
estaran acoplados a SQLAlchemy.

Los tests (PR 8) pueden avanzar en paralelo con cualquier otro PR.

---

## Definition of Done

La migracion se considera completa cuando:

- [ ] El dominio se prueba sin arrancar FastAPI.
- [ ] Los use cases se prueban con fakes (sin DB, sin HTTP).
- [x] Ningun use case recibe modelos SQLAlchemy.
- [x] `UploadFile` no aparece en application.
- [x] Cloudinary, Redis y SSE solo aparecen en infrastructure.
- [x] Los routers traducen HTTP y no contienen reglas de negocio.
- [x] Los eventos se publican solo despues de persistir correctamente.
- [x] Los schemas HTTP y las entidades de dominio se mapean de forma explicita.
- [x] Los modelos ORM solo se importan desde infrastructure.
- [x] `CurrentUserDep` retorna una entidad de application, no un ORM model.
- [x] Los tests HTTP existentes siguen cubriendo el comportamiento publico.
- [x] `password_hash` no aparece en payloads de eventos SSE.
- [x] `auth/utils.py`, `items/service.py`, `items/cache.py`, `items/repository.py`, `users/service.py`, `users/repository.py` estan eliminados.

## Validacion por cada PR

```bash
uv run ruff check learn_fastapi
uv run ruff format --check learn_fastapi
uv run ty check learn_fastapi
uv run pytest --config-file=pyproject.toml
```
