"""Open Masala MCP server — ancestry-adjusted health reference oracle."""

__all__ = ["main"]
__version__ = "0.0.3"


def __getattr__(name):
    # Lazy so `open_masala_mcp.core` (pure, no MCP dep) imports without the SDK.
    if name == "main":
        from .server import main
        return main
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
