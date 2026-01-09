import logging
import os
import discord
from discord import app_commands
from discord.ext import commands
from config import BOT_TOKEN, SYNC_GUILD

# Set intents
intents = discord.Intents.default()

# Set up logging
logs_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(logs_dir, exist_ok=True)
timestamp = discord.utils.utcnow().strftime("%Y-%m-%d_%H-%M-%S") # UTC timestamp
log_filename = os.path.join(logs_dir, f"log_{timestamp}.log")

logger = logging.getLogger("discord.app")
logger.setLevel(logging.INFO)
log_handler = logging.FileHandler(filename=log_filename, encoding="utf-8", mode="w")
# Using Python's standard formatting style
LOG_FORMAT = "[{asctime}] [{levelname:<8}] {name}: {message}"
log_formatter = logging.Formatter(LOG_FORMAT, "%Y-%m-%d %H:%M:%S", style="{")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        # No prefix since we use app commands
        super().__init__(command_prefix="", intents=intents)
        self.logger = logger

    # Load cogs
    async def load_cogs(self) -> None:
        for file in os.listdir(os.path.join(os.path.realpath(os.path.dirname(__file__)), "cogs")):
            if file.endswith(".py"): # Only load python files
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info("Loaded extension '%s'", extension)
                except Exception as error:
                    self.logger.error(
                        "Failed to load extension '%s': %s", extension, type(error).__name__
                    )
                    self.logger.exception(error)

    async def setup_hook(self) -> None:
        self.logger.info(
            "Logged in as %s#%s (ID: %s)", self.user.name, self.user.discriminator, self.user.id
        )
        self.logger.info("discord.py version: %s", discord.__version__)
        self.logger.info("-------------------")
        await self.load_cogs()

        # Sync global commands
        try:
            synced_global = await self.tree.sync()
            self.logger.info("Synced %d global interactions", len(synced_global))
        except Exception as error:
            self.logger.error("Failed to sync global interaction: %s", type(error).__name__)
            self.logger.exception(error)

        # Sync specific guild commands
        guild = discord.Object(id=SYNC_GUILD)
        try:
            synced_guild = await self.tree.sync(guild=guild)
            self.logger.info("Synced %d guild interactions to Guild ID %s", len(synced_guild), guild.id)
        except Exception as error:
            self.logger.error("Failed to sync guild interaction: %s", type(error).__name__)
            self.logger.exception(error)

    # Log app command execution
    async def on_app_command_completion(
            self, interaction: discord.Interaction, command: app_commands.Command
    ) -> None:
        if interaction.guild is not None:
            self.logger.info(
                "User %s (User ID: %s) executed the '%s' interaction in guild '%s' (Guild ID: %s)",
                interaction.user, interaction.user.id, command.qualified_name,
                interaction.guild.name, interaction.guild.id
            )
        else:
            self.logger.info(
                "User %s (User ID: %s) executed the '%s' interaction in DMs",
                interaction.user, interaction.user.id, command.qualified_name
            )


# Run the bot
bot = DiscordBot()
bot.run(BOT_TOKEN)