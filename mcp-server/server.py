#!/usr/bin/env python3
"""Convenience entry point so `python3 mcp-server/server.py` works from a source
checkout. The real implementation is the installable package in
`open_masala_mcp/`. For a no-clone install, prefer:  uvx open-masala-mcp
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from open_masala_mcp.server import main  # noqa: E402

if __name__ == "__main__":
    main()
