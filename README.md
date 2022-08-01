# Banter Bus Core API

A Websockets (Socketio) API for the Banter Bus application.

## Running using devcontainer

The easiest way to setup this project is to use vscode's development containers.
For this you will need:

- vscode
- [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

First make a copy of the example files:

```bash
cp .env.sample .env
cp .devcontainer/devcontainer.example.json .devcontainer/devcontainer.json
```

> The reason for this is so we can customise our development environment. For example I like to use fish shell instead of bash.

### Example `devcontainer.json`

```json
{
  "name": "Banter Bus Core API Devcontainer",
  "dockerComposeFile": ["../docker-compose.yml"],
  "shutdownAction": "stopCompose",
  "service": "app",
  "workspaceFolder": "/app",
  "settings": {
    "python.pythonPath": "/usr/local/bin/python",
    "terminal.integrated.defaultProfile.linux": "fish",
    "terminal.integrated.profiles.linux": {
      "fish": {
        "path": "/usr/bin/fish"
      }
    }
  },
  "extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-vsliveshare.vsliveshare"
  ],
  "remoteUser": "app"
}
```
