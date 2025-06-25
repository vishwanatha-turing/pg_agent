import os

__all__ = ["require_env"]


def require_env(key: str) -> str:
    """Return the value of environment variable *key* or raise a clear error."""
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Environment variable {key} is not set.")
    return value
