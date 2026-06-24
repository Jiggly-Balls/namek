# Namek Bot

An open source music bot for Discord with Lavalink.

## Table of Contents
- [Setting up Lavalink](#setting-up-lavalink-server)
- [Building the Bot](#building-the-bot)
  - [Building with python & uv](#building-with-python-&-uv)
  - [Building with Docker](#building-with-docker)

## Setting up Lavalink Server

This bot relies on lavalink server to stream music to discord.
You can set up the lavalink server from this [repository](https://github.com/lavalink-devs/Lavalink).
You are required to set up an `application.yml` file at the root of the project.
The easiest way to set up and configure it is via [Docker](https://docs.docker.com/engine/install/).
You can find the sample `application.yml` file [here](https://lavalink.dev/configuration/config/file.html) to configure it.

## Building the Bot

To run the bot you can either run it via your python system and [uv](https://docs.astral.sh/uv/) or you can run it via docker.

### Building with python & uv

You will first have to set up `uv` in your local dev environment.
You can check the installation instruction [here](https://docs.astral.sh/uv/getting-started/installation/).

Then set up your environment:
```
uv sync
```

Finally run the bot:
```
uv run python -m namek
```

Or if you have `make` in your system:
```
make dev
```

### Building with Docker

You can find the installation instructions for docker [here](https://docs.docker.com/engine/install/).

To start the docker container:
```
docker compose up -d
```

Or via `make`-
```
make docker
```

## Code Structure

```
namek
├───assets          - Holds all graphical / font assets for emojis & image generation.
│   ├───fonts
│   └───graphics
│       ├───emojis
│       └───other
├───cogs            - All extension files that get loaded at runtime.
│   ├───commands    - User facing commands.
│   ├───workers     - Background running tasks and event catching.
├───core            - Contains views, constants and "core" functionalities.
│   └───views       - All view subclasses that get used in commands
└────utils          - Helper functions / classes.
```
