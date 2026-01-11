"""Main entry point for the Discord bot."""
import logging
import os
import discord
from discord import app_commands
from discord.ext import commands
from config import BOT_TOKEN, SYNC_GUILD

# Set intents
intents = discord.Intents.default()
intents.members = True # Required to access guild.members
intents.presences = True # Required to access member status

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
    """Discord bot class with cog loading and error handling."""
    def __init__(self) -> None:
        """Initialize the Discord bot with intents and logging."""
        # No prefix since we use app commands
        super().__init__(command_prefix="", intents=intents)
        self.logger = logger
        self.tree.on_error = self.on_app_command_error

    # Load cogs
    async def load_cogs(self) -> None:
        """Load all cogs from the cogs directory."""
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
        """Perform initial setup, including loading cogs and syncing commands."""
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

        # Sync specific guild commands if SYNC_GUILD is configured
        if SYNC_GUILD:
            guild = discord.Object(id=SYNC_GUILD)
            try:
                synced_guild = await self.tree.sync(guild=guild)
                self.logger.info("Synced %d guild interactions to Guild ID %s", len(synced_guild), guild.id)
            except Exception as error:
                self.logger.error("Failed to sync guild interaction: %s", type(error).__name__)
                self.logger.exception(error)
        else:
            self.logger.warning("SYNC_GUILD not configured; guild-specific commands will not be synced.")

    # Log app command execution
    async def on_app_command_completion(
            self, interaction: discord.Interaction, command: app_commands.Command
    ) -> None:
        """Log when an app command is successfully executed."""
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

    # Log app command errors
    async def on_app_command_error(
            self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Handle and log app command errors."""
        command_name = interaction.command.name if interaction.command else "Unknown command"

        # Check if interaction was already responded to
        if interaction.response.is_done():
            send_msg = interaction.followup.send
        else:
            send_msg = interaction.response.send_message

        # Command not found
        if isinstance(error, app_commands.CommandNotFound):
            await send_msg(
                "This command does not exist or is not configured properly.",
                ephemeral=True
            )
            return
        # Command raised an unexpected error
        if isinstance(error, app_commands.CommandInvokeError):
            original = getattr(error, "original", error)
            # Bot doesn't have permission
            if isinstance(original, discord.Forbidden):
                await send_msg(
                    "I don't have permission to execute this command.",
                    ephemeral=True
                )
                return
            # Network issues or rate limiting
            elif isinstance(original, discord.HTTPException):
                self.logger.warning(
                    "HTTP exception occurred in interaction '%s' for user %s (User ID: %s): %s",
                    command_name, interaction.user.name, interaction.user.id, original
                )
                await send_msg(
                    "I cannot complete this command because of network issues. "
                    "I might have been rate limited. Please try again later.",
                    ephemeral=True
                )
                return
            # Handle all other CommandInvokeError cases
            else:
                self.logger.error(
                    "CommandInvokeError occurred in interaction '%s' by user %s (User ID: %s): %r",
                    command_name, interaction.user.name, interaction.user.id,
                    original, exc_info=(type(original), original, original.__traceback__)
                )
                await send_msg(
                    "An error occurred while executing the command.",
                    ephemeral=True
                )
            return
        # Other errors
        else:
            self.logger.error(
                "Unhandled app command error in interaction '%s' by user %s (User ID: %s): %r",
                command_name, interaction.user.name, interaction.user.id,
                error, exc_info=(type(error), error, error.__traceback__)
            )
            await send_msg(
                "An unexpected error occurred while executing the command.",
                ephemeral=True
            )


# Run the bot
bot = DiscordBot()

if not BOT_TOKEN:
    raise ValueError("Discord bot token was not found in environment variables!")
bot.run(BOT_TOKEN)
