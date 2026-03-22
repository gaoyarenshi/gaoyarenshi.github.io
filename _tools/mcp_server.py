#!/usr/bin/env python3
"""
Minimal MCP server (stdio) that exposes a build_blog tool.
No external dependencies required.
"""

import json
import os
import subprocess
import sys


def send(msg: dict):
    sys.stdout.write(json.dumps(msg) + '\n')
    sys.stdout.flush()


TOOLS = [
    {
        'name': 'build_blog',
        'description': 'Build static HTML files from _blog/*.md into blog/ and update root index.html with a blog listing',
        'inputSchema': {'type': 'object', 'properties': {}},
    }
]

BUILD_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build.py')


def handle(req: dict):
    method = req.get('method')
    req_id = req.get('id')

    if method == 'initialize':
        send({
            'jsonrpc': '2.0', 'id': req_id,
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': {'tools': {}},
                'serverInfo': {'name': 'blog-builder', 'version': '1.0.0'},
            },
        })

    elif method == 'notifications/initialized':
        pass  # notification — no response

    elif method == 'tools/list':
        send({'jsonrpc': '2.0', 'id': req_id, 'result': {'tools': TOOLS}})

    elif method == 'tools/call':
        name = req.get('params', {}).get('name')
        if name == 'build_blog':
            proc = subprocess.run(
                [sys.executable, BUILD_SCRIPT],
                capture_output=True, text=True,
            )
            output = (proc.stdout + proc.stderr).strip() or 'Done.'
            send({
                'jsonrpc': '2.0', 'id': req_id,
                'result': {
                    'content': [{'type': 'text', 'text': output}],
                    'isError': proc.returncode != 0,
                },
            })
        else:
            send({
                'jsonrpc': '2.0', 'id': req_id,
                'error': {'code': -32601, 'message': f'Unknown tool: {name}'},
            })

    elif req_id is not None:
        send({
            'jsonrpc': '2.0', 'id': req_id,
            'error': {'code': -32601, 'message': f'Method not found: {method}'},
        })


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            handle(json.loads(line))
        except Exception as e:
            sys.stderr.write(f'Error: {e}\n')


if __name__ == '__main__':
    main()
