"""Smoke tests for CI."""

import importlib
import sys


def test_server_initializes(ariba_env):
    sys.modules.pop("ariba_mcp.server", None)
    server = importlib.import_module("ariba_mcp.server")

    assert server.mcp.name == "ariba-mcp"
