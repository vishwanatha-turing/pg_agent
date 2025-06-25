from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("pg_agent")
except PackageNotFoundError:
    __version__ = "0.0.0"

# Re-export main build graph for convenience
from .pipeline.pipeline_graph import (
    build_pipeline_graph,
    test_pipeline,
)  # noqa: E402,F401

__all__ = [
    "build_pipeline_graph",
    "test_pipeline",
    "__version__",
]
