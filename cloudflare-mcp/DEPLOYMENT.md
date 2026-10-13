# Private prototype deployment

Deployed 2026-10-13 to Cloudflare Workers Free.

- MCP endpoint: https://masalahealth-mcp.neilshahis.workers.dev/mcp
- Health endpoint: https://masalahealth-mcp.neilshahis.workers.dev/health
- Worker version: `f67992c0-b4cc-4a4a-887d-9d58e3cd2783`
- Runtime source: review branch `codex/cloudflare-mcp`; default branch remains unchanged.
- Deployment: Wrangler with Account Read, User Read, Workers Scripts Write, and Background Access. Credentials are encrypted using a key in the OS keychain; no credentials are committed.
- No paid upgrade, database bindings, custom domain, or automatic Git deployment was created. GitHub integration was installed for `open-masala` only, but Workers Builds was not configured because its automatic token requests broader permissions than this prototype needs.

Verification: all 394 Python reference comparison cases passed, protocol/input/CORS/body-size checks passed, and GitHub CI passed. The live SDK client successfully initialized, discovered all six read-only tools, read the guidance resource, and exercised every tool with synthetic inputs, including missing sex, unit mismatch, and deprecated eGFR handling. This is endpoint verification, not a load test or a claim of clinical validation.

Repeat live checks from this folder with:

```sh
node test/verify-remote.js https://masalahealth-mcp.neilshahis.workers.dev/mcp
```

The `chatgpt-plugin` folder contains the hosted plugin package and workflow skills. Build its remote ZIP with `python3 chatgpt-plugin/build.py` from the repository root. The archive was successfully uploaded as a personal ChatGPT cloud plugin, and its page displays one MCP server and two skills. Final desktop enablement and conversation testing remain unverified: the computer-use tool blocks controls for the ChatGPT desktop app. Public directory publication is separate.
