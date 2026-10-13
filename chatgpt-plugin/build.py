#!/usr/bin/env python3
"""Package the plugin, optionally overriding its confirmed HTTPS MCP URL."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZipFile, ZIP_DEFLATED


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mcp-url', help='Confirmed public Open Masala streamable HTTP endpoint')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'plugin.json').read_text())
    mcp = json.loads((root / 'mcp.json').read_text())
    if args.mcp_url:
        url = urlsplit(args.mcp_url)
        if (url.scheme != 'https' or not url.hostname or url.username or url.password
                or url.query or url.fragment or url.hostname in ('localhost', '127.0.0.1', '::1')):
            parser.error('Use a public HTTPS endpoint without credentials, query, or fragment.')
        mcp['mcpServers']['open-masala'] = {
            'type': 'streamable-http', 'url': args.mcp_url,
            'extensions': {'com.openai': {'auth': {'type': 'none'}}},
        }
    mode = 'remote' if 'url' in mcp['mcpServers']['open-masala'] else 'local'
    output = root / 'dist' / f"masalahealth-{manifest['version']}-{mode}.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        archive.writestr('plugin.json', json.dumps(manifest, indent=2) + '\n')
        archive.writestr('mcp.json', json.dumps(mcp, indent=2) + '\n')
        for path in sorted((root / 'skills').rglob('SKILL.md')):
            archive.write(path, path.relative_to(root))
        archive.writestr('assets/icon.png', (root / 'assets/icon.png').read_bytes())
    print(output)
    print('Built package only; no installation, connection, or publication performed.')


if __name__ == '__main__':
    main()
