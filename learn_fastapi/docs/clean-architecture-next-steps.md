# Clean Architecture: siguiente etapa

Este documento resume el estado actual de la migracion del backend y los pasos
recomendados para continuar. Complementa `docs/clean-architecture-roadmap.md`.

## Estado actual

La migracion ya ha avanzado bastante:

- `items`, `users` y `auth` tienen `domain`, `application`, `infrastructure` y `presentation`.
- Los repositorios SQLAlchemy convierten ORM en entidades de dominio.
- `items` tiene adapters para SQLAlchemy, Redis, Cloudinary y SSE.
- Los casos de uso de `items` ya reciben puertos para repositorio, cache e imagen.
- Los schemas HTTP se han separado de los comandos y queries de application.
- Las dependencias de FastAPI construyen los repositorios, adapters y casos de uso.
- Ruff, `ty` y los tests actuales del backend pasan en el estado validado.

El siguiente objetivo no es crear mas carpetas. Es cerrar las dependencias que
todavia atraviesan las capas y aumentar las pruebas aisladas.

## Fronteras pendientes

### 1. Eventos de `items`

Actualmente `ItemsService` ejecuta el caso de uso y publica el evento despues.
El servicio sigue coordinando una parte del workflow.

El puerto debe recibir la entidad que produce el evento:

```python
class ItemsEventPublisher(Protocol):
    async def item_created(self, item: PublishableItem) -> None: ...
    async def item_updated(self, item: PublishableItem) -> None: ...
    async def item_image_updated(self, item: PublishableItem) -> None: ...
    async def item_deleted(self, item: PublishableItem) -> None: ...
```

Los casos de uso de escritura deben recibir ese puerto y publicar despues de
persistir correctamente. El publisher debe ser stateless: no debe guardar un
`item` en su constructor.

```python
item = await self.items_repository.create_item(...)
await self.cache.invalidate_all()
await self.events.item_created(item)
return item
```

El servicio puede quedarse temporalmente como adapter HTTP, encargado de
convertir schemas, mapear excepciones de dominio a HTTP y devolver respuestas.

### 2. Autorizacion de items

`ItemsService._resolve_owner` mezcla ORM, consultas y reglas de autorizacion.
Conviene reemplazar el modelo ORM por un contexto pequeno de aplicacion:

```python
@dataclass(frozen=True, slots=True)
class CurrentActor:
    id: UserId
    is_superuser: bool
```

Los comandos pueden recibir el actor y el caso de uso puede decidir si puede
operar sobre otro propietario. Application no deberia recibir
`users.models.User`.

### 3. Archivos de imagen

`UploadFile` no debe aparecer en application. El puerto puede definir un
protocolo pequeno para el contenido de la imagen, o presentation puede
convertir `UploadFile` a un DTO de application antes de crear el comando.

La abstraccion de subida no es una entidad de dominio. Por tanto, `ImageUpload`
deberia vivir en `application/ports.py` o en un modulo compartido de puertos,
no en `domain/entities.py`.

### 4. Criptografia de auth y users

Los casos de uso actuales importan directamente `hash_password` y
`verify_password` desde `auth.utils`. Esto acopla application a Argon2 u otra
implementacion concreta.

Crear un puerto:

```python
class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...
    def verify(self, password: str, password_hash: str) -> bool: ...
```

Su implementacion debe vivir en `auth/infrastructure/password_hasher.py` y ser
inyectada desde `auth/presentation/dependencies.py`.

Despues pueden extraerse tambien:

- `TokenIssuer` para JWT.
- `RefreshTokenGenerator`.
- `Clock` para fechas y expiracion.

Cookies, `Request`, `Response`, formularios OAuth y excepciones HTTP deben
permanecer en presentation. El caso de uso de login debe recibir un
`LoginCommand` y devolver un resultado de aplicacion; presentation se ocupa de
crear la respuesta HTTP y las cookies.

## Orden recomendado de trabajo

### PR 1: completar eventos de items

1. Ajustar `ItemsEventPublisher` para recibir el item.
2. Inyectarlo en los casos de uso de escritura.
3. Publicar solo despues de una persistencia exitosa.
4. Dejar `ItemsService` como traductor HTTP.

### PR 2: pruebas de application

Crear pruebas aisladas con fakes:

```text
tests/unit/items/domain/
tests/unit/items/application/
tests/unit/users/application/
tests/unit/auth/application/
```

Casos importantes:

- Un cache hit no consulta SQLAlchemy.
- Un cache miss consulta el repositorio y guarda el resultado.
- Las mutaciones invalidan el cache.
- Cada mutacion publica un unico evento.
- Si falla la persistencia, no se publica ningun evento.
- Si falla una actualizacion de imagen, se elimina la imagen nueva.
- La imagen antigua se elimina solo despues de actualizar la base de datos.

### PR 3: autorizacion de items

Mover la seleccion del propietario y las reglas de superusuario a application.
Presentation solo debe convertir el usuario autenticado en `CurrentActor`.

### PR 4: eliminar el legacy de items

Cuando ningun router dependa de ellos, retirar gradualmente:

```text
items/service.py
items/repository.py
items/cache.py
```

No eliminarlos antes: durante la migracion funcionan como fachadas de
compatibilidad.

### PR 5: puertos de auth

Extraer `PasswordHasher`, `TokenIssuer`, `RefreshTokenGenerator` y `Clock`.
Despues crear pruebas de `LoginUseCase`, refresh, logout y revocacion usando
fakes, sin FastAPI ni una base de datos real.

### PR 6: terminar users

Eliminar las dependencias de ORM y de HTTP de los workflows de cuenta. Los
casos de uso deben trabajar solo con entidades, comandos, queries y puertos.

### PR 7: frontend

Cuando los contratos del backend sean estables, continuar con
`learn_nextjs/src/features/items`:

```text
features/items/
|-- domain/
|-- application/
|-- infrastructure/
`-- presentation/
```

Las Server Actions deben limitarse a leer cookies, parsear `FormData`, llamar a
application, actualizar cache tags y redirigir.

## Regla de dependencias

```text
presentation -> application -> domain
infrastructure -> application -> domain
```

El dominio y application no deben importar FastAPI, SQLAlchemy, Redis,
Cloudinary, modelos ORM ni excepciones HTTP.

## Definition of Done

La migracion sera util cuando se cumpla lo siguiente:

- El dominio se prueba sin arrancar FastAPI.
- Los casos de uso se prueban con fakes.
- Ningun caso de uso recibe modelos SQLAlchemy.
- `UploadFile` no aparece en application.
- Cloudinary, Redis y SSE solo aparecen en infrastructure.
- Los routers traducen HTTP y no contienen reglas de negocio.
- Los eventos se publican solo despues de persistir correctamente.
- Los schemas HTTP y las entidades de dominio se mapean de forma explicita.
- Los tests HTTP existentes siguen cubriendo el comportamiento publico.

## Validacion por cada PR

Desde la raiz del repositorio:

```bash
uv run ruff check learn_fastapi
uv run ruff format --check learn_fastapi
uv run ty check learn_fastapi
uv run pytest --config-file=pyproject.toml
```

Si una migracion cambia el schema de base de datos, ejecutar Alembic desde
`learn_fastapi/`.
