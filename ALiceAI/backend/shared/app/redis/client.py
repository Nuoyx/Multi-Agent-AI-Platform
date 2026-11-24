"""Redis connection creation; callers own the client and its lifecycle."""

from redis import Redis


def create_redis_client(url: str) -> Redis:
    """Create a synchronous client with its own pool and decoded string values."""
    return Redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
