# Shared backend infrastructure

Redis source code lives in `shared/app/redis/`. The installed import name remains
`aliceai_shared` to avoid colliding with each service's own `app` package.

`aliceai-shared` contains reusable Redis connection code. Auth and future chat
services each create their own client/pool; no connection is shared across processes.

Auth installs this local package with `uv sync` in `backend/services/auth`.
To use it from a future `backend/services/chat` project, add `aliceai-shared`
to its dependencies and this source to its `pyproject.toml`:

```toml
[tool.uv.sources]
aliceai-shared = { path = "../../shared", editable = true }
```

Each service reads its own `REDIS_URL` environment setting. For local development:

```ini
REDIS_URL=redis://127.0.0.1:6379/0
```

```python
from aliceai_shared.redis.client import create_redis_client

with create_redis_client(redis_url) as client:
    client.ping()
```

Client construction is lazy; a command such as `ping()` opens the connection.
Auth keeps the client in `request.app.state.redis` and closes it at shutdown.
This is a synchronous client, suitable for auth's synchronous route handlers.
Do not call blocking Redis commands directly from async route handlers.

Keep session behavior in auth and chat behavior in chat. Use distinct key
prefixes such as `auth:session:` and `chat:`. This package does not implement
session persistence or change the login cookie behavior.
