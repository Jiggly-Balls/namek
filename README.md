# Namek Bot

An open-source music bot for Discord with Lavalink.

## Table of Contents
- [Setting up Lavalink](#setting-up-lavalink-server)
- [Building the Bot](#building-the-bot)
  - [Building with Python & uv](#building-with-python-and-uv)
  - [Building with Docker](#building-with-docker)

## Setting up Lavalink Server

This bot relies on the Lavalink server to stream music to Discord.
You can set up the Lavalink server from [this](https://github.com/lavalink-devs/Lavalink) repository.
You are required to set up an `application.yml` file at the root of the project.
The easiest way to set up and configure it is via [Docker](https://docs.docker.com/engine/install/).
You can find the sample `application.yml` file [here](https://lavalink.dev/configuration/config/file.html) to configure it.

## Configuring the Environment File

Create an `.env` file and copy and paste the contents of `.env.example` file into it.

Obtain your Discord bot token from the [developer portal](https://discord.com/developers/home) and paste it into the `BOT_TOKEN` attribute.

You can copy the discord ID of the members you want to give owner access to. 


## Building the Bot

To run the bot, you can either run it via your Python system and [uv](https://docs.astral.sh/uv/) or via [Docker](https://docs.docker.com/engine/install/).

### Building with Python and uv

You will first have to set up uv in your local dev environment.
You can check the installation instructions [here](https://docs.astral.sh/uv/getting-started/installation/).

Then, set up your environment:
```
uv sync
```

Finally, run the bot:
```
uv run python -m namek
```

Or, if you have `make` in your system:
```
make dev
```

### Building with Docker

You can find the installation instructions for Docker [here](https://docs.docker.com/engine/install/).

To start the Docker Container:
```
docker compose up -d
```

Or, via `make`:
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
│   ├───commands    - User-facing commands.
│   ├───workers     - Background-running tasks and event catching.
├───core            - Contains views, constants and "core" functionalities.
│   └───views       - All view subclasses that get used in commands.
└────utils          - Helper functions / classes.
```

### License

This project is licensed under MIT; check the LICENSE file for more details.

All the emoji images & font assets are licensed under Apache 2.0 (no attribution required; commercial use is allowed).

### Credits

- [Maha](https://github.com/CodesMaha) for proofreading.
