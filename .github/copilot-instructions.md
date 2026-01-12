# Copilot Instructions for Pyxis

## Project Overview
Pyxis is a Discord bot designed to invite users to other servers and to manage servers. It's built using discord.py (>= 2.6.4) with a cog-based architecture.

## Architecture & Structure

### Project Layout
- `main.py` - Entry point for the bot, contains the `DiscordBot` class
- `config.py` - Configuration module for environment variables (BOT_TOKEN, SYNC_GUILD)
- `cogs/` - Directory containing bot command modules (cogs)
  - Each cog is a separate Python file implementing specific functionality
  - Use discord.py's `commands.Cog` class pattern

### Bot Implementation
- The bot uses discord.py's Application Commands (slash commands)
- No traditional command prefix is used (set to empty string)
- Commands are synchronized both globally and to a specific guild (SYNC_GUILD)
- Default intents are used, but others can be added if required

## Coding Conventions

### Python Style
- Use type hints for function parameters and return values (e.g., `-> None`, `interaction: discord.Interaction`)
- Follow PEP 8 style guidelines
- Use async/await for all Discord operations
- Keep code clean and readable with appropriate comments
- Make simple, minimal docstrings
- Adhere to Pylint rules:
  - C0301: Line too long (line-too-long)
  - C0304: Final newline missing (missing-final-newline)

### Discord.py Patterns
- Use `app_commands.command()` decorator for slash commands
- Use `@app_commands.guilds(guild)` to restrict commands to specific guilds
- use `@app_commands.guild_only()` to restrict commands to be used in guilds only
- Always handle exceptions when loading extensions and syncing commands
- Use `ephemeral=True` for command responses that should be private
- Cogs must have an async `setup()` function to register with the bot

### Error Handling
- Wrap extension loading in try-except blocks
- Log informative error messages for debugging
- Handle command sync failures gracefully

## Configuration
- Use environment variables for sensitive data (BOT_TOKEN, SYNC_GUILD)
- Import configuration from `config.py`
- Never hardcode tokens or sensitive information

## Development Practices

### Adding New Features
1. Create new cogs in the `cogs/` directory for new functionality
2. Follow the existing cog pattern (see `cogs/invite.py`)
3. Each cog should be in its own file ending with `.py`
4. Implement the async `setup()` function for cog registration

### Dependencies
- Keep `requirements.txt` up to date
- Pin major versions but allow minor updates (e.g., `>=2.6.4`)
- Current dependencies:
  - discord.py >= 2.6.4
  - python-dotenv >= 1.2.1

### Testing
- Test commands in a Discord server before deployment
- Verify both global and guild-specific command syncing
- Check that cogs load properly on startup

## Common Tasks

### Creating a New Command
```python
@app_commands.command(name="command_name", description="Command description")
async def command_name(self, interaction: discord.Interaction):
    await interaction.response.send_message("Response", ephemeral=True)
```

### Creating a New Cog
```python
import discord
from discord.ext import commands
from discord import app_commands

class NewCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Add commands here

async def setup(bot):
    await bot.add_cog(NewCog(bot))
```

## Important Notes
- The bot automatically loads all `.py` files from the `cogs/` directory
- Commands are synced on bot startup via `setup_hook()`
- Guild-specific commands appear only in the configured guild
- Global commands may take time to propagate across Discord
