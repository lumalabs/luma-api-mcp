# Luma MCP

ref claude desktop config json

```
{
    "globalShortcut": "",
    "mcpServers": {
        "Luma Photon MCP": {
            "command": "/Users/karanganesan/.local/bin/uv",
            "args": [
                "run",
                "--with",
                "mcp[cli]",
                "--with",
                "aiohttp",
                "mcp",
                "run",
                "/Users/karanganesan/code/personal/luma-mcp/server.py"
            ],
            "env": {
                "LUMA_API_KEY": "luma-..."
            }
        }
    }
}

```

Replace command, arg python file and luma api key
