# snek it up

**[Python-Discord code jam 1](https://github.com/discord-python/code-jam-1) entry by Momo and kel/qrie** (Team 23)


## what is it

A Discord bot that:

- Finds snek species on the [ITIS database](https://itis.gov/) 🐍
- Hosts Snakes and Ladders games in concurrent channels 🎲
- Imitates your chat history, but with 105% more snekin 💬
- Lets you hatch snek eggs for your very own snek collection ≧◡≦
- Draws random sneks using Perlin noise 🖌️
- Plays snek rattles in your voice channel, on demand 🔊

## how u do that

- Snek lookup: `bot.snakes.get('snek name here')`
- Snakes and Ladders:
  - Create a game using `bot.sal create` (the author can cancel the game using `bot.sal cancel`)
  - Others join the game using `bot.sal join` (players can leave using `bot.sal leave`)
  - The author starts the match using `bot.sal start`
  - When a round begins, players use `bot.roll` to roll the dice
  - glhf

- Snake imitation: `bot.snakes.snakeme`
- Egg hatching: `bot.snakes.hatch`
- Snek drawing: `bot.snakes.draw`
- Rattle-up your voice channel: `bot.snakes.rattle`

## environment variables

You will need these environment variables to setup mr bot:

- `BOT_TOKEN`: The Discord API token for the bot.
- `FFMPEG`: A direct path to a `ffmpeg` executable. If not provided, it will assume the `ffmpeg` command is in your path.
- `LIBOPUS` The name of the `libopus` library file, located in the project folder. If not provided, defaults to `libopus`.
  - ffmpeg and libopus are only used for snek rattling (voice comms)

## note about libopus

The `libopus.dll` is compiled for 64-bit Windows only. If you're using a different OS/architecture, you will need to find/compile the library for your system. If the name of the file changes, you will need to provide the `LIBOPUS` env variable, as described above.
