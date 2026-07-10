# Publishing the MCP server

The server is distributed as a **PyPI package** (`open-masala-mcp`) so clients run it with `uvx open-masala-mcp` — no clone, no hosting. Then it's listed on the MCP registries.

## 1. Publish to PyPI

The dataset is bundled into the wheel (see `pyproject.toml` `force-include`), so the installed server is self-contained. From this directory:

```bash
cd mcp-server
uv build                      # builds sdist + wheel into dist/
uv publish                    # needs a PyPI API token (UV_PUBLISH_TOKEN or prompt)
```

Verify: `uvx open-masala-mcp` should start the server (Ctrl-C to stop).

Keep the version in `pyproject.toml`, `open_masala_mcp/__init__.py`, and `../server.json` in lockstep with the dataset version.

## 2. List on the official MCP Registry

Uses [`../server.json`](../server.json). The `io.github.masalahealth/*` namespace is proven via GitHub auth.

```bash
# install the publisher CLI (see modelcontextprotocol/registry docs)
mcp-publisher login github        # OIDC / device flow for the io.github.masalahealth namespace
mcp-publisher publish             # reads server.json
```

## 3. Community directories

- **`punkpeye/awesome-mcp-servers`** — open a PR adding one line under the health/other section:
  > `[Open Masala](https://github.com/masalahealth/open-masala) 🐍 🏠 — Ancestry-adjusted health reference ranges (South Asian biomarker cutoffs, cited) as MCP tools.`
  (`🐍` = Python, `🏠` = local/stdio.)
- **Glama** (`glama.ai/mcp/servers`), **PulseMCP**, **mcp.so** — these auto-index public GitHub repos with MCP topics; add the topic `mcp` (and `mcp-server`) to the repo so they discover it.

## 4. Smithery

Smithery's "add server URL" form is for **remote/hosted** servers, which this isn't. Either skip it (the registries above cover local servers) or, if one-click install matters, host the server over HTTP (a free Docker host works since it does no inference) and submit that URL.
